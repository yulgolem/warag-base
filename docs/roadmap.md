# Development Roadmap

This roadmap outlines upcoming milestones for WriterAgents as it evolves from a collection of command-line tools into a fully orchestrated web-based system.

## 1. Model Integration
- Implement calls to language models using the endpoints defined in the YAML configuration (e.g. `remote.yaml`).
- Support both local servers like Ollama and remote API services.
- Replace the placeholder responses in `WriterAgent` and other modules with actual model-generated text.

## 1.1 Agent flow decisions
- Choose from different agent flow strategies such as pipelineg agents, sliding context window, Memory-Enhanced Agents, Coordinator + Workers, Self-Critique Loop and others based on hardware limitations (Lenovo P1 Gen2 32 GB Ram Nvidia Quaddro 1000)

## 2. Agent Logic
- Finish the implementations of `CreativityAssistant`, `RAGSearchAgent`, and `WorldBuildingArchivist.run`.
- Enhance the `ConsistencyChecker` and `StoryStructureAnalyst` with deeper analyses and metrics.

## 3. Memory Layers
- Complete `DatabaseMemory` and `RedisMemory` to provide long-term and short-term storage.
- Abstract the storage backend so it can be swapped via configuration.

## 4. Orchestrator
- Preserve conversation context in memory.
- Decide which agent to invoke based on the dialogue history.
- Allow enabling and configuring agents through YAML settings.

## 5. Dynamic Story Structures
- Extend the story-structure analyst to load narrative templates from configuration instead of a fixed three-act scheme.
- Let users define their own plot structures and switch between them dynamically.

## 6. Configuration Cleanup
- Move hard-coded thresholds, limits, and defaults into the YAML files.
- Expose options in the Web UI to select modes (local vs networked) and tweak agent parameters.

## 7. Tests and Documentation
- Add test coverage for model integration and storage layers.
- Document setup for Docker and configuration of custom story structures.

This plan will lead to a more flexible system where key behaviours—such as which plot templates to apply—can be changed without modifying the codebase.
