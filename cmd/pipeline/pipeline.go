package main

import (
	"context"
	"fmt"
	"io"
	"net/http"
	"os"

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

type Answer struct {
	ModelDetails           string `yaml:"model_details"`
	IntendedUse            string `yaml:"intended_use"`
	Factors                string `yaml:"factors"`
	Metrics                string `yaml:"metrics"`
	EvaluationData         string `yaml:"evaluation_data"`
	TrainingData           string `yaml:"training_data"`
	EthicalConsiderations  string `yaml:"ethical_considerations"`
	CaveatsRecommendations string `yaml:"caveats_recommendations"`
	QuantitativeAnalysis   string `yaml:"quantitative_analysis"`
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

	var scrapedData string
	// Fetch data from each source
	for _, dataSource := range config.DataSources {
		data, err := fetchData(dataSource)
		if err != nil {
			fmt.Printf("Error fetching data for model %s: %v\n", dataSource.Name, err)
			continue
		}

		scrapedData += data
	}

	// Feed the scraped data into the question answering module
	answer := answerQuestion(scrapedData)
	fmt.Println("Answer:", answer)

	// Generate the YAML file
	// yamlData, err := yaml.Marshal(answer)
	// if err != nil {
	// 	fmt.Printf("Error generating YAML: %v\n", err)
	// 	return
	// }
	//
	// // Write the YAML data to a file
	// err = os.WriteFile("answer.yaml", yamlData, 0644)
	// if err != nil {
	// 	fmt.Printf("Error writing YAML file: %v\n", err)
	// 	return
	// }
	//
	// fmt.Println("YAML file generated successfully.")
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
		// Download the PDF file.
		pdfPath := "./cmd/pipeline/temp.pdf"
		if err := downloadPDF(dataSource.Source, pdfPath); err != nil {
			return "", fmt.Errorf("error downloading PDF from %s: %v", dataSource.Source, err)
		}

		// Extract text from the PDF file.
		textOutputPath := "./cmd/pipeline/temp"
		if err := extractTextFromPDF(pdfPath, textOutputPath); err != nil {
			return "", fmt.Errorf("error extracting text from PDF: %v", err)
		}

		dirs, err := os.ReadDir(textOutputPath)
		if err != nil {
			return "", fmt.Errorf("error reading text file: %v", err)
		}

		var data string
		for _, dir := range dirs {
			if dir.IsDir() {
				continue
			}

			file, err := os.ReadFile(textOutputPath + "/" + dir.Name())
			if err != nil {
				return "", fmt.Errorf("error reading text file: %v", err)
			}

			data += string(file)
		}

		return data, nil

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

func answerQuestion(data string) Answer {
	// Set up the OpenAI client
	client := openai.NewClient(os.Getenv("OPENAI_API"))

	// Define the question
	question := `Here is a YAML format. Please answer the following model-card related questions:

<YAML>
model_details:
intended_use:
factors:
metrics:
evaluation_data:
training_data:
ethical_considerations:
caveats_recommentations:
quantitative_analysis:
</YAML>
`

	// Create the chat completion request
	resp, err := client.CreateChatCompletion(
		context.Background(),
		openai.ChatCompletionRequest{
			Model: openai.GPT4TurboPreview,
			Messages: []openai.ChatCompletionMessage{
				{
					Role:    openai.ChatMessageRoleUser,
					Content: fmt.Sprintf("Please answer the following question given this text: <CONTENT>%s</CONTENT> %s", data, question),
				},
			},
		},
	)
	if err != nil {
		fmt.Printf("Error calling OpenAI API: %v\n", err)
		return Answer{}
	}

	// Extract the answer from the API response
	answer := resp.Choices[0].Message.Content

	fmt.Println("Answer:", answer)

	// Parse the answer into the Answer struct
	var parsedAnswer Answer
	// err = yaml.Unmarshal([]byte(answer), &parsedAnswer)
	// if err != nil {
	// 	fmt.Printf("Error parsing answer: %v\n", err)
	// 	return Answer{}
	// }

	return parsedAnswer
}