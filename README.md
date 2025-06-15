# WriterAgents

WriterAgents orchestrates multiple specialized agents to collaboratively craft stories and documentation. This project began as a command-line interface and is evolving toward a Web-based UI for richer interactions.

## Architecture

The system is composed of the following agents:

- **World Building Archivist (WBA)** – Maintains a persistent archive of the fictional world's details.
- **Consistency Checker** – Ensures plot points and facts remain logically consistent.
- **Creativity Assistant** – Offers stylistic suggestions and brainstorms new ideas.
- **RAG Search Agent** – Performs retrieval-augmented generation to gather supporting information.
- **Writer Agent** – Coordinates the workflow and produces final output for the user.

Agents communicate through short-term and long-term storage mechanisms. The CLI acts as the main control surface, with plans to extend functionality through a Web UI in upcoming versions.

## Command Line Usage

Run the project with the ``writeragents`` command. By default the CLI loads
``config/local.yaml`` but this can be overridden either with ``--config`` or via
environment variables.

```bash
# explicit config path
writeragents --config config/remote.yaml

# using environment variables
WRITERAGENTS_CONFIG=config/remote.yaml DATABASE_URL=postgresql://user:pass@host/db \
REDIS_HOST=redis.example.com writeragents
```

Environment variables provide a convenient way to change the database and Redis
connection details without editing configuration files:

- ``WRITERAGENTS_CONFIG`` – default configuration file path when ``--config`` is
  omitted.
- ``DATABASE_URL`` – overrides ``storage.database_url`` from the YAML file.
- ``REDIS_HOST`` – overrides ``storage.redis_host`` from the YAML file.

## Roadmap

1. Finalize CLI utilities and configuration management.
2. Introduce a simple Web UI that mirrors CLI features.
3. Iterate on agent interactions and expand storage options.

## Roadmap Progress

Phase 1 (CLI and configuration management) is complete. Development is now
focused on the initial Web UI and deeper agent coordination.

Additional documentation is available in the [docs/](docs/) directory.

## Makefile Commands

Common development tasks can be run via the provided `Makefile`:

- `make build` – Build the Docker image defined by `Dockerfile`.
- `make up` – Launch services with Docker Compose.
- `make test` – Execute the test suite inside the `app` container.
- `make down` – Stop and remove the Compose services.
