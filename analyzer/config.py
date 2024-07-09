from typing import Dict, List


class OpenAIConfig:
    DEFAULT_TEMPERATURE: float = 0.1
    DEFAULT_INSTRUCTIONS: str = (
        "You are an expert in analyzing research papers, and you have access to these papers to identify dataset and model dependencies."
    )
    DEFAULT_MODEL_NAME: str = "gpt-4o"
    DEFAULT_FILE_SEARCH_TOOL_ID: str = "file_search"

    def __init__(
        self,
        temperature: float = DEFAULT_TEMPERATURE,
        instructions: str = DEFAULT_INSTRUCTIONS,
        model_name: str = DEFAULT_MODEL_NAME,
        tools: List[Dict] = None,
        file_search_tool_id: str = DEFAULT_FILE_SEARCH_TOOL_ID,
    ):
        self.temperature = temperature
        self.instructions = instructions
        self.model_name = model_name
        self.tools = tools if tools else [{"type": file_search_tool_id}]


class AnalyzerConfig:
    DEFAULT_MAX_CHUNK_SIZE_TOKENS = 4096
    DEFAULT_CHUNK_OVERLAP_TOKENS = 256
    DEFAULT_NUM_RUNS = 5
    DEFAULT_PROMPT = """
    Please extract and list all dataset dependencies and model dependencies mentioned in the research paper that were used for training or fine-tuning the main model

    - Include pre-trained models that were fine-tuned or further trained as part of the model development process.
    - Exclude all datasets and models used solely for validation, testing, evaluation, baseline comparisons or benchmarking.
    - For datasets, if a subset was used, list the original, larger dataset as the dependency.
    - Provide a brief explanation for each dependency, showing how it was used in the model development.
    - Exclude general concepts, libraries, tools, and architectures (e.g., Scikit-learn, Logistic Regression, Variational Autoencoder, Text Transformer, etc).

    For instance, if a paper states 'we fine-tuned a pre-trained Model X', then Model X should be listed as a dependency.

    Present the information in this format:
    Dataset dependencies:
    - [Dataset name]: [Brief explanation of its use in training/fine-tuning]
    Model dependencies:
    - [Model name]: [Brief explanation of its use in training/fine-tuning]

    If no relevant datasets or models are identified, state "None identified" under the respective category.
    DO NOT include any other information in your response.
    """
    DEFAULT_FILTER_PROMPT = """
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

    Present the information in this format:
    Confirmed dependencies:
    - [Dataset 1 name]
    - [Dataset 2 name]
    - [Model 1 name]
    - [Model 2 name]

    If no dependencies are confirmed for training/fine-tuning, state "None confirmed" under the respective category.
    DO NOT include any other information in your response.
    """
    DEFAULT_SECOND_FILTER_PROMPT = """
    I have a list of dependencies, and I need to extract only the specific models, datasets, or proper nouns.
    Generic terms or non-specific descriptions should be removed.
    Please provide ONLY the names of the specific models, datasets, or technologies. For example, given:

    Confirmed dependencies:
    - LAION
    - Pre-trained CLIP model

    Present the information in this format:
    - LAION
    - CLIP
    DO NOT include any other information in your response.
    """

    def __init__(
        self,
        max_chunk_size_tokens: int = DEFAULT_MAX_CHUNK_SIZE_TOKENS,
        chunk_overlap_tokens: int = DEFAULT_CHUNK_OVERLAP_TOKENS,
        num_runs: int = DEFAULT_NUM_RUNS,
        prompt: str = DEFAULT_PROMPT,
        filter_prompt: str = DEFAULT_FILTER_PROMPT,
        second_filter_prompt: str = DEFAULT_SECOND_FILTER_PROMPT,
    ):
        self.max_chunk_size_tokens = max_chunk_size_tokens
        self.chunk_overlap_tokens = chunk_overlap_tokens
        self.num_runs = num_runs
        self.prompt = prompt
        self.filter_prompt = filter_prompt
        self.second_filter_prompt = second_filter_prompt
