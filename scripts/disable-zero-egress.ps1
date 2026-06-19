$ErrorActionPreference = "Continue"
$RulePrefix = "LocalAIWorkbench-ZeroEgress"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Get-NetFirewallRule -DisplayName "$RulePrefix*" -ErrorAction SilentlyContinue | ForEach-Object {
  Write-Host "Removing firewall rule: $($_.DisplayName)"
  Remove-NetFirewallRule -Name $_.Name
}
$LogMarker = Join-Path $ProjectRoot "logs\zero_egress_firewall.enabled"
if (Test-Path $LogMarker) { Remove-Item $LogMarker -Force }
Write-Host "Removed only Local AI Workbench zero-egress firewall rules."
