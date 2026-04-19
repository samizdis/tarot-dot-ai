import json
import random
from pathlib import Path

from app.models import Card, DrawnCard, POSITIONS

_CARDS_DIR = Path(__file__).parent.parent / "data" / "cards"
_CACHE: list[Card] | None = None


def load_deck() -> list[Card]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    cards: list[Card] = []
    for path in sorted(_CARDS_DIR.glob("*.json")):
        with path.open() as f:
            for raw in json.load(f):
                cards.append(Card.model_validate(raw))
    if len(cards) != 78:
        raise RuntimeError(f"Expected 78 cards, loaded {len(cards)}")
    _CACHE = cards
    return cards


def draw_three(rng: random.Random | None = None) -> list[DrawnCard]:
    rng = rng or random.Random()
    deck = load_deck()
    picks = rng.sample(deck, 3)
    return [
        DrawnCard(card=card, position=pos, reversed=rng.random() < 0.5)
        for card, pos in zip(picks, POSITIONS)
    ]
