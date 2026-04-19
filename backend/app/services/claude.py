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
being preachy.

Always structure your response with these exact markdown headings, in order:
## Past — {card name}{ (Reversed) if reversed}
## Present — {card name}{ (Reversed) if reversed}
## Future — {card name}{ (Reversed) if reversed}
## Synthesis

Each card section is 2–3 short paragraphs that integrate (a) the card's \
traditional meaning, (b) its spread position, and (c) its orientation. The \
synthesis is 1–2 paragraphs on how the three cards interact as a story.\
"""


def _format_draw(draw: list[DrawnCard]) -> str:
    payload = [
        {
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
        for dc in draw
    ]
    return json.dumps(payload, indent=2)


def build_user_prompt(draw: list[DrawnCard]) -> str:
    return (
        "Here is the spread (3-card Past / Present / Future):\n\n"
        f"```json\n{_format_draw(draw)}\n```\n\n"
        "Give the reading using the heading structure from the system prompt. "
        "Reference the orientation and the position naturally — don't just "
        "restate the keywords. End with the Synthesis section."
    )


async def stream_reading(draw: list[DrawnCard]) -> AsyncIterator[str]:
    client = get_client()
    model = os.getenv("CLAUDE_MODEL", "claude-opus-4-7")
    async with client.messages.stream(
        model=model,
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_user_prompt(draw)}],
    ) as stream:
        async for text in stream.text_stream:
            yield text
