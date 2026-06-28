from openai import OpenAI


class LLMClient:

    def __init__(self):
        self.client = OpenAI()

    def chat(self, prompt: str):
        ...