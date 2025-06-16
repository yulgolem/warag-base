# warag-base

This repository demonstrates caching Ollama models during Docker builds.

The Dockerfile uses BuildKit's `--mount=type=cache` feature to store the model
files in `/root/.ollama`. Enable BuildKit when building to avoid repeatedly
pulling the model:

```bash
DOCKER_BUILDKIT=1 docker build -t myapp .
```
