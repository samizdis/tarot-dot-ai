import json
import os
from collections.abc import AsyncIterator

from anthropic import AsyncAnthropic

from app.models import DrawnCard

_client: AsyncAnthropic | None = None


def get_client() -> AsyncAnthropic:
    global _client
    if _client is None:
        _client = AsyncAnthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _client


SYSTEM_PROMPT = """\
You are a thoughtful tarot reader. Your role is reflective, not predictive — \
you treat the cards as a mirror that helps the querent see their situation \
from a new angle, never as fortune-telling.

Voice: warm, grounded, observant. Avoid mystical filler ("the universe is \
guiding you"); favour concrete, sensory language. Use "you" naturally without \
being preachy.\
"""


SECTIONS = ("past", "present", "future", "synthesis")
_SECTION_INDEX = {"past": 0, "present": 1, "future": 2}


def _card_payload(dc: DrawnCard) -> dict:
    return {
        "position": dc.position,
        "card": dc.card.name,
        "orientation": "reversed" if dc.reversed else "upright",
        "keywords": (
            dc.card.keywords_reversed if dc.reversed else dc.card.keywords_upright
        ),
        "short_meaning": (
            dc.card.short_reversed if dc.reversed else dc.card.short_upright
        ),
    }


def build_section_prompt(draw: list[DrawnCard], section: str) -> str:
    if section == "synthesis":
        payload = [_card_payload(dc) for dc in draw]
        return (
            "Here is the full 3-card spread (Past / Present / Future):\n\n"
            f"```json\n{json.dumps(payload, indent=2)}\n```\n\n"
            "Write ONLY the Synthesis section, starting with exactly this heading:\n\n"
            "## Synthesis\n\n"
            "Follow it with 1–2 short paragraphs on how the three cards interact as a "
            "story — the arc from past to present to future, and what the whole spread "
            "is pointing at. Do not include any other section headings."
        )

    if section not in _SECTION_INDEX:
        raise ValueError(f"unknown section: {section}")

    dc = draw[_SECTION_INDEX[section]]
    heading = f"## {dc.position} — {dc.card.name}"
    if dc.reversed:
        heading += " (Reversed)"

    return (
        f"Here is the {dc.position} card in a 3-card spread:\n\n"
        f"```json\n{json.dumps(_card_payload(dc), indent=2)}\n```\n\n"
        f"Write ONLY this section, starting with exactly this heading:\n\n"
        f"{heading}\n\n"
        f"Follow it with 2–3 short paragraphs that integrate the card's "
        f"traditional meaning, its {dc.position} position, and its orientation. "
        f"Do not include any other section headings, and do not write a synthesis."
    )


async def stream_reading(draw: list[DrawnCard], section: str) -> AsyncIterator[str]:
    client = get_client()
    model = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")
    async with client.messages.stream(
        model=model,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_section_prompt(draw, section)}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
