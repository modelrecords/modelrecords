import threading
import concurrent.futures
import logging
from typing import List, Dict
from collections import namedtuple

from analyzer.config import AnalyzerConfig
from analyzer.services import DatabaseService, OpenAIService


VectorStoreResult = namedtuple("VectorStoreResult", ["store_id", "exists"])


class ResearchPaperAnalyzer:
    def __init__(
        self,
        db_service: DatabaseService,
        openai_service: OpenAIService,
        config: AnalyzerConfig,
    ):
        self.db_service = db_service
        self.openai_service = openai_service
        self.config = config

    def get_or_create_assistant(self, model_name: str, assistant_name: str) -> str:
        result = self.db_service.query(
            "SELECT id FROM assistants WHERE model_name = ? AND assistant_name = ?",
            (model_name, assistant_name),
        )
        if result:
            assistant_id = result[0]
            return assistant_id

        assistant_id = self.openai_service.create_assistant(assistant_name, model_name)
        self.db_service.execute(
            "INSERT OR REPLACE INTO assistants (model_name, assistant_name, id) VALUES (?, ?, ?)",
            (model_name, assistant_name, assistant_id),
        )
        return assistant_id

    def get_or_create_vector_store(self, store_name: str) -> VectorStoreResult:
        result = self.db_service.query(
            "SELECT id FROM vector_stores WHERE store_name = ?", (store_name,)
        )
        if result:
            return VectorStoreResult(store_id=result[0], exists=True)
        chunking_strategy = {
            "type": "static",
            "static": {
                "max_chunk_size_tokens": self.config.max_chunk_size_tokens,
                "chunk_overlap_tokens": self.config.chunk_overlap_tokens,
            },
        }
        store_id = self.openai_service.create_vector_store(
            store_name, chunking_strategy
        )
        self.db_service.execute(
            "INSERT OR REPLACE INTO vector_stores (store_name, id) VALUES (?, ?)",
            (store_name, store_id),
        )
        return VectorStoreResult(store_id=store_id, exists=False)

    def upload_files(self, store_id: str, filepaths: List[str]) -> List[str]:
        file_ids = []
        for filepath in filepaths:
            result = self.db_service.query(
                "SELECT id FROM files WHERE file_path = ?", (filepath,)
            )
            if result:
                file_id = result[0]
                file_ids.append(file_id)
            else:
                file_id = self.openai_service.upload_file_to_vector_store(
                    store_id, filepath
                )
                file_ids.append(file_id)
                self.db_service.execute(
                    "INSERT OR REPLACE INTO files (file_path, id) VALUES (?, ?)",
                    (filepath, file_id),
                )
        return file_ids

    def update_assistant(self, assistant_id: str, vector_store_id: str) -> None:
        tool_resources = {"file_search": {"vector_store_ids": [vector_store_id]}}
        self.openai_service.client.beta.assistants.update(
            assistant_id,
            tool_resources=tool_resources,
        )

    def process_chunk(self, assistant_id: str) -> List[str]:
        full_response = list(
            self.openai_service.create_and_run_thread(assistant_id, self.config.prompt)
        )
        msgs = "".join(full_response)

        # First filter.
        data = self.construct_filter_prompt(msgs, self.config.filter_prompt)
        res = self.openai_service.analyze_chunk(data)

        # Second filter.
        data = self.construct_filter_prompt(res, self.config.second_filter_prompt)
        res = self.openai_service.analyze_chunk(data)

        # Extract dependencies.
        dependencies = [
            line[2:].strip() for line in res.split("\n") if line.startswith("- ")
        ]
        return dependencies

    def construct_filter_prompt(self, text: str, prompt: str) -> str:
        return f"{prompt}\nText chunk:{text}"

    def consolidate_results(self, results: List[List[str]]) -> List[str]:
        dep_count: Dict[str, int] = {}
        total_results = len(results)
        for dependencies in results:
            dep_set = set(dependencies)
            for dep in dep_set:
                dep_count[dep] = dep_count.get(dep, 0) + 1

        majority_threshold = total_results // 2
        final_dependencies = [
            dep for dep, count in dep_count.items() if count > majority_threshold
        ]
        return final_dependencies

    def analyze_files_concurrently(self, assistant_id: str) -> List[List[str]]:
        results = []
        errors = []
        results_lock = threading.Lock()
        errors_lock = threading.Lock()

        def process_chunk_wrapper():
            try:
                dependencies = self.process_chunk(assistant_id)
                with results_lock:
                    results.append(dependencies)
                print("Run completed successfully")
            except Exception as exc:
                with errors_lock:
                    errors.append(f"Run generated an exception: {exc}")

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.config.num_runs
        ) as executor:
            futures = [
                executor.submit(process_chunk_wrapper)
                for _ in range(self.config.num_runs)
            ]
            concurrent.futures.wait(futures)

        if errors:
            for error in errors:
                logging.error(error)
            logging.fatal("One or more runs failed")
            return []

        return results
