from pydantic import BaseModel
from .card import Card

class Report(BaseModel):
    title: str
    cards: list[Card]