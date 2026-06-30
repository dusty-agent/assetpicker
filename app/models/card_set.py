from pydantic import BaseModel

from .card import Card
from .story import Story


class CardSet(BaseModel):

    title: str

    story: Story

    cards: list[Card]