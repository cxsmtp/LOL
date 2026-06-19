$ErrorActionPreference = "Stop"
$RulePrefix = "LocalAIWorkbench-ZeroEgress"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$LogMarker = Join-Path $ProjectRoot "logs\zero_egress_firewall.enabled"
New-Item -ItemType Directory -Force -Path (Join-Path $ProjectRoot "logs") | Out-Null
Write-Host "Enabling zero-egress firewall rules for this project. Administrator rights may be required."
$paths = @(
  (Join-Path $ProjectRoot ".venv\Scripts\python.exe"),
  (Join-Path $ProjectRoot ".venv\Scripts\pythonw.exe"),
  (Join-Path $ProjectRoot "node.exe"),
  (Join-Path $ProjectRoot "local-ai-workbench.exe")
) | Where-Object { Test-Path $_ }
foreach ($path in $paths) {
  $name = "$RulePrefix-$([IO.Path]::GetFileNameWithoutExtension($path))"
  if (-not (Get-NetFirewallRule -DisplayName $name -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName $name -Direction Outbound -Program $path -Action Block -Profile Any | Out-Null
    Write-Host "Created outbound block rule: $name -> $path"
  } else { Write-Host "Rule already exists: $name" }
}
"enabled $(Get-Date -Format o)" | Set-Content -Path $LogMarker -Encoding UTF8
Write-Host "Localhost traffic is not blocked by these outbound program rules. Verify with scripts\test-egress.ps1."
