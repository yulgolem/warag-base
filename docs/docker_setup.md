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
