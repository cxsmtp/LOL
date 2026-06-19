# Troubleshooting

- Podman machine not running: start Podman Desktop or run `podman machine start`, then run `scripts/start.ps1` again.
- Ollama not in PATH: reinstall Ollama or add its install directory to PATH; verify with `ollama --version`.
- localhost not reachable: check Windows Firewall and whether ports 11434 and 3000 are in use.
- Model too slow: switch to a smaller model in `config/models.yaml` and run `scripts/pull-model.ps1 -ModelName <name>`.
- Out of memory: close other applications, use 3B/mini models, or reduce document batch size.
- PDF parsing failure: try OCR/export to text, or install/update `pypdf`.
- Permission issues: run PowerShell from the project folder as your normal user; avoid protected directories.
