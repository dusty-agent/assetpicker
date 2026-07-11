import json

from openai import OpenAI

from app.config import OPENAI_API_KEY


class LLMClient:

    def __init__(self):

        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
        )

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str = "gpt-5.5",
    ):

        response = self.client.responses.create(
            model=model,
            input=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
        )

        return json.loads(
            response.output_text,
        )