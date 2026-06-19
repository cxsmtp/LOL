param([string]$ModelName = "llama3.2:3b", [switch]$OverrideZeroEgress)
$ErrorActionPreference = "Stop"
$security = Get-Content "config\security.yaml" -Raw
if ($security -match "zero_egress_mode:\s*true" -and -not $OverrideZeroEgress) {
  throw "Zero-egress mode is enabled. This action requires internet. Disable zero-egress temporarily only if you understand the risk, or rerun with -OverrideZeroEgress during a controlled setup window."
}
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { throw "Ollama is not installed or not in PATH." }
Write-Host "Pulling model $ModelName..."
ollama pull $ModelName
