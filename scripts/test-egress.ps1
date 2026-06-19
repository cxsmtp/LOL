$ErrorActionPreference = "Continue"
Write-Host "Testing zero-egress behavior..."
$externalBlocked = $false
$localOk = $false
try {
  Invoke-WebRequest -Uri "https://example.com" -TimeoutSec 5 | Out-Null
  Write-Warning "External URL unexpectedly succeeded."
} catch {
  $externalBlocked = $true
  Write-Host "External URL blocked or unreachable as expected."
}
try {
  Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/tags" -TimeoutSec 3 | Out-Null
  $localOk = $true
  Write-Host "Local Ollama reachable."
} catch {
  Write-Warning "Local Ollama is not reachable on 127.0.0.1:11434. Start Ollama first."
}
if ($externalBlocked -and $localOk) { Write-Host "PASS"; exit 0 } else { Write-Host "FAIL"; exit 1 }
