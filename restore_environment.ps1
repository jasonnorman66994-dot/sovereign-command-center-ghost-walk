# restore_environment.ps1
# PowerShell script for Sovereign 2.0 environment reset

# 1. Flush Logs
Write-Host "[RESTORE] Clearing send_gmail_test.log..."
Remove-Item -Path send_gmail_test.log -ErrorAction SilentlyContinue
New-Item -Path send_gmail_test.log -ItemType File | Out-Null

# 2. Reset HUD counter
Write-Host "[RESTORE] Resetting HUD SESSION HARVEST counter to 0/50..."
Set-Content -Path hud_counter.txt -Value "0/50"

# 3. Reset UI (3D Globe)
Write-Host "[RESTORE] Resetting 3D Globe to Standard Blue/Green..."
Set-Content -Path hud_status.txt -Value "STANDARD"

# 4. Re-arm Traps (clear revocation flags)
Write-Host "[RESTORE] Clearing session revocation flags..."
Remove-Item -Path revoked_sessions.json -ErrorAction SilentlyContinue
New-Item -Path revoked_sessions.json -ItemType File | Out-Null

# 5. Archive forensic artifacts

# Archive to dated folder for final protocol
$archiveDir = "history/2026-05-01_SeriesA_Success"
if (!(Test-Path $archiveDir)) { New-Item -Path $archiveDir -ItemType Directory | Out-Null }
Write-Host "[RESTORE] Archiving forensic artifacts..."
Move-Item -Path SeriesA_Security_Summary.pdf -Destination $archiveDir -Force -ErrorAction SilentlyContinue
Move-Item -Path send_gmail_test.log -Destination $archiveDir -Force -ErrorAction SilentlyContinue

Write-Host "[RESTORE] Environment restored. Ready for next simulation."
