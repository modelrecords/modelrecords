package main

import (
	"bytes"
	"context"
	"fmt"
	"io"
	"net/http"
	"os"
	"regexp"
	"strings"

	"github.com/ledongthuc/pdf"
	"github.com/pdfcpu/pdfcpu/pkg/api"
	"github.com/sashabaranov/go-openai"
	"gopkg.in/yaml.v2"
)

type DataSource struct {
	Name   string `yaml:"name"`
	Type   string `yaml:"type"`
	Source string `yaml:"source"`
}

type Config struct {
	DataSources []DataSource `yaml:"data_sources"`
}

func main() {
	// Read the configuration file
	configData, err := os.ReadFile("./cmd/pipeline/config.yaml")
	if err != nil {
		fmt.Printf("Error reading config file: %v\n", err)
		return
	}

	var config Config
	err = yaml.Unmarshal(configData, &config)
	if err != nil {
		fmt.Printf("Error parsing config file: %v\n", err)
		return
	}

	re := regexp.MustCompile(`(?s)^\x60{3}(?:yaml|YAML)?\n(.*)\n\x60{3}$`)

	// Fetch data from each source
	for _, dataSource := range config.DataSources {
		data, err := fetchData(dataSource)
		if err != nil {
			fmt.Printf("Error fetching data for model %s: %v\n", dataSource.Name, err)
			continue
		}

		// Feed the scraped data into the question answering module
		answer, err := answerQuestion(data)
		if err != nil {
			fmt.Printf("Error answering question: %v\n", err)
			return
		}

		match := re.FindStringSubmatch(answer)
		if len(match) == 2 {
			answer = match[1]
		}

		modelName := strings.ToLower(dataSource.Name)

		rawOutFile := fmt.Sprintf("./cmd/pipeline/out/raw/%s.txt", modelName)
		err = os.WriteFile(rawOutFile, []byte(answer), os.ModePerm)
		if err != nil {
			fmt.Printf("Error writing raw output file: %v\n", err)
			return
		}

		// Parse the answer string into a map.
		var answerMap map[string]any
		err = yaml.Unmarshal([]byte(answer), &answerMap)
		if err != nil {
			fmt.Printf("Error parsing answer string: %v\n", err)
			return
		}

		// Generate the YAML file.
		yamlData, err := yaml.Marshal(answerMap)
		if err != nil {
			fmt.Printf("Error generating YAML: %v\n", err)
			return
		}

		yamlFile := fmt.Sprintf("./cmd/pipeline/out/yaml/%s.yaml", modelName)
		err = os.WriteFile(yamlFile, yamlData, os.ModePerm)
		if err != nil {
			fmt.Printf("Error writing YAML file: %v\n", err)
			return
		}

		fmt.Println("YAML file generated successfully for ", dataSource.Name)
	}

	fmt.Println("All data sources processed successfully.")
}

func fetchData(dataSource DataSource) (string, error) {
	var data string

	switch dataSource.Type {
	case "website":
		resp, err := http.Get(dataSource.Source)
		if err != nil {
			return "", fmt.Errorf("error fetching data from %s: %v", dataSource.Source, err)
		}
		defer resp.Body.Close()

		body, err := io.ReadAll(resp.Body)
		if err != nil {
			return "", fmt.Errorf("error reading response body from %s: %v", dataSource.Source, err)
		}

		data = string(body)

	case "file":
		content, err := os.ReadFile(dataSource.Source)
		if err != nil {
			return "", fmt.Errorf("error reading file %s: %v", dataSource.Source, err)
		}

		data = string(content)

	case "pdf":
		resp, err := http.Get(dataSource.Source)
		if err != nil {
			return "", fmt.Errorf("error fetching PDF from %s: %v", dataSource.Source, err)
		}
		defer resp.Body.Close()

		// Check the response status code
		if resp.StatusCode != http.StatusOK {
			return "", fmt.Errorf("unexpected status code: %d", resp.StatusCode)
		}

		// Create a bytes.Buffer to store the PDF content
		var pdfBuffer bytes.Buffer

		// Copy the response body to the buffer
		_, err = io.Copy(&pdfBuffer, resp.Body)
		if err != nil {
			return "", fmt.Errorf("error copying PDF content: %v", err)
		}

		// Create a new PDF reader from the buffer
		pdfReader, err := pdf.NewReader(bytes.NewReader(pdfBuffer.Bytes()), int64(pdfBuffer.Len()))
		if err != nil {
			return "", fmt.Errorf("error creating PDF reader: %v", err)
		}

		var builder strings.Builder
		for pageIndex := 1; pageIndex <= pdfReader.NumPage(); pageIndex++ {
			page := pdfReader.Page(pageIndex)
			if page.V.IsNull() {
				continue
			}

			textContent, err := page.GetPlainText(nil)
			if err != nil {
				return "", fmt.Errorf("error extracting text from page %d: %v", pageIndex, err)
			}

			builder.WriteString(textContent)
		}

		return builder.String(), nil

	default:
		return "", fmt.Errorf("unsupported data source type: %s", dataSource.Type)
	}

	return data, nil
}

// downloadPDF downloads a PDF from a URL and saves it to a specified local path.
func downloadPDF(url, outputPath string) error {
	resp, err := http.Get(url)
	if err != nil {
		return fmt.Errorf("error fetching PDF from %s: %v", url, err)
	}
	defer resp.Body.Close()

	// Create the output file
	outFile, err := os.Create(outputPath)
	if err != nil {
		return fmt.Errorf("error creating file %s: %v", outputPath, err)
	}
	defer outFile.Close()

	// Copy the response body to the file
	_, err = io.Copy(outFile, resp.Body)
	if err != nil {
		return fmt.Errorf("error writing PDF content to file: %v", err)
	}

	return nil
}

// extractTextFromPDF uses pdfcpu to extract text from a PDF file.
func extractTextFromPDF(pdfPath, textOutputPath string) error {
	err := api.ExtractContentFile(pdfPath, textOutputPath, nil, nil)
	if err != nil {
		return fmt.Errorf("error extracting text from PDF: %v", err)
	}

	return nil
}

func answerQuestion(data string) (string, error) {
	client := openai.NewClient(os.Getenv("OPENAI_API"))

	question := `Here is a YAML format. Please answer the following model-card related questions and provide the answers in valid YAML format:

Please provide the following information about the model in the specified format:
Model Details:
- Name: [Model Name]
- Version: [Model Version]
- Release Date: [Release Date]
- Developed By: [Developer]
- Model Type: [Model Type]

Intended Use:
- [Intended Use 1]
- [Intended Use 2]
...

Factors:
- [Factor 1]
- [Factor 2]
...

Metrics:
- [Metric 1]
- [Metric 2]
...

Evaluation Data:
- Description: [Evaluation Data Description]

Training Data:
- Description: [Training Data Description]

Ethical Considerations:
- [Ethical Consideration 1]
- [Ethical Consideration 2]
...

Caveats and Recommendations:
- [Caveat/Recommendation 1]
- [Caveat/Recommendation 2]
...

Additional Information:
- [Additional Information 1]
- [Additional Information 2]
`

	resp, err := client.CreateChatCompletion(
		context.Background(),
		openai.ChatCompletionRequest{
			Model: openai.GPT4TurboPreview,
			Messages: []openai.ChatCompletionMessage{
				{
					Role:    openai.ChatMessageRoleUser,
					Content: fmt.Sprintf("Please answer the following question given this text: \n\n<CONTENT>%s</CONTENT>\n\n Question: %s", data, question),
				},
			},
		},
	)
	if err != nil {
		return "", fmt.Errorf("error creating chat completion: %v", err)
	}

	return resp.Choices[0].Message.Content, nil
}
