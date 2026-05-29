FROM python:3.12-slim

WORKDIR /app/backend

# System deps for pandas/openpyxl
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && \
    rm -rf /var/lib/apt/lists/*

# Install Python deps (pyproject.toml)
COPY backend/pyproject.toml ./pyproject.toml
RUN pip install --no-cache-dir .

# Copy application code
COPY backend/app/ ./app/
COPY backend/data/ ./data/

# Non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
