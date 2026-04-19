import uuid

from fastapi import APIRouter

from app.models import DrawResponse, DrawnCard
from app.services.deck import draw_three

router = APIRouter()

# In-memory draw cache so /reading can replay the draw by id.
_DRAWS: dict[str, list[DrawnCard]] = {}


def get_draw(draw_id: str) -> list[DrawnCard] | None:
    return _DRAWS.get(draw_id)


@router.post("/draw", response_model=DrawResponse)
async def post_draw() -> DrawResponse:
    cards = draw_three()
    draw_id = uuid.uuid4().hex
    _DRAWS[draw_id] = cards
    return DrawResponse(draw_id=draw_id, cards=cards)
