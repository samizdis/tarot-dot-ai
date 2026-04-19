from pydantic import BaseModel


class Card(BaseModel):
    id: str
    name: str
    arcana: str  # "major" | "minor"
    suit: str | None = None  # wands/cups/swords/pentacles or None for major
    number: int
    keywords_upright: list[str]
    keywords_reversed: list[str]
    short_upright: str
    short_reversed: str


POSITIONS = ["Past", "Present", "Future"]


class DrawnCard(BaseModel):
    card: Card
    position: str
    reversed: bool


class DrawResponse(BaseModel):
    draw_id: str
    cards: list[DrawnCard]
