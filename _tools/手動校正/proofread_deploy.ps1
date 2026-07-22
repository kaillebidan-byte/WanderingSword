# proofread_deploy.ps1
# One-step deploy: verify -> apply+repack -> copy pak into the game's Paks folder.
# Just run this after editing. CLOSE THE GAME first (the pak is locked while running).
# ASCII-only so Windows PowerShell 5.1 parses it. Japanese guide in the same folder.
# Lives in _tools\<manual-proofread>\ ; project root is two levels up.

$ErrorActionPreference = "Stop"
$proj = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location -LiteralPath $proj
$env:PYTHONIOENCODING = "utf-8"

# Warn if the game seems to be running (would lock the pak)
$running = Get-Process -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -match "Wandering|WS-Win64|WSGame|Shipping" }
if ($running) {
  Write-Host "The game appears to be running. Close it, then re-run this script." -ForegroundColor Yellow
  exit 1
}

python (Join-Path $PSScriptRoot "apply_manual.py") --deploy
$rc = $LASTEXITCODE
Write-Host ""
if ($rc -ne 0) {
  Write-Host "Deploy did NOT complete (exit $rc). See messages above." -ForegroundColor Red
} else {
  Write-Host "Done. Start the game to see the changes." -ForegroundColor Green
}
Read-Host "Press Enter to close"
exit $rc
