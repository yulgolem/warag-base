# WriterAgents Overview

WriterAgents is a modular system for orchestrating multiple agents that collaboratively produce coherent written works. Each agent fulfills a specialized role and communicates via a shared memory layer. The system currently focuses on a command-line interface with plans to evolve into a more interactive Web UI.

## High-Level Architecture

```
CLI / Web UI
    |
    v
Storage Layer (Short- & Long-Term Memory)
    |
    v
Agents (WBA, Consistency Checker, Creativity Assistant, RAG Search, Writer Agent)
```

- **Command Interface**: Users initiate and control runs through the CLI, which will later expand into a Web interface.
- **Storage Layer**: Provides short-term memory via Redis and long-term memory via SQLite or PostgreSQL.
- **Agents**: Each agent performs a discrete task in the writing workflow, ensuring consistent world-building, factual continuity, and stylistic creativity.

## Embedding Model

WriterAgents uses the **FRIDA** model to create Russian embeddings for archived text. These embeddings enable agents to perform retrieval-augmented generation. See [embedding_models.md](embedding_models.md) for more details.

