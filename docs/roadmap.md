# Development Roadmap

This roadmap outlines upcoming milestones for WriterAgents as it evolves from a collection of command-line tools into a fully orchestrated web-based system.

## Summary

- [x] Finalize CLI utilities and configuration management.
- [x] Introduce a simple Web UI for chat interactions.
- [x] Implement model integration with local and remote endpoints.
- [x] Complete agent logic and expand storage options.
- [x] Add an orchestrator to direct agents and review the [agent_flow](agent_flow.md).
- [x] Expand the World Building Archivist with self-organizing classification.
- [x] Incorporate a consistency checker and story-structure analysis module.
- [x] Implement dynamic story structures and clean up configuration.
- [x] Provide thorough tests and documentation.

The sections below describe each area in more detail.
## 1. Model Integration
- [x] Implement calls to language models using the endpoints defined in the YAML configuration (e.g. `remote.yaml`).
- [x] Support both local servers like Ollama and remote API services.
- [x] Replace the placeholder responses in `WriterAgent` and other modules with actual model-generated text.

## 1.1 Agent flow decisions
The agent interactions combine several patterns: pipeline processing, a self-critique loop and a sliding context window. They are coordinated by the orchestrator and respect the limitations of a Lenovo P1 Gen2 laptop with 32 GB RAM and a Quadro 1000 GPU. See [agent_flow.md](agent_flow.md) for the detailed flow description.

## 2. Agent Logic
- [x] Finish the implementations of `CreativityAssistant`, `RAGSearchAgent`, and `WorldBuildingArchivist.run`.
- [x] Enhance the `ConsistencyChecker` and `StoryStructureAnalyst` with deeper analyses and metrics.

## 3. Memory Layers
- [x] Complete `DatabaseMemory` and `RedisMemory` to provide long-term and short-term storage.
- [x] Abstract the storage backend so it can be swapped via configuration.

## 4. Orchestrator
- [x] Preserve conversation context in memory.
- [x] Decide which agent to invoke based on the dialogue history.
- [x] Allow enabling and configuring agents through YAML settings.

## 5. Dynamic Story Structures
- [x] Extend the story-structure analyst to load narrative templates from configuration instead of a fixed three-act scheme.
- [x] Let users define their own plot structures and switch between them dynamically.

## 6. Configuration Cleanup
- [x] Move hard-coded thresholds, limits, and defaults into the YAML files.
- [x] Expose options in the Web UI to select modes (local vs networked) and tweak agent parameters.

## 7. Tests and Documentation
- [x] Add test coverage for model integration and storage layers.
- [x] Document setup for Docker and configuration of custom story structures.

This plan will lead to a more flexible system where key behaviours—such as which plot templates to apply—can be changed without modifying the codebase.
