from pydantic import BaseModel

class Card(BaseModel):
    title: str
    body: str