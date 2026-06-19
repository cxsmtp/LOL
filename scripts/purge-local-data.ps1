param(
  [switch]$VectorStores,
  [switch]$Reports,
  [switch]$Logs,
  [switch]$MobileReports,
  [switch]$Caches,
  [switch]$All
)
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$targets = @()
if ($All -or $VectorStores) { $targets += "data\work\vector_store", "data\personal\vector_store" }
if ($All -or $Reports) { $targets += "reports" }
if ($All -or $Logs) { $targets += "logs" }
if ($All -or $MobileReports) { $targets += "mobile\reports" }
if ($All -or $Caches) { $targets += ".pytest_cache", "app\__pycache__", "tests\__pycache__" }
if (-not $targets) { Write-Host "Choose what to purge, for example: scripts\purge-local-data.ps1 -Reports"; exit 1 }
Write-Host "The following local data will be deleted:"
$targets | ForEach-Object { Write-Host " - $_" }
$confirm = Read-Host "Type DELETE to continue"
if ($confirm -ne "DELETE") { Write-Host "Cancelled."; exit 1 }
foreach ($rel in $targets) {
  $path = Join-Path $ProjectRoot $rel
  if (Test-Path $path) {
    Remove-Item -Recurse -Force $path
    New-Item -ItemType Directory -Force -Path $path | Out-Null
    New-Item -ItemType File -Force -Path (Join-Path $path ".gitkeep") | Out-Null
    Write-Host "Purged $rel"
  }
}
