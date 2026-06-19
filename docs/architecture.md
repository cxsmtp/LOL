# Architecture

Local AI Workbench uses Ollama for local models, Open WebUI for browser chat, and Python utilities for local RAG, analysis, and presentation drafting.

```text
User -> Open WebUI -> Ollama
User -> Python scripts -> local data folders -> local vector_store -> Ollama
```

Work and personal data are separated by directory and by required `--scope` arguments. No cloud service is configured by default.
