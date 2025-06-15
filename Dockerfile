# Use official Python 3.11 image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl && \
    rm -rf /var/lib/apt/lists/* && \
    curl -fsSL https://ollama.com/install.sh | sh

# Install Python dependencies
RUN pip install --no-cache-dir redis psycopg2-binary

# Pre-download the Qwen model for local serving
RUN ollama pull qwen2.5:7b-instruct-q4_k_m

# Set work directory
WORKDIR /app

# Copy source
COPY . /app

# Default command
CMD ["python", "cli/__init__.py"]
