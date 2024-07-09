import argparse
import logging
import os
from pathlib import Path

from analyzer.config import AnalyzerConfig, OpenAIConfig
from analyzer.dependency_manager import build_yaml_structure, write_yaml
from analyzer.paper_analyzer import ResearchPaperAnalyzer
from analyzer.services import DatabaseService, OpenAIService


ASSISTANT_NAME: str = "Research Paper Analyzer"
STORE_NAME: str = "Model Papers"


def main() -> None:
    parser = argparse.ArgumentParser(description="Research Paper Analyzer CLI")
    parser.add_argument("-input", help="Path to the input PDF file", required=True)
    args = parser.parse_args()

    if not args.input:
        logging.fatal(
            "Input file path is required. Use -input flag to specify the PDF file."
        )
        return

    db_service = DatabaseService("cache.db")

    open_ai_config = OpenAIConfig()
    openai_service = OpenAIService(
        api_key=os.getenv("OPENAI_API_KEY"), config=open_ai_config
    )

    analyzer = ResearchPaperAnalyzer(
        db_service=db_service, openai_service=openai_service, config=AnalyzerConfig()
    )
    assistant_id = analyzer.get_or_create_assistant(
        open_ai_config.model_name, ASSISTANT_NAME
    )
    file_path = Path(args.input)
    store_name = f"{STORE_NAME}-{file_path.stem}"

    try:
        vector_store_result = analyzer.get_or_create_vector_store(store_name)
        analyzer.upload_files(vector_store_result.store_id, [str(file_path)])

        if not vector_store_result.exists:
            analyzer.update_assistant(assistant_id, vector_store_result.store_id)
            print(
                f"Successfully updated assistant with vector store {vector_store_result.store_id}"
            )

        results = analyzer.analyze_files_concurrently(assistant_id)
        final_dependencies = analyzer.consolidate_results(results)
        yaml_structure = build_yaml_structure(final_dependencies)
        write_yaml(yaml_structure)
    except Exception as e:
        logging.fatal(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
