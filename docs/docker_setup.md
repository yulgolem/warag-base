# Docker Setup

The repository includes a `Dockerfile` and `docker-compose.yml` for building and running WriterAgents with its service dependencies.

## Build the Image

From the repository root run:

```bash
docker build -t writeragents .
```

This creates an image with Python 3.11, Redis and PostgreSQL client libraries pre-installed.

## Run with Docker Compose

Use `docker-compose` to start PostgreSQL, Redis and the application container:

```bash
docker-compose up
```

The application mounts the project directory for live editing. PostgreSQL data is persisted in the `pgdata` volume.

Stop the services with `Ctrl+C` and remove containers using:

```bash
docker-compose down
```

## GPU Requirements for Ollama

Ollama relies on an NVIDIA GPU with at least 4 GB of VRAM. Make sure the
NVIDIA Container Toolkit is installed so Docker can access the GPU. The
`ollama` service in `docker-compose.yml` requests a GPU device and exposes port
`11434` for API access. Start all services with:

```bash
docker compose up
```

If GPU access fails, verify that you can run `nvidia-smi` inside a container
and that Docker is configured with the `--gpus` flag.

## Model Initialization

The Docker image downloads the `qwen2.5:7b-instruct-q4_k_m` model during the
build step. On first run the `ollama` service starts the model server with a
32K context window:

```bash
ollama serve --host 0.0.0.0 --context-size 32768
```

The downloaded model data is stored in the `ollama` Docker volume so repeated
runs do not trigger new downloads.
