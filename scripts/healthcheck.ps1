param([string]$ConfigPath = "config/app_settings.yaml")
$ErrorActionPreference = "Continue"
Write-Host "Local AI Workbench zero-egress health check"
$ok = $true
if ($env:OLLAMA_HOST -and $env:OLLAMA_HOST -match "0\.0\.0\.0") { Write-Error "OLLAMA_HOST must not be 0.0.0.0 in zero-egress mode."; $ok = $false }
if (-not $env:OLLAMA_HOST) { Write-Host "OLLAMA_HOST is not set in this shell; start.ps1 sets it to 127.0.0.1:11434." }
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { Write-Error "Ollama is not in PATH."; $ok = $false } else { ollama --version }
try { $r = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 3; Write-Host "Ollama API reachable on localhost. Models:"; $r.models.name } catch { Write-Warning "Ollama API not reachable on http://127.0.0.1:11434. Start Ollama or run scripts/start.ps1"; $ok = $false }
try { Invoke-RestMethod -Uri "http://$($env:COMPUTERNAME):11434/api/tags" -TimeoutSec 2 | Out-Null; Write-Error "Ollama may be reachable via LAN hostname. Check binding."; $ok = $false } catch { Write-Host "LAN hostname Ollama check failed as expected." }
if (Get-Command podman -ErrorAction SilentlyContinue) { podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" } else { Write-Warning "Podman not found; Open WebUI container will not start." }
if ($ok) { exit 0 } else { exit 1 }
