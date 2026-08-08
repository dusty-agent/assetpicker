from typing import Any

from app.daily.models import NewsCard
from app.daily.builder.cards_builder import DailyCardBuilder
from app.daily.prompts import (
    SYSTEM_PROMPT,
    build_prompt,
)
from app.llm.client import LLMClient


class DailyGenerator:

    def __init__(self):

        self.llm = LLMClient()

        self.builder = DailyCardBuilder()

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

        return self.builder.build(
            result,
        )