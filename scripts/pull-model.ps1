param([string]$ModelName = "llama3.2:3b")
$ErrorActionPreference = "Stop"
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { throw "Ollama is not installed or not in PATH." }
Write-Host "Pulling model $ModelName..."
ollama pull $ModelName
