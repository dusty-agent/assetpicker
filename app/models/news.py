from pydantic import BaseModel
from datetime import datetime

class News(BaseModel):

    title: str

    summary: str | None = None

    source: str

    reporter: str | None = None

    url: str

    published_at: datetime

    category: str | None = None

    source_type: str | None = None
    # Official
    # Professional
    # Market Signal
    # Promotion
    # Research

    tags: list[str] = []

    metadata: dict = {}