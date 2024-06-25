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
    DEFAULT_MAX_CHUNK_SIZE_TOKENS = 2048
    DEFAULT_CHUNK_OVERLAP_TOKENS = 256
    DEFAULT_NUM_RUNS = 5
    DEFAULT_PROMPT = """
    Please extract and list all dataset dependencies and model dependencies mentioned in the research paper.

    - Focus on specific datasets and models used for training or fine-tuning the main model. Generally proper nouns.
    - Only include dependencies that are explicitly mentioned as being used to create or fine-tune the model.
    - Do not include datasets or models used solely for validation, testing, or evaluation.
    - Exclude datasets that were created as part of the research study. Only list datasets and models that existed prior to this research.
    - Provide detailed names of the specific datasets and models.
    - Exclude general concepts, libraries, tools, and architectures (e.g., Scikit-learn, Logistic Regression, Variational Autoencoder, Text Transformer, etc).
    - Ensure the dependencies are directly involved in the creation or fine-tuning of the model, not just used as benchmarks or comparisons.
    - Concise Formatting: Present the information in a concise list format.

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

    Please list using the following format, providing ONLY the name of the dataset or model:
    Confirmed dependencies:
    - [Dataset 1]
    - [Dataset 2]
    - [Model 1]
    - [Model 2]

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

    The result should be:
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
