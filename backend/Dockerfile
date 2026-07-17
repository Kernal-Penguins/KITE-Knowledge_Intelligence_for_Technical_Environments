# Use Python 3.12 (stable, 3.14 is pre-release and has compatibility issues with many packages)
FROM python:3.12-slim

WORKDIR /app

# System deps for docling (PDF parsing) and Tesseract OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpoppler-cpp-dev \
    poppler-utils \
    tesseract-ocr \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency specs first (enables Docker layer caching — deps only re-install if these change)
COPY pyproject.toml uv.lock ./

# Install dependencies (without application code so this layer is cached)
RUN uv pip install --system --no-cache -r pyproject.toml

# Copy application code (this layer re-builds when code changes, but deps layer stays cached)
COPY app/ ./app/

# Create documents directory
RUN mkdir -p /app/data/documents

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
