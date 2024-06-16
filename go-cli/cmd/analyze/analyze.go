package main

import (
	"bufio"
	"context"
	"flag"
	"fmt"
	"io"
	"log"
	"os"
	"regexp"
	"runtime"
	"strings"
	"sync"

	"github.com/james-bowman/nlp"
	"github.com/jdkato/prose/v2"
	"github.com/ledongthuc/pdf"
	"github.com/pkoukk/tiktoken-go"
	"github.com/sashabaranov/go-openai"
	"golang.org/x/sync/errgroup"
	"gonum.org/v1/gonum/floats"
	"gonum.org/v1/gonum/mat"
	"gopkg.in/yaml.v3"
)

func main() {
	filePath := flag.String("input", "", "Path to the input PDF file")
	modelName := flag.String("model", "gpt-4o", "The model to use for reviewing.")
	threshold := flag.Float64("threshold", 0.8, "Similarity threshold for filtering responses")
	flag.Parse()

	if *filePath == "" {
		log.Fatalf("Input file path is required. Use -input flag to specify the PDF file.")
	}

	text, err := readPDF(*filePath)
	if err != nil {
		log.Fatalf("Failed to read PDF: %v", err)
	}

	cleanedText := preprocessText(text)
	fmt.Printf("Cleaned Text; Size: %d\n", len(cleanedText))

	chunks, err := ChunkReader(strings.NewReader(cleanedText))
	if err != nil {
		log.Fatalf("Failed to chunk text: %v", err)
	}

	fmt.Println("Number of Chunks:", len(chunks))

	client := openai.NewClient(os.Getenv("OPENAI_API_KEY"))

	var mu sync.Mutex
	var responses []string
	var g errgroup.Group
	g.SetLimit(runtime.NumCPU())

	for i, chunk := range chunks {
		i, chunk := i, chunk
		g.Go(func() error {
			response, err := analyzeChunk(client, chunk.Content, *modelName)
			if err != nil {
				return fmt.Errorf("failed to analyze chunk %d: %w", i+1, err)
			}

			if !strings.Contains(response, "No dependencies found") {
				mu.Lock()
				responses = append(responses, response)
				mu.Unlock()
			}
			fmt.Println("Analyzed Chunk:", i+1)
			return nil
		})
	}

	if err := g.Wait(); err != nil {
		log.Fatalf("Failed to analyze chunks: %v", err)
	}

	uniqueResponses := filterSimilarResponses(responses, *threshold)
	fmt.Println("Filtered Responses; Size:", len(uniqueResponses))

	consolidatedResponse, err := consolidateDependencies(client, uniqueResponses, *modelName)
	if err != nil {
		log.Fatalf("Failed to consolidate dependencies: %v", err)
	}

	fmt.Println("Consolidated Dependencies:")
	fmt.Println(consolidatedResponse)

	// Parse the consolidated response.
	upstreamDeps := parseConsolidatedResponse(consolidatedResponse)

	// Build the YAML structure.
	yamlStructure := buildYAMLStructure(upstreamDeps)

	// Write the YAML to a file.
	err = writeYAML(yamlStructure, "dependencies.yaml")
	if err != nil {
		log.Fatalf("Failed to write YAML: %v", err)
	}

	fmt.Println("YAML file generated successfully")
}

func readPDF(filePath string) (string, error) {
	file, err := os.Open(filePath)
	if err != nil {
		return "", fmt.Errorf("error opening PDF file: %v", err)
	}

	stat, err := os.Stat(filePath)
	if err != nil {
		return "", fmt.Errorf("error getting file info: %v", err)
	}

	pdfReader, err := pdf.NewReader(file, stat.Size())
	if err != nil {
		return "", fmt.Errorf("error creating PDF reader: %v", err)
	}

	var (
		builder  strings.Builder
		previous string
	)
	for pageIndex := 1; pageIndex <= pdfReader.NumPage(); pageIndex++ {
		page := pdfReader.Page(pageIndex)
		if page.V.IsNull() {
			continue
		}

		textContent, err := page.GetPlainText(nil)
		if err != nil {
			return "", fmt.Errorf("error extracting text from page %d: %v", pageIndex, err)
		}

		if previous != "" && strings.HasPrefix(textContent, previous) {
			textContent = strings.TrimPrefix(textContent, previous)
		}
		previous = textContent

		if textContent == "" {
			continue
		}

		builder.WriteString(textContent)
	}

	return builder.String(), nil
}

var re = regexp.MustCompile(`[^a-z0-9\s]+`)

func preprocessText(text string) string {
	// Normalize and clean the text.
	doc, err := prose.NewDocument(text)
	if err != nil {
		log.Fatalf("Failed to create document: %v", err)
	}

	// Extract the cleaned text.
	var builder strings.Builder
	for _, tok := range doc.Tokens() {
		if tok.Tag != "PUNCT" { // Remove punctuation
			builder.WriteString(tok.Text + " ")
		}
	}

	cleanedText := builder.String()
	cleanedText = strings.ToLower(cleanedText)
	cleanedText = re.ReplaceAllString(cleanedText, " ")
	cleanedText = strings.TrimSpace(cleanedText)
	cleanedText = regexp.MustCompile(`\s+`).ReplaceAllString(cleanedText, " ")

	return cleanedText
}

const (
	tokenLimit     = 1 << 11 // 2048 tokens
	maxScanBufSize = 1 << 20 // 1 MB
	defaultBufSize = 1 << 16 // 64 KB
)

type Chunk struct {
	NChunk  int
	Content string
}

func ChunkReader(r io.Reader) ([]Chunk, error) {
	var chunks []Chunk
	scanner := bufio.NewScanner(r)
	scanner.Buffer(make([]byte, defaultBufSize), maxScanBufSize) // Increase buffer size for
	var currentChunk string

	tokenEncoder, err := tiktoken.GetEncoding(tiktoken.MODEL_CL100K_BASE)
	if err != nil {
		return nil, fmt.Errorf("failed to get token encoder: %w", err)
	}

	nChunk := 1

	for scanner.Scan() {
		line := scanner.Text()
		currentChunk += line + "\n"

		toks := tokenEncoder.Encode(currentChunk, nil, nil)
		if len(toks) > tokenLimit {
			start := 0
			for start < len(toks) {
				end := start + tokenLimit
				if end > len(toks) {
					end = len(toks)
				}

				chunkTokens := toks[start:end]
				chunkContent := tokenEncoder.Decode(chunkTokens)
				fmt.Printf("Creating chunk %d with %d tokens, data size %d\n", nChunk, len(chunkTokens), len(chunkContent)) // Debug statement
				chunks = append(chunks, Chunk{
					NChunk:  nChunk,
					Content: chunkContent,
				})
				nChunk++

				start = end
			}

			// Reset currentChunk after processing.
			currentChunk = ""
		}
	}

	if currentChunk != "" {
		toks := tokenEncoder.Encode(currentChunk, nil, nil)
		fmt.Printf("Final chunk %d with %d tokens\n", nChunk, len(toks)) // Debug statement
		chunks = append(chunks, Chunk{
			NChunk:  nChunk,
			Content: currentChunk,
		})
	}

	return chunks, scanner.Err()
}

const temperature = 0.5

func analyzeChunk(client *openai.Client, chunk, modelName string) (string, error) {
	systemMessage := openai.ChatCompletionMessage{
		Role:    openai.ChatMessageRoleSystem,
		Content: "You are an expert in analyzing research papers to identify dataset and model dependencies.",
	}

	userMessage := openai.ChatCompletionMessage{
		Role:    openai.ChatMessageRoleUser,
		Content: constructPrompt(chunk),
	}

	messages := []openai.ChatCompletionMessage{systemMessage, userMessage}

	resp, err := client.CreateChatCompletion(context.Background(), openai.ChatCompletionRequest{
		Model:       modelName,
		Messages:    messages,
		Temperature: temperature,
	})
	if err != nil {
		return "", err
	}

	return resp.Choices[0].Message.Content, nil
}

func constructPrompt(chunk string) string {
	prompt := fmt.Sprintf(`
I have a research paper text chunk below. Please extract and list all dataset dependencies and model dependencies mentioned in the text.

- Provide detailed names of the specific datasets and models.
- Only include dependencies that are explicitly mentioned in the text; do not infer any dependencies from the context.
- Exclude general concepts, libraries, and tools (e.g., Scikit-learn, Logistic Regression, Variational Autoencoder).
- Only include specific datasets and models.
- Be concise.
- If available, include links to references directly within each item in the format: [Name](https://link-to-reference).

        Text chunk:
        %s
        
        Please list:
        1. Dataset dependencies:
        2. Model dependencies:
        
        If no dependencies are found, reply with "No dependencies found".
    `, chunk)
	return prompt
}

// Filter similar responses using TF-IDF vectors and cosine similarity
func filterSimilarResponses(responses []string, threshold float64) []string {
	if len(responses) == 0 {
		return responses
	}

	// Create a new TF-IDF vectorizer
	vectorizer := nlp.NewCountVectoriser()
	transformer := nlp.NewTfidfTransformer()

	// Fit and transform the responses into TF-IDF matrix
	X, _ := vectorizer.FitTransform(responses...)
	tfidfMatrix, _ := transformer.FitTransform(X)

	filteredResponses := []string{responses[0]}
	for i := 1; i < len(responses); i++ {
		unique := true
		vectorA := extractRow(tfidfMatrix, i)
		for _, existingResponse := range filteredResponses {
			vectorB := extractRow(tfidfMatrix, indexOf(responses, existingResponse))
			if cosineSimilarity(vectorA, vectorB) > threshold {
				unique = false
				break
			}
		}
		if unique {
			filteredResponses = append(filteredResponses, responses[i])
		}
	}
	return filteredResponses
}

// Extract a row from a sparse matrix as a dense vector.
func extractRow(matrix mat.Matrix, row int) []float64 {
	_, cols := matrix.Dims()
	vector := make([]float64, cols)
	for i := 0; i < cols; i++ {
		vector[i] = matrix.At(row, i)
	}
	return vector
}

// Find the index of a response in the slice.
func indexOf(slice []string, item string) int {
	for i, v := range slice {
		if v == item {
			return i
		}
	}
	return -1
}

func cosineSimilarity(a, b []float64) float64 {
	dotProduct := floats.Dot(a, b)
	normA := floats.Norm(a, 2)
	normB := floats.Norm(b, 2)
	if normA == 0 || normB == 0 {
		return 0
	}
	return dotProduct / (normA * normB)
}

func consolidateDependencies(client *openai.Client, responses []string, modelName string) (string, error) {
	prompt := constructConsolidationPrompt(responses)
	systemMessage := openai.ChatCompletionMessage{
		Role:    openai.ChatMessageRoleSystem,
		Content: "You are an expert in analyzing and consolidating research paper dependencies.",
	}
	userMessage := openai.ChatCompletionMessage{
		Role:    openai.ChatMessageRoleUser,
		Content: prompt,
	}

	messages := []openai.ChatCompletionMessage{
		systemMessage,
		userMessage,
	}

	resp, err := client.CreateChatCompletion(context.Background(), openai.ChatCompletionRequest{
		Model:       modelName,
		Messages:    messages,
		Temperature: temperature,
	})
	if err != nil {
		return "", err
	}

	return resp.Choices[0].Message.Content, nil
}

func constructConsolidationPrompt(responses []string) string {
	combinedResponses := strings.Join(responses, "\n---\n")
	fmt.Println("Size of combined responses:", len(combinedResponses))
	prompt := fmt.Sprintf(`
I have multiple responses containing dataset dependencies and model dependencies from various chunks of a research paper.
Please consolidate these responses into a unique list of dataset dependencies and model dependencies, removing any duplicates.
Provide links to references directly within each item in the format: [Name](https://link-to-reference).

        Responses:
        %s

        Please provide:
        1. Consolidated list of dataset dependencies:
        2. Consolidated list of model dependencies:
    `, combinedResponses)
	return prompt
}

// Dependency represents a dependency with references
type Dependency struct {
	Type      string    `yaml:"type"`
	Metadata  Metadata  `yaml:"metadata"`
	Safety    Safety    `yaml:"safety"`
	Relations Relations `yaml:"relations"`
}

type Metadata struct {
	Name        string   `yaml:"name"`
	Refs        []string `yaml:"refs"`
	Description string   `yaml:"description"`
}

type Safety struct {
	NSFW     string `yaml:"nsfw"`
	CSAM     string `yaml:"csam"`
	Violence string `yaml:"violence"`
}

type Relations struct {
	Upstream []string `yaml:"upstream"`
}

var referenceRE = regexp.MustCompile(`\[(.*)]\((https://.*\))`)

// Parse the consolidated response to extract dependencies
func parseConsolidatedResponse(consolidatedResponse string) []string {
	matches := referenceRE.FindAllStringSubmatch(consolidatedResponse, -1)

	// If multiple references have the same link, they are likely from the header,
	// therefore do not include them as dependencies.
	links := make(map[string]struct{}, len(matches))
	names := make(map[string]struct{}, len(matches))

	for _, match := range matches {
		name := match[1]
		link := match[2]
		if _, ok := links[link]; ok {
			delete(names, name)
			continue
		}
		links[link] = struct{}{}
		names[name] = struct{}{}
	}

	upstreamDeps := make([]string, 0, len(names))
	for name := range names {
		upstreamDeps = append(upstreamDeps, name)
	}

	return upstreamDeps
}

// Build the YAML structure with the upstream dependencies
func buildYAMLStructure(upstreamDeps []string) Dependency {
	return Dependency{
		Type: "",
		Metadata: Metadata{
			Name:        "",
			Refs:        []string{},
			Description: "",
		},
		Safety: Safety{
			NSFW:     "",
			CSAM:     "",
			Violence: "",
		},
		Relations: Relations{
			Upstream: upstreamDeps,
		},
	}
}

// Write the YAML structure to a file
func writeYAML(dependency Dependency, _ string) error {
	data, err := yaml.Marshal(dependency)
	if err != nil {
		return err
	}

	fmt.Println(string(data))

	// err = os.WriteFile(filename, data, 0644)
	// if err != nil {
	// 	return err
	// }

	return nil
}
