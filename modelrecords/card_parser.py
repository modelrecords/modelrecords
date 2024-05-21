import os
from openai import OpenAI
import json

class Parser():
    def __init__(self):
        self.templates = 'modelrecord/templates/card_parser'
        self.answers = {}
        self.all_texts = {}
        self._load_gpt()

    def _load_gpt(self):
        self.openai_client = OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
        )

    def prepare_prompt(self, template, all_text):
        with open(f'{self.templates}/{template}', 'r') as f:
            tpl = ''.join(f.readlines())
        txt = tpl.replace('{all_text}',all_text)
        return txt
    
    def load_texts(self, paths=[], truncate=150_000):
        for path in paths:
            with open(path, 'r') as f:
                self.all_texts[path] = ''.join(f.readlines())[:truncate]

    def as_text_blob(self):
        blob = ''
        for lines in self.all_texts.values():
            blob += lines

        return blob

    def parse_with_gpt(self, paths):
        self.load_texts(paths)
        queries = ['model_card_000.txt', 'model_card_001.txt']
        for query in queries:
            content = self.prepare_prompt(query, self.as_text_blob())
            chat_completion = self.openai_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": content,
                    }
                ],
                model="gpt-4-turbo-preview",
            )
            response = chat_completion
            parsed_answers = json.loads('{' + f"{response.choices[0].message.content.split('{')[1].split('}')[0]}" + '}')

            for key,val in parsed_answers.items():
                self.answers[key] = val
