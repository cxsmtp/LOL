# Offline Model Management

Download models only during a controlled setup window. After required models are present, enable zero-egress mode and work offline.

Commands:

```powershell
ollama list
ollama show <model-name>
scripts\pull-model.ps1 -ModelName <model-name> -OverrideZeroEgress
```

`pull-model.ps1` blocks downloads while zero-egress mode is enabled unless you explicitly pass `-OverrideZeroEgress` during a controlled setup window. Model files remain local in Ollama's model storage.
