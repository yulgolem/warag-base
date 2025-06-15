# Docker Setup

The repository includes a `Dockerfile` and `docker-compose.yml` for building and running WriterAgents with its service dependencies.

## Build the Image

From the repository root run:

```bash
docker build -t writeragents .
```

This creates an image with Python 3.11, Redis and PostgreSQL client libraries pre-installed.
It also copies example WBA verification documents to `/app/docs/wba_samples` in
the container. The `WBA_DOCS` environment variable points to this directory for
easy reference.

## Run with Docker Compose

Use `docker compose` to start PostgreSQL, Redis and the application container:

```bash
docker compose up
```

The application mounts the project directory for live editing. PostgreSQL data is persisted in the `pgdata` volume.

Stop the services with `Ctrl+C` and remove containers using:

```bash
docker compose down
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
build step. The Dockerfile briefly launches `ollama serve` so that `ollama pull`
can fetch the model. On first run the `ollama` service starts the model server
with a 32K context window:

```bash
ollama serve --host 0.0.0.0 --context-size 32768
```

The downloaded model data is stored in the `ollama` Docker volume so repeated
runs do not trigger new downloads.

## Running Tests

The compose setup provides PostgreSQL and Redis with the same environment
variables used in the default configuration. To execute the test suite
against these services run:

```bash
docker compose run --rm app pytest
```

This command launches the application container, connects to the
containerized database and Redis instances, and then invokes `pytest`.

## Running CLI Commands

To invoke the interactive menu or other `writeragents` subcommands from your
host machine, prefix the command with `docker compose run --rm app`. For
example:

```bash
docker compose run --rm app python -m writeragents wba-menu
```

If the stack is already running with `docker compose up`, swap `run` for
`exec`:

```bash
docker compose exec app python -m writeragents wba-menu
```

The menu loads the example Markdown files from `/app/docs/wba_samples` when you
choose option 1. Option 5 clears the archive so you can experiment repeatedly.

