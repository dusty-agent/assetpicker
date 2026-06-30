from pydantic import BaseModel

from app.models.news import News


class Story(BaseModel):

     # 원본 기사
    news: News

    # 카드 1
    headline: str

    # 카드 2
    summary: str

    # 카드 3
    why: str

    # 카드 4
    buyer_view: str

    # 카드 5
    assetpicker_view: str

    # 분석 결과
    keywords: list[str] = []

    # 선택사항
    score: float | None = None