param([switch]$NoWebUI)
$ErrorActionPreference = "Stop"
Write-Host "Starting Local AI Workbench..."
if (Get-Command ollama -ErrorAction SilentlyContinue) { Start-Process -WindowStyle Hidden ollama "serve" -ErrorAction SilentlyContinue; Start-Sleep 2 } else { Write-Warning "Ollama not found. Install it from https://ollama.com/download" }
if (-not $NoWebUI) {
  if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker run -d --name open-webui --restart unless-stopped -p 3000:8080 -e OLLAMA_BASE_URL=http://host.docker.internal:11434 -v open-webui:/app/backend/data ghcr.io/open-webui/open-webui:main 2>$null || docker start open-webui
  } else { Write-Warning "Docker not found; skipping Open WebUI." }
}
Write-Host "Open WebUI: http://localhost:3000  Ollama: http://localhost:11434"
