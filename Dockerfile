# Base image: Python 3.11 Slim (Lightweight & Stable)
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1

# Install system dependencies
# - build-essential: for compiling python packages
# - curl: for installing poetry
# - poppler-utils: for pdf2image/fitz functionality if needed
# - libgl1: often needed for opencv or image processing libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    poppler-utils \
    libgl1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="$POETRY_HOME/bin:$PATH"

# Copy dependency files first (for caching)
COPY pyproject.toml poetry.lock ./

# Install Python dependencies (Production only)
RUN poetry install --without dev --no-root

# Copy application code
COPY src ./src
COPY assets ./assets
# Copy documentation for reference (optional)
COPY README.md API_GUIDE.md ./

# Create directories for data persistence
RUN mkdir -p data/uploads chroma_db

# Expose API port
EXPOSE 8000

# Default command: Run Uvicorn server
CMD ["poetry", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
