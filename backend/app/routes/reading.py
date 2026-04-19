import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.routes.draw import get_draw
from app.services.claude import SECTIONS, stream_reading

router = APIRouter()
log = logging.getLogger(__name__)


@router.get("/reading")
async def get_reading(draw_id: str, section: str) -> StreamingResponse:
    if section not in SECTIONS:
        raise HTTPException(status_code=400, detail=f"invalid section: {section}")
    draw = get_draw(draw_id)
    if draw is None:
        raise HTTPException(status_code=404, detail="draw not found")

    async def event_source():
        try:
            async for chunk in stream_reading(draw, section):
                # SSE: one or more `data:` lines, then a blank line.
                # Escape newlines so the message stays on one logical event.
                escaped = chunk.replace("\n", "\\n")
                yield f"event: token\ndata: {escaped}\n\n"
            yield "event: done\ndata: end\n\n"
        except Exception:
            # Log details server-side; send only a generic message to the client
            # so exception text (which could in theory carry secrets) never leaks.
            log.exception("reading stream failed (draw_id=%s section=%s)", draw_id, section)
            yield "event: error\ndata: upstream reading failed\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
