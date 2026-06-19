Write-Host "Stopping optional Open WebUI container..."
if (Get-Command docker -ErrorAction SilentlyContinue) { docker stop open-webui 2>$null | Out-Null }
Write-Host "Ollama may keep running as a user service. Stop it from the tray icon if desired."
