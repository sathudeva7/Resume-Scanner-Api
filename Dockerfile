FROM python:3.11-slim

# --- Environment ---
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8080 \
    WORKERS=4

# --- System deps (runtime only) ---
# libmagic1: for python-magic; curl: for HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends \
      libmagic1 \
      curl \
    && rm -rf /var/lib/apt/lists/*

# --- App setup ---
WORKDIR /app

# Cache-friendly: install Python deps first
COPY requirements-minimal.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements-minimal.txt

# Copy code
COPY app/ ./app/
# Optional: bring in an example env file (avoid baking real secrets into images)
COPY env.example .env

# Data dirs (e.g., uploads) with safe perms
RUN mkdir -p /app/uploads

# Non-root user
RUN adduser --disabled-password --gecos '' appuser \
 && chown -R appuser:appuser /app
USER appuser

# --- Networking ---
EXPOSE 8080

# --- Healthcheck ---
# Uses $PORT so it works if you override the port at runtime
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -fsS "http://127.0.0.1:${PORT}/health" || exit 1

# --- Run (Gunicorn with Uvicorn workers) ---
# Use shell form so env vars like ${PORT} expand.
CMD sh -c 'uvicorn app.main:app --host 0.0.0.0 --port ${PORT}'-b 0.0.0.0:${PORT} app.main:app'
