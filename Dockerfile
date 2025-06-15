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
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the Qwen model for local serving
RUN ollama serve >/tmp/ollama.log 2>&1 & \
    pid=$! && \
    sleep 5 && \
    ollama pull qwen2.5:7b-instruct-q4_k_m && \
    kill $pid

# Set work directory
WORKDIR /app

# Copy source
COPY . /app
# Include WBA sample verification documents
COPY docs/wba_samples /app/docs/wba_samples
ENV WBA_DOCS=/app/docs/wba_samples

# Default command
CMD ["python", "-m", "writeragents"]
