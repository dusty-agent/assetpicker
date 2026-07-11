from openai import OpenAI

from app.config import OPENAI_API_KEY

from app.daily.prompts import (
    SYSTEM_PROMPT,
    build_prompt,
)

import json


class DailyLLM:

    def __init__(self):

       self.client = OpenAI(

            api_key=OPENAI_API_KEY,

        )

    def generate(
        self,
        articles,
    ):

        response = self.client.responses.create(

            model="gpt-5.5",

            input=[

                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },

                {
                    "role": "user",
                    "content": build_prompt(
                        articles,
                    ),
                },

            ],

        )

        return json.loads(
            response.output_text,
        )