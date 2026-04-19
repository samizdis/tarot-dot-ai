from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routes.draw import router as draw_router
from app.routes.reading import router as reading_router

app = FastAPI(title="tarot-dot-ai")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(draw_router, prefix="/api")
app.include_router(reading_router, prefix="/api")

# Serve the built Vue frontend in production
_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="static")
