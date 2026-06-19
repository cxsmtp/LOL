param([switch]$SkipPython)
$ErrorActionPreference = "Stop"
Write-Host "Installing Local AI Workbench dependencies..."
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { Write-Warning "Install Ollama manually from https://ollama.com/download, then rerun healthcheck." }
if (-not $SkipPython) { python -m venv .venv; .\.venv\Scripts\python.exe -m pip install --upgrade pip; .\.venv\Scripts\pip.exe install -r requirements.txt }
Write-Host "Install complete. Next: scripts/pull-model.ps1 then scripts/start.ps1"
