# Architecture

Local AI Workbench uses Ollama for local models, Open WebUI for browser chat, and Python utilities for local RAG, analysis, and presentation drafting.

```text
User -> Open WebUI -> Ollama
User -> Python scripts -> local data folders -> local vector_store -> Ollama
```

Work and personal data are separated by directory and by required `--scope` arguments. No cloud service is configured by default.


## Container runtime

Open WebUI is started with Podman. On Windows, Podman Desktop should provide `podman` and `host.containers.internal` so the container can reach Ollama on the host at port 11434.

## Mobile testing helper

`app/mobile_app_review.py` performs local static review of APK and IPA archives and writes reports to `mobile/reports`. It is intended as an authorized testing aid, not a replacement for device-based dynamic testing.
