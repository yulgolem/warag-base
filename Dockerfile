FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Pull the Ollama model using BuildKit cache
RUN --mount=type=cache,target=/root/.ollama \
    ollama serve >/tmp/ollama.log 2>&1 & \
    pid=$! && sleep 5 && ollama pull qwen2.5:7b-instruct && \
    kill -SIGINT $pid && wait $pid

CMD ["python", "-m", "http.server"]
