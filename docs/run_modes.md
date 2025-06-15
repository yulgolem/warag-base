# Running WriterAgents

WriterAgents supports two execution modes: **local** and **networked**.

## Local Mode

- Uses locally hosted language models.
- Recommended for experimentation without external dependencies.
- Configure local endpoints and database paths in `config/local.yaml`.

## Networked Mode

- Connects to remote OpenAPI-compatible LLM services.
- Ideal for leveraging larger hosted models.
- Configure API keys and endpoints in `config/remote.yaml`.

Switch between modes by providing the appropriate configuration file when launching the CLI.

