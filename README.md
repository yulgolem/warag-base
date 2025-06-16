# WriterAgents

WriterAgents orchestrates multiple specialized agents to collaboratively craft stories and documentation. This project began as a command-line interface and is evolving toward a Web-based UI for richer interactions.

After installation you can invoke the CLI from any directory using::

    python -m writeragents

New commands include::

    python -m writeragents load path/to/mds
    python -m writeragents search "query" --mode semantic
    python -m writeragents wba-menu

The ``wba-menu`` command launches an interactive prompt for loading markdown
files into the archive, searching existing entries, and viewing statistics.
Selecting option ``1`` now automatically loads the bundled sample documents from
``docs/wba_samples`` (or the directory specified by the ``WBA_DOCS``
environment variable). Option ``5`` clears the RAG store so you can start fresh.

When using Docker Compose you can run menu commands from the host with::

    docker compose run --rm app python -m writeragents wba-menu

If the services are already running, use ``docker compose exec app`` instead of ``run``.

To start the Web UI from your host, publish port ``5000`` and run::

    docker compose run --rm -p 5000:5000 app python -m writeragents.web.app

Again, replace ``run`` with ``exec`` if the container is already running.
Then open `http://localhost:5000` in your browser to access the chat interface.
View the chat logs with ``docker compose logs -f app``.

## Status

Phase 1 is complete. The project currently provides the CLI utilities and
configuration management. A lightweight Web chat interface is also included as
the starting point for phase 2.
Run the CLI as shown above. It loads `writeragents/config/local.yaml` by
default. Use `--config` or the `WRITERAG_CONFIG` environment variable to select
a different YAML configuration file, such as `writeragents/config/remote.yaml`.

## Architecture

The system is composed of the following agents:

- **World Building Archivist (WBA)** – Maintains a persistent archive of the fictional world's details.
- **Consistency Checker** – Ensures plot points and facts remain logically consistent.
- **Creativity Assistant** – Offers stylistic suggestions and brainstorms new ideas.
- **RAG Search Agent** – Performs retrieval-augmented generation to gather supporting information.
- **Writer Agent** – Coordinates the workflow and produces final output for the user.

Agents communicate through short-term and long-term storage mechanisms. The CLI acts as the main control surface, with plans to extend functionality through a Web UI in upcoming versions.

## Language Support

The project currently relies on the **FRIDA** model for generating text embeddings in Russian. These embeddings power search and retrieval operations across the agents.

## Roadmap

1. Finalize CLI utilities and configuration management.
2. Introduce a simple Web UI that mirrors CLI features. Launch it with::

       python -m writeragents.web.app

   This opens a minimal chat page at `http://localhost:5000`.
3. Iterate on agent interactions and expand storage options.
4. Add an [orchestrator](docs/orchestrator.md) to direct all agents.
5. Expand the WBA with [self-organizing classification](docs/wba_classification.md).
6. Incorporate a robust [consistency checker](docs/consistency_checker.md).
7. Build a [story-structure analysis](docs/story_structure.md) module.

Additional documentation is available in the [docs/](docs/) directory.

## Makefile Commands

Common development tasks can be run via the provided `Makefile`:

- `make build` – Build the Docker image defined by `Dockerfile`.
- `make up` – Launch services with Docker Compose.
- `make test` – Execute the test suite inside the `app` container.
- `make down` – Stop and remove the Compose services.

You can also start the full stack manually::

    docker compose up
