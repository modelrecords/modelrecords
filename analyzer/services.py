import sqlite3
import threading
import logging
from typing import Optional, Tuple

from openai import OpenAI
from analyzer.config import OpenAIConfig


class OpenAIService:
    def __init__(self, api_key: str, config: OpenAIConfig):
        self.client = OpenAI(api_key=api_key)
        self.config = config

    def create_assistant(self, name: str):
        assistant = self.client.beta.assistants.create(
            model=self.config.model_name,
            name=name,
            instructions=self.config.instructions,
            tools=self.config.tools,
        )
        return assistant.id

    def create_vector_store(self, store_name: str, chunking_strategy: dict):
        store = self.client.beta.vector_stores.create(
            name=store_name, chunking_strategy=chunking_strategy
        )
        return store.id

    def upload_file_to_vector_store(self, store_id: str, filepath: str):
        file = self.client.files.create(file=filepath, purpose="assistants")
        _ = self.client.beta.vector_stores.files.create_and_poll(
            vector_store_id=store_id, file_id=file.id
        )
        return file.id

    def create_and_run_thread(self, assistant_id: str, content: str):
        thread = self.client.beta.threads.create(
            messages=[{"role": "user", "content": content}]
        )
        full_response = []
        with self.client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant_id,
            instructions=self.config.instructions,
            model=self.config.model_name,
            temperature=self.config.temperature,
        ) as stream:
            for text in stream.text_deltas:
                full_response.append(text)
        return "".join(full_response)

    def analyze_chunk(self, chunk: str):
        response = self.client.chat.completions.create(
            model=self.config.model_name,
            messages=[
                {"role": "system", "content": self.config.instructions},
                {"role": "user", "content": chunk},
            ],
            temperature=self.config.temperature,
        )
        return response.choices[0].message.content


class DatabaseService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.lock = threading.Lock()
        self.init_db()

    def init_db(self) -> None:
        with self.lock:
            if self.conn is None:
                try:
                    self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
                    self.cursor = self.conn.cursor()
                    self.cursor.executescript(
                        """
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
                        """
                    )
                    self.conn.commit()
                except sqlite3.Error as e:
                    logging.error(f"Failed to initialize database: {e}")
                    raise

    def query(self, query: str, params: Tuple) -> Optional[Tuple]:
        with self.lock:
            try:
                self.cursor.execute(query, params)
                result = self.cursor.fetchone()
                logging.debug(f"Query result: {result}")
                return result
            except sqlite3.Error as e:
                logging.error(f"Failed to execute query: {e}")
                raise

    def execute(self, query: str, params: Tuple) -> None:
        with self.lock:
            try:
                self.cursor.execute(query, params)
                self.conn.commit()
            except sqlite3.Error as e:
                logging.error(f"Failed to execute: {e}")
                raise
