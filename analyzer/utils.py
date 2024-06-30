import os
from dotenv import load_dotenv, find_dotenv


def get_openai_api_key():
    _ = load_dotenv(find_dotenv())

    return os.getenv("OPENAI_API_KEY")
