param([string]$ConfigPath = "config/app_settings.yaml")
$ErrorActionPreference = "Continue"
Write-Host "Local AI Workbench health check"
$ok = $true
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { Write-Error "Ollama is not in PATH."; $ok = $false } else { ollama --version }
try { $r = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3; Write-Host "Ollama API reachable. Models:"; $r.models.name } catch { Write-Warning "Ollama API not reachable on http://localhost:11434. Start Ollama or run scripts/start.ps1"; $ok = $false }
if (Get-Command podman -ErrorAction SilentlyContinue) { podman ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" } else { Write-Warning "Podman not found; Open WebUI container will not start." }
if ($ok) { exit 0 } else { exit 1 }
