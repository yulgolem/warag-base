# Use official Python 3.11 image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir redis psycopg2-binary

# Set work directory
WORKDIR /app

# Copy source
COPY . /app

# Default command
CMD ["python", "cli/__init__.py"]
