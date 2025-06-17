# Agent Flow Design

This document summarizes the planned interaction model for WriterAgents.
It is based on the architectural analysis from the discussion about roadmap
item **1.1 Agent flow decisions**.

## Coordinator (Orchestrator)
The orchestrator receives requests from the CLI or web UI, parses the
intent, and invokes the appropriate agent. Conversation logs and recent
context are stored in Redis.

## Memory and Retrieval
- **Short-term memory**: Redis stores the current dialogue and partial
  results.
- **Long-term memory**: SQLite or PostgreSQL archives texts with
  embeddings, enabling semantic search.
- **RAGEmbeddingStore**: provides similarity search to fetch relevant
  passages when the context exceeds the 32k token limit of the LLM.

## Execution Flow
1. **Pipeline**: complex tasks can chain agents in a fixed order,
   for example `WriterAgent -> ConsistencyChecker -> CreativityAssistant`.
2. **Self-Critique Loop**: the writer agent may repeatedly call the
   consistency checker (and optionally the creativity assistant) until
   the output meets quality standards.
3. **Sliding Context Window**: long inputs are broken into segments, with
   summaries stored in memory so agents can work within the context limit.

## Hardware Limitations
The target machine uses a 4 GB VRAM GPU and 32 GB of RAM. Running a
quantized model such as `qwen2.5:7b-instruct-q4_k_m` keeps GPU memory
usage manageable. Embedding operations are batch processed to avoid
excessive RAM consumption.

