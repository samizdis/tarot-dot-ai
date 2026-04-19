from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.routes.draw import get_draw
from app.services.claude import stream_reading

router = APIRouter()


@router.get("/reading")
async def get_reading(draw_id: str) -> StreamingResponse:
    draw = get_draw(draw_id)
    if draw is None:
        raise HTTPException(status_code=404, detail="draw not found")

    async def event_source():
        try:
            async for chunk in stream_reading(draw):
                # SSE: one or more `data:` lines, then a blank line.
                # Escape newlines so the message stays on one logical event.
                escaped = chunk.replace("\n", "\\n")
                yield f"event: token\ndata: {escaped}\n\n"
            yield "event: done\ndata: end\n\n"
        except Exception as exc:  # surface errors to the browser cleanly
            yield f"event: error\ndata: {type(exc).__name__}: {exc}\n\n"

    return StreamingResponse(
        event_source(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
