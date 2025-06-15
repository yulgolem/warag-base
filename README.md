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

## Roadmap

1. Finalize CLI utilities and configuration management.
2. Introduce a simple Web UI that mirrors CLI features.
3. Iterate on agent interactions and expand storage options.

Additional documentation is available in the [docs/](docs/) directory.
