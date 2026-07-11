from typing import Any

from app.daily.models import NewsCard
from app.daily.pipeline import DailyPipeline
from app.daily.prompts import (
    SYSTEM_PROMPT,
    build_prompt,
)
from app.llm.client import LLMClient


class DailyGenerator:

    def __init__(self):

        self.llm = LLMClient()

        self.pipeline = DailyPipeline()

    def generate(

        self,

        cards: list[NewsCard],

    ) -> dict[str, Any]:

        result = self.llm.generate(

            system_prompt=SYSTEM_PROMPT,

            user_prompt=build_prompt(
                cards,
            ),

        )

        if "cards" not in result:

            raise RuntimeError(
                "LLM 응답에 cards가 없습니다."
            )

        if not result["cards"]:

            raise RuntimeError(
                "LLM이 카드를 생성하지 않았습니다."
            )

        return self.pipeline.build(
            result,
        )