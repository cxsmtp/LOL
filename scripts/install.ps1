param([switch]$SkipPython, [switch]$OverrideZeroEgress)
$ErrorActionPreference = "Stop"
Write-Host "Installing Local AI Workbench dependencies..."
$security = Get-Content "config\security.yaml" -Raw
if ($security -match "zero_egress_mode:\s*true" -and -not $OverrideZeroEgress) {
  throw "Zero-egress mode is enabled. This action requires internet. Disable zero-egress temporarily only if you understand the risk, or rerun with -OverrideZeroEgress during a controlled setup window."
}
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) { Write-Warning "Install Ollama manually during a controlled setup window." }
if (-not $SkipPython) { python -m venv .venv; .\.venv\Scripts\python.exe -m pip install --upgrade pip; .\.venv\Scripts\pip.exe install -r requirements.txt }
Write-Host "Install complete. Next: scripts/pull-model.ps1 -OverrideZeroEgress, then enable zero-egress."
