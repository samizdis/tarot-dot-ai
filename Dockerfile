# --- Stage 1: build the Vue frontend ---
FROM node:20-alpine AS frontend
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Stage 2: Python backend serving the built frontend ---
FROM python:3.12-slim AS backend
WORKDIR /app

COPY backend/pyproject.toml ./backend/
RUN pip install --no-cache-dir -e ./backend

COPY backend/ ./backend/
COPY --from=frontend /app/dist ./frontend/dist

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
WORKDIR /app/backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
