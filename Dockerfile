# Multi-stage Dockerfile: backend (Python) + frontend (Node → static)

# ─── Stage 1: Frontend Build ───────────────────────────────────────────────
FROM node:20-alpine AS frontend-build

WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --no-audit --prefer-offline

COPY frontend/ .
RUN npm run build

# ─── Stage 2: Backend Runtime ───────────────────────────────────────────────
FROM python:3.11-slim AS backend

WORKDIR /app

# System deps needed by weasyprint + psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libharfbuzz0b \
    libffi-dev \
    libssl-dev \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY backend/pyproject.toml .
RUN pip install --no-cache-dir -e ".[all]" 2>/dev/null || pip install --no-cache-dir \
    fastapi uvicorn[standard] sqlalchemy alembic pydantic pydantic-settings \
    python-multipart aiofiles httpx openai python-dotenv psycopg2-binary \
    markdown weasyprint

# Copy backend source
COPY backend/ ./backend/
COPY --from=frontend-build /app/frontend/dist ./frontend/dist

# Copy submodule if present (optional MiroFish)
COPY .gitmodules ./
RUN mkdir -p mirofish

# Create upload directory
RUN mkdir -p uploads

WORKDIR /app/backend

EXPOSE 8000

CMD ["python", "run.py"]
