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

Launch the application with the ``writeragents`` command. Pass a configuration
file using ``--config`` or set ``WRITERAGENTS_CONFIG`` in the environment.
This flag controls which of the modes below is active.

