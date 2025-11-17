# apps/api/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy các thư mục từ thư mục gốc của project
COPY ./apps ./apps
COPY ./apps/backend/requirements.txt ./requirements.txt

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app


# Cài g++/libpq để build/psycopg2 (slim cần libpq-dev)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev curl ffmpeg && \
    rm -rf /var/lib/apt/lists/*

COPY . .

EXPOSE 8000
# Uvicorn chạy FastAPI
CMD ["uvicorn","apps.backend.main:app","--host","0.0.0.0","--port","8000"]