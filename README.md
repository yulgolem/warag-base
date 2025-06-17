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

To launch the Web UI simply run::

    docker compose up -d

Then open `http://localhost:5000` in your browser to access the chat interface.
The page provides **Load samples** and **Clear store** buttons. Clicking
``Load samples`` sends a request to ``/load-samples`` which imports the
verification markdown files from the directory specified by the ``WBA_DOCS``
environment variable (default ``/app/docs/wba_samples``). The server responds
with ``{"message": "Loaded"}`` and the text appears in the chat log.

``Clear store`` issues ``/clear-store`` to wipe the archive. A response of
``{"message": "Cleared"}`` confirms success.

View the chat logs with ``docker compose logs -f app``.
Additional container setup details are documented in
[docs/docker_setup.md](docs/docker_setup.md).

## Status

Phase 1 is complete. The project currently provides the CLI utilities and
configuration management. A lightweight Web chat interface is also included as
the starting point for phase 2.
Run the CLI as shown above. It loads `writeragents/config/local.yaml` by
default. Use `--config` or the `WRITERAG_CONFIG` environment variable to select
a different YAML configuration file, such as `writeragents/config/remote.yaml`.
The configuration also lets you define custom story templates under the
`story_structure` section. See [docs/story_structure.md](docs/story_structure.md)
for details.

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

The complete development plan lives in [docs/roadmap.md](docs/roadmap.md).
Current progress is tracked in [docs/progress.md](docs/progress.md).

Launch the minimal Web UI locally with::

    python -m writeragents.web.app

Or run ``docker compose up -d`` to start it in a container. Both open a chat
page at `http://localhost:5000`.

Additional documentation is available in the [docs/](docs/) directory,
including the current [progress report](docs/progress.md).

## Makefile Commands

Common development tasks can be run via the provided `Makefile`:

- `make build` – Build the Docker image defined by `Dockerfile`.
- `make up` – Launch services with Docker Compose.
- `make test` – Execute the test suite inside the `app` container.
- `make down` – Stop and remove the Compose services.

You can also start the full stack manually::

    docker compose up

## Running Tests Locally

Install dependencies from PyPI and enable editable mode::

    pip install -r requirements.txt
    pip install -e .[dev]

Then execute `pytest` from the project root:

    pytest -q

All tests should pass without additional configuration.
