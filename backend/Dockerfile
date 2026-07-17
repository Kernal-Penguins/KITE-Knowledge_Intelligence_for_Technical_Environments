FROM python:3.14-slim

WORKDIR /app

# System deps for docling (PDF parsing) and sentence-transformers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpoppler-cpp-dev \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency spec first (layer caching)
COPY pyproject.toml .

# Install dependencies
RUN uv pip install --system --no-cache -e .

# Copy application code
COPY . .

# Create documents directory
RUN mkdir -p /app/data/documents

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
