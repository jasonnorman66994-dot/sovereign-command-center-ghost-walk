# Automated Campaign Orchestration Script
# This script will:
# 1. Launch each phase (20 lures per phase, with jitter)
# 2. Wait for a configurable interval between phases
# 3. Log status and send real-time updates to the console
# 4. Optionally trigger boardroom snapshots after each phase

param(
    [int]$Phases = 5,
    [int]$LuresPerPhase = 20,
    [int]$JitterMin = 10,
    [int]$JitterMax = 40,
    [int]$IntervalBetweenPhases = 1800, # 30 minutes
    [switch]$SnapshotAfterPhase
)

for ($phase = 1; $phase -le $Phases; $phase++) {
    Write-Host ("[CAMPAIGN] Launching Phase {0}..." -f $phase) -ForegroundColor Cyan
    pwsh -File .\send_lures.ps1 -Limit $LuresPerPhase -JitterMin $JitterMin -JitterMax $JitterMax
    Write-Host ("[CAMPAIGN] Phase {0} complete. Waiting {1} seconds before next phase..." -f $phase, $IntervalBetweenPhases) -ForegroundColor Yellow
    if ($SnapshotAfterPhase) {
        Write-Host "[CAMPAIGN] Triggering boardroom snapshot..." -ForegroundColor Green
        pwsh -Command ".\engagement_monitor.ps1 -Snapshot"
    }
    if ($phase -lt $Phases) {
        Start-Sleep -Seconds $IntervalBetweenPhases
    }
}
Write-Host "[CAMPAIGN] All phases complete. Monitoring for detections..." -ForegroundColor Magenta
