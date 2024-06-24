package main

import (
	"bytes"
	"context"
	"database/sql"
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"regexp"
	"strings"
	"sync"
	"time"

	_ "github.com/mattn/go-sqlite3"
	"github.com/sashabaranov/go-openai"
	"gopkg.in/yaml.v3"
)

const (
	assistantName = "Research Paper Analyzer"
	storeName     = "Model Papers"
	instructions  = "You are an expert in analyzing research papers, and you have access to these papers to identify dataset and model dependencies."
	modelName     = "gpt-4o"
	prompt        = `
Please extract and list all dataset dependencies and model dependencies mentioned in the research paper.

- Focus on specific datasets and models used for training or fine-tuning the main model. Generally proper nouns.
- Only include dependencies that are explicitly mentioned as being used to create or fine-tune the model.
- Do not include datasets or models used solely for validation, testing, or evaluation.
- Exclude datasets that were created as part of the research study. Only list datasets and models that existed prior to this research.
- Provide detailed names of the specific datasets and models.
- Exclude general concepts, libraries, tools, and architectures (e.g., Scikit-learn, Logistic Regression, Variational Autoencoder, Text Transformer, etc).
- Ensure the dependencies are directly involved in the creation or fine-tuning of the model, not just used as benchmarks or comparisons.
- Concise Formatting: Present the information in a concise list format.
- Include References (If Available): If references are available within the paper, include links to them directly within each item in the format: [Name](https://link-to-reference).

For each listed dependency, provide sufficient context from the paper that confirms its use in training or fine-tuning the model.
This should include sentences around where the dependency is mentioned, the context of its use, and any relevant details that confirm its role in the model development process.

Please ONLY list:
1. Dataset dependencies:
2. Model dependencies:

If no relevant datasets or models are identified, state "None identified" under the respective category.
DO NOT include any other information in your response.
`
	filterPrompt = `
Review the list of dependencies and their contexts carefully.
Identify and list only the datasets and models that meet ALL of the following criteria:
1. Were definitively used for training or fine-tuning the main model described in the paper.
2. Existed prior to this research and were not created solely as part of this study. Note: Datasets curated from existing public sources are considered pre-existing if not uniquely created for this study.
3. Are not used solely for validation, testing, evaluation, or comparison.

For datasets, focus on large-scale datasets used for pre-training or fine-tuning.
For models, include only those that were directly used as a base for further training or adaptation.

Exclude:
- Datasets created specifically for this study
- Models used only for comparison or baseline results
- Datasets used only for evaluation or testing
- General concepts, libraries, tools, and architectures (e.g., Scikit-learn, Logistic Regression, Variational Autoencoder, Text Transformer, etc).

For each retained dependency, provide:
1. ONLY, the name of the dataset or model.

Please list using the following format, providing ONLY the name of the dataset or model:
Confirmed dependencies:
- [Dataset 1]
- [Dataset 2]
- [Model 1]
- [Model 2]

If no dependencies are confirmed for training/fine-tuning, state "None confirmed" under the respective category.
DO NOT include any other information in your response.
`
	secondFilterPrompt = `
I have a list of dependencies, and I need to extract only the specific models, datasets, or proper nouns.
Generic terms or non-specific descriptions should be removed.
Please provide ONLY the names of the specific models, datasets, or technologies. For example, given:

Confirmed dependencies:
- LAION
- Pre-trained CLIP model

The result should be:
- LAION
- CLIP
DO NOT include any other information in your response.
`
)

var db *sql.DB
var dbOnce sync.Once

func initDB() {
	dbOnce.Do(func() {
		var err error
		db, err = sql.Open("sqlite3", "./cache.db")
		if err != nil {
			log.Fatalf("Failed to open database: %v", err)
		}

		_, err = db.Exec(`
			CREATE TABLE IF NOT EXISTS assistants (
				model_name TEXT,
				assistant_name TEXT,
				id TEXT,
				PRIMARY KEY (model_name, assistant_name)
			);
			CREATE TABLE IF NOT EXISTS vector_stores (
				store_name TEXT PRIMARY KEY,
				id TEXT
			);
			CREATE TABLE IF NOT EXISTS files (
				file_path TEXT PRIMARY KEY,
				id TEXT
			);
			CREATE TABLE IF NOT EXISTS vector_files (
				file_id TEXT PRIMARY KEY,
				vector_store_id TEXT,
				status TEXT
			);

			CREATE INDEX IF NOT EXISTS idx_assistants ON assistants (model_name, assistant_name);
			CREATE INDEX IF NOT EXISTS idx_vector_stores ON vector_stores (store_name);
			CREATE INDEX IF NOT EXISTS idx_files ON files (file_path);
			CREATE INDEX IF NOT EXISTS idx_vector_files ON vector_files (file_id, vector_store_id);
		`)
		if err != nil {
			log.Fatalf("Failed to create tables and indexes: %v", err)
		}
	})
}

func getAssistant(modelName, assistantName string) (string, bool) {
	var id string
	err := db.QueryRow("SELECT id FROM assistants WHERE model_name = ? AND assistant_name = ?", modelName, assistantName).Scan(&id)
	if errors.Is(err, sql.ErrNoRows) {
		return "", false
	}
	if err != nil {
		log.Fatalf("Failed to query assistant: %v", err)
	}
	return id, true
}

func setAssistant(modelName, assistantName, id string) {
	_, err := db.Exec("INSERT OR REPLACE INTO assistants (model_name, assistant_name, id) VALUES (?, ?, ?)", modelName, assistantName, id)
	if err != nil {
		log.Fatalf("Failed to insert assistant: %v", err)
	}
}

func getVectorStore(storeName string) (string, bool) {
	var id string
	err := db.QueryRow("SELECT id FROM vector_stores WHERE store_name = ?", storeName).Scan(&id)
	if errors.Is(err, sql.ErrNoRows) {
		return "", false
	}
	if err != nil {
		log.Fatalf("Failed to query vector store: %v", err)
	}
	return id, true
}

func setVectorStore(storeName, id string) {
	_, err := db.Exec("INSERT OR REPLACE INTO vector_stores (store_name, id) VALUES (?, ?)", storeName, id)
	if err != nil {
		log.Fatalf("Failed to insert vector store: %v", err)
	}
}

func getFile(filePath string) (string, bool) {
	var id string
	err := db.QueryRow("SELECT id FROM files WHERE file_path = ?", filePath).Scan(&id)
	if errors.Is(err, sql.ErrNoRows) {
		return "", false
	}
	if err != nil {
		log.Fatalf("Failed to query file: %v", err)
	}
	return id, true
}

func setFile(filePath, id string) {
	_, err := db.Exec("INSERT OR REPLACE INTO files (file_path, id) VALUES (?, ?)", filePath, id)
	if err != nil {
		log.Fatalf("Failed to insert file: %v", err)
	}
}

func getVectorFile(fileID, vectorStoreID string) (string, bool) {
	var status string
	err := db.QueryRow("SELECT status FROM vector_files WHERE file_id = ? AND vector_store_id = ?", fileID, vectorStoreID).Scan(&status)
	if errors.Is(err, sql.ErrNoRows) {
		return "", false
	}
	if err != nil {
		log.Fatalf("Failed to query vector file: %v", err)
	}
	return status, true
}

func setVectorFile(fileID, vectorStoreID, status string) {
	_, err := db.Exec("INSERT OR REPLACE INTO vector_files (file_id, vector_store_id, status) VALUES (?, ?, ?)", fileID, vectorStoreID, status)
	if err != nil {
		log.Fatalf("Failed to insert vector file: %v", err)
	}
}

func main() {
	filePath := flag.String("input", "", "Path to the input PDF file")
	flag.Parse()

	if *filePath == "" {
		log.Fatalf("Input file path is required. Use -input flag to specify the PDF file.")
	}

	initDB()

	ctx := context.Background()
	apiKey := os.Getenv("OPENAI_API_KEY")
	client := openai.NewClient(apiKey)

	assistant, err := getOrCreateAssistant(ctx, client, modelName, assistantName, instructions)
	if err != nil {
		log.Fatalf("Failed to create assistant: %v", err)
	}

	filename := strings.Split(*filePath, "/")
	filename = strings.Split(filename[len(filename)-1], ".")

	store := fmt.Sprintf("%s-%s", storeName, filename)

	_, vectorStoreID, err := getOrCreateVectorStoreAndUploadFiles(ctx, client, store, apiKey, []string{*filePath})
	if err != nil {
		log.Fatalf("Failed to create vector store and upload files: %v", err)
	}

	err = updateAssistant(ctx, client, assistant, vectorStoreID)
	if err != nil {
		log.Fatalf("Failed to update assistant: %v", err)
	}

	const temperature = 0.1
	const numRuns = 5

	var wg sync.WaitGroup
	var mu sync.Mutex
	results := make([][]string, 0, numRuns)
	errChan := make(chan error, numRuns)

	for i := 0; i < numRuns; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()

			msgs, err := createAndRunThread(ctx, client, assistant, prompt, temperature)
			if err != nil {
				errChan <- fmt.Errorf("failed to create and run thread: %w", err)
				return
			}

			data := constructFirstFilterPrompt(msgs)
			res, err := analyzeChunk(ctx, client, data, instructions)
			if err != nil {
				errChan <- fmt.Errorf("failed to analyze chunk: %w", err)
				return
			}

			data = constructSecondFilterPrompt(res)
			res, err = analyzeChunk(ctx, client, data, instructions)
			if err != nil {
				errChan <- fmt.Errorf("failed to analyze chunk: %w", err)
				return
			}

			lines := strings.Split(res, "\n")
			var dependencies []string
			for _, line := range lines {
				line = strings.TrimSpace(line)
				if strings.HasPrefix(line, "- ") {
					dependency := strings.TrimSpace(line[2:])
					dependencies = append(dependencies, dependency)
				}
			}

			mu.Lock()
			results = append(results, dependencies)
			mu.Unlock()
		}()
	}

	wg.Wait()
	close(errChan)

	if len(errChan) > 0 {
		for err := range errChan {
			log.Println(err)
		}
		log.Fatalf("One or more runs failed")
	}
	fmt.Println("Dependencies extracted successfully")

	finalDependencies := consolidateResults(results)
	fmt.Printf("Consolidated dependencies\n\n")

	yamlStructure := buildYAMLStructure(finalDependencies)

	fmt.Println("BUILDING UMR...")
	err = writeYAML(yamlStructure, "dependencies.yaml")
	if err != nil {
		log.Fatalf("Failed to write YAML: %v", err)
	}

	// fmt.Println("YAML file generated successfully")
}

func getOrCreateAssistant(ctx context.Context, client *openai.Client, modelName, assistantName, instructions string) (string, error) {
	if id, exists := getAssistant(modelName, assistantName); exists {
		return id, nil
	}

	id, err := createAssistant(ctx, client, modelName, assistantName, instructions)
	if err != nil {
		return "", err
	}

	setAssistant(modelName, assistantName, id)
	return id, nil
}

func getOrCreateVectorStoreAndUploadFiles(ctx context.Context, client *openai.Client, storeName, apiKey string, filepaths []string) ([]string, string, error) {
	if id, exists := getVectorStore(storeName); exists {
		var fileIDs []string
		for _, filepath := range filepaths {
			if fileID, exists := getFile(filepath); exists {
				fileIDs = append(fileIDs, fileID)
			} else {
				uploadedFileIDs, err := uploadAndPollFiles(ctx, client, id, apiKey, []string{filepath})
				if err != nil {
					return nil, "", err
				}
				fileIDs = append(fileIDs, uploadedFileIDs...)
				setFile(filepath, uploadedFileIDs[0])
			}
		}
		return fileIDs, id, nil
	}

	uploadedFileIDs, vectorStoreID, err := createVectorStoreAndUploadFiles(ctx, client, storeName, apiKey, filepaths)
	if err != nil {
		return nil, "", err
	}

	setVectorStore(storeName, vectorStoreID)
	for i, filepath := range filepaths {
		setFile(filepath, uploadedFileIDs[i])
	}

	return uploadedFileIDs, vectorStoreID, nil
}

func createAssistant(ctx context.Context, client *openai.Client, modelName, assistantName, instructions string) (string, error) {
	resp, err := client.CreateAssistant(ctx, openai.AssistantRequest{
		Instructions: &instructions,
		Model:        modelName,
		Name:         &assistantName,
		Tools:        []openai.AssistantTool{{Type: "file_search"}},
	})
	if err != nil {
		return "", err
	}

	return resp.ID, nil
}

func createVectorStoreAndUploadFiles(ctx context.Context, client *openai.Client, storeName, apiKey string, filepaths []string) ([]string, string, error) {
	vectorStoreID, err := createAndPollVectorStore(ctx, client, storeName)
	if err != nil {
		return nil, "", err
	}

	uploadedFileIDs, err := uploadAndPollFiles(ctx, client, vectorStoreID, apiKey, filepaths)
	if err != nil {
		return nil, "", err
	}

	return uploadedFileIDs, vectorStoreID, nil
}

func createAndPollVectorStore(ctx context.Context, client *openai.Client, storeName string) (string, error) {
	resp, err := client.CreateVectorStore(ctx, openai.VectorStoreRequest{Name: storeName})
	if err != nil {
		return "", err
	}

	resultChan, errorChan, doneChan := pollVectorStoreCreation(ctx, client, resp.ID)

	for {
		select {
		case result, ok := <-resultChan:
			if !ok {
				return "", nil
			}
			fmt.Println("Vector Store Creation Status:", result)
		case err := <-errorChan:
			return "", err
		case <-doneChan:
			return resp.ID, nil
		}
	}
}

func pollVectorStoreCreation(ctx context.Context, client *openai.Client, vectorStoreID string) (<-chan string, <-chan error, <-chan struct{}) {
	resultChan := make(chan string)
	errorChan := make(chan error)
	doneChan := make(chan struct{})

	go func() {
		defer close(resultChan)
		defer close(errorChan)
		defer close(doneChan)

		for {
			resp, err := client.RetrieveVectorStore(ctx, vectorStoreID)
			if err != nil {
				errorChan <- err
				return
			}

			resultChan <- string(resp.Status)

			if resp.Status == "completed" {
				resultChan <- "Vector Store creation completed successfully"
				doneChan <- struct{}{}
				return
			}

			time.Sleep(1 * time.Second)
		}
	}()

	return resultChan, errorChan, doneChan
}

func uploadAndPollFiles(ctx context.Context, client *openai.Client, vectorStoreID, apiKey string, filepaths []string) ([]string, error) {
	var uploadedFileIDs []string
	for _, filepath := range filepaths {
		fileID, err := uploadAndPollFile(ctx, client, vectorStoreID, filepath, apiKey)
		if err != nil {
			return nil, err
		}
		uploadedFileIDs = append(uploadedFileIDs, fileID)
	}
	return uploadedFileIDs, nil
}

func uploadAndPollFile(ctx context.Context, client *openai.Client, vectorStoreID, filepath, apiKey string) (string, error) {
	resp, err := client.CreateFile(ctx, openai.FileRequest{FilePath: filepath, Purpose: "assistants"})
	if err != nil {
		return "", err
	}
	fmt.Printf("File uploaded successfully: %s\n", filepath)

	fileID := resp.ID
	if status, exists := getVectorFile(fileID, vectorStoreID); exists && status == "completed" {
		return fileID, nil
	}

	vectorFileID, err := createVectorStoreFile(ctx, apiKey, vectorStoreID, fileID)
	if err != nil {
		return "", err
	}

	resultChan, errorChan, doneChan := pollVectorFileUpload(ctx, apiKey, vectorStoreID, vectorFileID)

	for {
		select {
		case result, ok := <-resultChan:
			if !ok {
				return "", nil
			}
			fmt.Println("Vector File Upload Status:", result)
		case err := <-errorChan:
			return "", err
		case <-doneChan:
			setVectorFile(fileID, vectorStoreID, "completed")
			return fileID, nil
		}
	}
}

type VectorStoreFileResponse struct {
	ID               string  `json:"id"`
	Object           string  `json:"object"`
	UsageBytes       int64   `json:"usage_bytes"`
	CreatedAt        int64   `json:"created_at"`
	VectorStoreID    string  `json:"vector_store_id"`
	Status           string  `json:"status"`
	LastError        *string `json:"last_error"`
	ChunkingStrategy struct {
		Type   string `json:"type"`
		Static struct {
			MaxChunkSizeTokens int `json:"max_chunk_size_tokens"`
			ChunkOverlapTokens int `json:"chunk_overlap_tokens"`
		} `json:"static"`
	} `json:"chunking_strategy"`
}

func createVectorStoreFile(ctx context.Context, apiKey, vectorStoreID, fileID string) (string, error) {
	url := fmt.Sprintf("https://api.openai.com/v1/vector_stores/%s/files", vectorStoreID)

	const (
		maxChunkSizeTokens = 2048
		chunkOverlapTokens = 256
	)
	chunkingStrategy := map[string]any{
		"type": "static",
		"static": map[string]interface{}{
			"max_chunk_size_tokens": maxChunkSizeTokens,
			"chunk_overlap_tokens":  chunkOverlapTokens,
		},
	}

	requestBody, err := json.Marshal(map[string]any{
		"file_id":           fileID,
		"chunking_strategy": chunkingStrategy,
	})
	if err != nil {
		return "", err
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, url, bytes.NewBuffer(requestBody))
	if err != nil {
		return "", err
	}

	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", apiKey))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("OpenAI-Beta", "assistants=v2")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("failed to create vector store file: %s", string(bodyBytes))
	}

	var res VectorStoreFileResponse
	err = json.NewDecoder(resp.Body).Decode(&res)
	if err != nil {
		return "", err
	}

	return res.ID, nil
}

func pollVectorFileUpload(ctx context.Context, apiKey, vectorStoreID, fileID string) (<-chan string, <-chan error, <-chan struct{}) {
	resultChan := make(chan string)
	errorChan := make(chan error)
	doneChan := make(chan struct{})

	go func() {
		defer close(resultChan)
		defer close(errorChan)
		defer close(doneChan)

		for {
			status, err := getVectorFileStatus(ctx, apiKey, vectorStoreID, fileID)
			if err != nil {
				errorChan <- err
				return
			}

			resultChan <- status

			if status == "completed" {
				resultChan <- "Vector File upload completed successfully"
				doneChan <- struct{}{}
				return
			}

			time.Sleep(1 * time.Second)
		}
	}()

	return resultChan, errorChan, doneChan
}

func getVectorFileStatus(ctx context.Context, apiKey, vectorStoreID, fileID string) (string, error) {
	url := fmt.Sprintf("https://api.openai.com/v1/vector_stores/%s/files/%s", vectorStoreID, fileID)
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, url, nil)
	if err != nil {
		return "", err
	}

	req.Header.Set("Authorization", fmt.Sprintf("Bearer %s", apiKey))
	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("OpenAI-Beta", "assistants=v2")

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		bodyBytes, _ := io.ReadAll(resp.Body)
		return "", fmt.Errorf("failed to retrieve vector file status: %s", string(bodyBytes))
	}

	var res VectorStoreFileResponse
	if err = json.NewDecoder(resp.Body).Decode(&res); err != nil {
		return "", err
	}

	return res.Status, nil
}

func updateAssistant(ctx context.Context, client *openai.Client, assistantID, vectorStoreID string) error {
	_, err := client.ModifyAssistant(ctx, assistantID, openai.AssistantRequest{
		ToolResources: &openai.AssistantToolResource{
			FileSearch: &openai.AssistantToolFileSearch{
				VectorStoreIDs: []string{vectorStoreID},
			},
		},
	})
	return err
}

// createAndRunThread creates and runs a thread, streaming the results.
func createAndRunThread(ctx context.Context, client *openai.Client, assistantID, content string, temp float32) (string, error) {
	resp, err := client.CreateThreadAndRun(ctx, openai.CreateThreadAndRunRequest{
		RunRequest: openai.RunRequest{
			AssistantID:  assistantID,
			Model:        modelName,
			Instructions: instructions,
			Temperature:  &temp,
		},
		Thread: openai.ThreadRequest{
			Messages: []openai.ThreadMessage{{
				Role:    openai.ChatMessageRoleUser,
				Content: content,
			}},
		},
	})
	if err != nil {
		return "", err
	}

	resultChan, errorChan, doneChan := StreamRunResult(ctx, client, resp.ThreadID, resp.ID)

	for {
		select {
		case result, ok := <-resultChan:
			if !ok {
				return "", nil
			}
			fmt.Println("Run Result:", result)
		case err := <-errorChan:
			return "", err
		case <-doneChan:
			// When done, list messages in the thread.
			return listMessages(ctx, client, resp.ThreadID)
		}
	}
}

// StreamRunResult retrieves the run result and streams it back to the caller via a channel.
func StreamRunResult(ctx context.Context, client *openai.Client, threadID, runID string) (<-chan string, <-chan error, <-chan struct{}) {
	resultChan := make(chan string)
	errorChan := make(chan error)
	doneChan := make(chan struct{})

	go func() {
		defer close(resultChan)
		defer close(errorChan)
		defer close(doneChan)

		for {
			resp, err := client.RetrieveRun(ctx, threadID, runID)
			if err != nil {
				errorChan <- err
				return
			}

			// Stream intermediate result
			resultChan <- string(resp.Status)

			// Check if the run is finished
			if resp.Status == openai.RunStatusCompleted {
				resultChan <- "Run completed successfully"
				doneChan <- struct{}{}
				return
			}

			// Sleep for a while before polling again
			time.Sleep(1 * time.Second)
		}
	}()

	return resultChan, errorChan, doneChan
}

// listMessages lists and prints messages in the thread.
func listMessages(ctx context.Context, client *openai.Client, threadID string) (string, error) {
	msgResp, err := client.ListMessage(ctx, threadID, nil, nil, nil, nil)
	if err != nil {
		return "", err
	}

	var builder strings.Builder
	// Print the messages.
	for _, msg := range msgResp.Messages {
		if msg.Role != openai.ChatMessageRoleUser {
			for _, content := range msg.Content {
				builder.WriteString(content.Text.Value)
				builder.WriteString("\n")
			}
		}
	}

	return builder.String(), nil
}

func analyzeChunk(ctx context.Context, client *openai.Client, chunk, instruction string) (string, error) {
	const temperature = 0.2

	systemMessage := openai.ChatCompletionMessage{
		Role:    openai.ChatMessageRoleSystem,
		Content: instruction,
	}

	userMessage := openai.ChatCompletionMessage{
		Role:    openai.ChatMessageRoleUser,
		Content: chunk,
	}

	messages := []openai.ChatCompletionMessage{systemMessage, userMessage}

	resp, err := client.CreateChatCompletion(ctx, openai.ChatCompletionRequest{
		Model:       modelName,
		Messages:    messages,
		Temperature: temperature,
	})
	if err != nil {
		return "", err
	}

	return resp.Choices[0].Message.Content, nil
}

func constructFirstFilterPrompt(chunk string) string {
	prompt := fmt.Sprintf(`%s\nText chunk:%s`, filterPrompt, chunk)
	return prompt
}

func constructSecondFilterPrompt(chunk string) string {
	prompt := fmt.Sprintf(`%s\n %s\n 
Please return only the specific, named models or proper nouns, removing any generic terms
`, secondFilterPrompt, chunk)
	return prompt
}

func consolidateResults(results [][]string) []string {
	depCount := make(map[string]int)
	totalResults := 0

	for _, dependencies := range results {
		depSet := make(map[string]struct{})
		for _, dep := range dependencies {
			depSet[dep] = struct{}{}
		}
		for dep := range depSet {
			depCount[dep]++
		}
		totalResults++
	}

	finalDependencies := make([]string, 0)
	majorityThreshold := totalResults / 2
	for dep, count := range depCount {
		if count > majorityThreshold {
			finalDependencies = append(finalDependencies, dep)
		}
	}

	return finalDependencies
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

var dependencyRE = regexp.MustCompile(`(?m)^\s*-\s*(\w+.*?)\s*(?i:(dataset|model))?\s*$`)

func parseConsolidatedResponse(consolidatedResponse string) []string {
	var dependencies []string

	matches := dependencyRE.FindAllStringSubmatch(consolidatedResponse, -1)

	for _, match := range matches {
		if len(match) > 1 {
			dependencies = append(dependencies, strings.TrimSpace(match[1]))
		}
	}

	return dependencies
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
