# Kagema-FM backend (FastAPI). Build context is this `backend/` directory.
# Replaces the Emergent-platform base image + external supervisor coupling with a
# portable, self-contained image.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# curl is used by the container healthcheck below.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first so the layer caches across code changes.
# If a dependency has no prebuilt wheel for this platform, add build-essential.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Application code.
COPY . .

EXPOSE 8001

# MONGO_URL and DB_NAME must be supplied at runtime (see .env.example).
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://localhost:8001/api/ || exit 1

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
