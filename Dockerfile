FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Update system and install dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install wheel
RUN pip install --no-cache-dir --upgrade \
    pip==25.1.1 \
    setuptools==68.2.2 \
    wheel==0.41.2

# Copy requirements first (better caching)
COPY requirements.txt .

# Install Python dependencies with increased timeout and retries
RUN pip install -v --no-cache-dir \
    --timeout=300 \
    --retries=5 \
    --index-url=https://pypi.org/simple/ \
    -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY tests/ ./tests/
COPY scripts/ ./scripts/

# Create logs directory
RUN mkdir -p logs

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Set PYTHONPATH to include src directory
ENV PYTHONPATH=/app

# Run Streamlit
CMD ["streamlit", "run", "src/main.py", "--server.address=0.0.0.0", "--server.port=8501"]
