from pydantic import BaseModel


class SourceStat(BaseModel):
    source: str
    article_count: int
    average_score: float
    duplicate_count: int


class ReporterStat(BaseModel):
    reporter: str
    article_count: int
    average_score: float


class CategoryStat(BaseModel):
    category: str
    article_count: int
    average_score: float