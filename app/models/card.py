from pydantic import BaseModel

from app.models.card_type import CardType


class Card(BaseModel):

    type: CardType

    title: str

    body: str

    subtitle: str | None = None

    footer: str | None = None

    icon: str | None = None

    image: str | None = None