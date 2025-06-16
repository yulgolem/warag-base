#!/bin/sh
set -e
MODEL="qwen2.5:7b-instruct-q4_k_m"

# Ensure ollama server is running and model is available
ollama pull "$MODEL"
exec ollama serve --host 0.0.0.0 --context-size 32768
