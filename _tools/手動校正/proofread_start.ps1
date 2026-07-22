# proofread_start.ps1
# Manual-proofread web server launcher. Session-independent: run this in YOUR own
# PowerShell window. Keeps running until you close the window or press Ctrl+C.
# This script lives in _tools\<manual-proofread>\ . Project root is two levels up.
# Kept ASCII-only so Windows PowerShell 5.1 parses it. Sibling files are referenced
# via $PSScriptRoot so the (Japanese) folder name never appears as a literal.

$ErrorActionPreference = "Stop"
$proj = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
Set-Location -LiteralPath $proj
$env:PYTHONIOENCODING = "utf-8"

# Free port 8765 if a previous instance is still listening
$conns = Get-NetTCPConnection -LocalPort 8765 -State Listen -ErrorAction SilentlyContinue
if ($conns) {
  foreach ($c in $conns) { Stop-Process -Id $c.OwningProcess -Force -ErrorAction SilentlyContinue }
}

Write-Host ""
Write-Host "=== Manual Proofread Server ===" -ForegroundColor Cyan
Write-Host ("Project: " + $proj)
Write-Host "URL    : http://127.0.0.1:8765"
Write-Host "Stop   : press Ctrl+C in this window" -ForegroundColor Yellow
Write-Host ""

# Open the browser ~6s after the server starts listening
Start-Job { Start-Sleep 6; Start-Process "http://127.0.0.1:8765" } | Out-Null

python (Join-Path $PSScriptRoot "proofread_server.py")
