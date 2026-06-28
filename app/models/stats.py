from pydantic import BaseModel


class PipelineStats(BaseModel):
    collected: int = 0
    filtered: int = 0
    duplicates: int = 0
    categorized: int = 0