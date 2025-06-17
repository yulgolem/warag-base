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
COPY pip.conf /etc/pip.conf
RUN pip install --no-cache-dir --root-user-action=ignore \
    --disable-pip-version-check -r requirements.txt

# Copy runtime helper script for Ollama
COPY entrypoint_ollama.sh /usr/local/bin/entrypoint_ollama.sh
RUN chmod +x /usr/local/bin/entrypoint_ollama.sh

# Set work directory
WORKDIR /app

# Copy source
COPY . /app
# Include WBA sample verification documents
COPY docs/wba_samples /app/docs/wba_samples
ENV WBA_DOCS=/app/docs/wba_samples

# Default command
EXPOSE 5000
CMD ["python", "-m", "writeragents.web.app"]
