# ---- Stage 1: build the React dashboard ----
FROM node:22-alpine AS frontend-build
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# ---- Stage 2: Python runtime ----
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY config.py app.py agent.py ./
COPY scripts/ scripts/
COPY --from=frontend-build /frontend/dist frontend/dist

# Run as an unprivileged user
RUN useradd --create-home --uid 10001 appuser && mkdir -p logs && chown -R appuser /app
USER appuser

EXPOSE 5002
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5002/api/health', timeout=2)"

# Single worker: metrics history lives in process memory. Threads handle concurrency.
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "--workers", "1", "--threads", "4", "app:app"]
