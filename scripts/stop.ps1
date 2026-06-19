Write-Host "Stopping optional Open WebUI Podman container..."
if (Get-Command podman -ErrorAction SilentlyContinue) { podman stop open-webui 2>$null | Out-Null }
Write-Host "Ollama may keep running as a user service. Stop it from the tray icon if desired."
