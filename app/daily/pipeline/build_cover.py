from app.llm.client import LLMClient

from app.daily.prompts import (
    SYSTEM_PROMPT,
    build_prompt,
)

from app.daily.pipeline.build_cover import build_cover
from app.daily.pipeline.build_issue import build_issue
from app.daily.pipeline.build_summary import build_summary
from app.daily.pipeline.build_insight import build_insight
from app.daily.pipeline.build_introduction import build_introduction
from app.daily.pipeline.build_ending import build_ending


class DailyGenerator:

    def __init__(self):

        self.llm = LLMClient()

    def generate(self, cards):

        result = self.llm.generate(

            system_prompt=SYSTEM_PROMPT,

            user_prompt=build_prompt(cards),

        )

        return {
            "cover": build_cover(result),
            "introduction": build_introduction(result),
            "issue": build_issue(result),
            "summary": build_summary(result),
            "insight": build_insight(result),
            "ending": build_ending(result),
        }