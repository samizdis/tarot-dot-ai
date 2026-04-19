# tarot-dot-ai

A mini tarot reading app powered by Claude. Draw three cards, flip them one by one, and get an AI-generated reading.

## Dev setup

### Prerequisites
- Python 3.11+
- Node 20+
- An Anthropic API key

### Backend
```bash
cd backend
cp ../.env.example .env   # fill in ANTHROPIC_API_KEY
pip install -e ".[dev]"
uvicorn app.main:app --reload
```
API runs on http://localhost:8000. Interactive docs at http://localhost:8000/docs.

### Frontend
```bash
cd frontend
npm install
npm run dev
```
App runs on http://localhost:5173 (proxies /api/* to :8000).

## Deploy (Koyeb)

Build and push the multi-stage Docker image, or connect the repo directly in the Koyeb dashboard. Set `ANTHROPIC_API_KEY` as a secret in the service settings.

```bash
docker build -t tarot-dot-ai .
```

## Project structure
```
backend/app/
  main.py          # FastAPI app entry point
  models.py        # Pydantic models
  routes/          # draw.py, reading.py
  services/        # deck.py, claude.py
  data/tarot.json  # 78-card RWS dataset

frontend/src/
  components/      # SpreadBoard, TarotCard, Reading
  lib/api.ts       # fetch helpers
```
