param([switch]$NoWebUI, [switch]$SkipSecurityChecks)
$ErrorActionPreference = "Stop"
$env:OLLAMA_HOST = "127.0.0.1:11434"
Write-Host "Starting Local AI Workbench in zero-egress mode..."
if (-not $SkipSecurityChecks) {
  python app\security_status.py
  if ($LASTEXITCODE -ne 0) { throw "Zero-egress security checks failed. Refusing to start." }
}
if (Get-Command ollama -ErrorAction SilentlyContinue) { Start-Process -WindowStyle Hidden ollama "serve" -ErrorAction SilentlyContinue; Start-Sleep 2 } else { Write-Warning "Ollama not found. Install it during a controlled setup window." }
if (-not $NoWebUI) {
  if (Get-Command podman -ErrorAction SilentlyContinue) {
    Write-Warning "Zero-egress mode is enabled. Podman image pulls require internet and should be done only during controlled setup."
    podman run -d --name open-webui --replace --restart unless-stopped -p 127.0.0.1:3000:8080 -e OLLAMA_BASE_URL=http://host.containers.internal:11434 -e ENABLE_SIGNUP=false -e ENABLE_OPENAI_API=false -e SCARF_NO_ANALYTICS=true -e DO_NOT_TRACK=true -v open-webui:/app/backend/data ghcr.io/open-webui/open-webui:main 2>$null
    if ($LASTEXITCODE -ne 0) { podman start open-webui }
  } else { Write-Warning "Podman not found; skipping Open WebUI. Install Podman Desktop or run scripts/start.ps1 -NoWebUI." }
}
Write-Host "Open WebUI: http://localhost:3000  Ollama: http://127.0.0.1:11434"
