# threat_simulation_scheduler.ps1
# PowerShell script to automate and schedule threat simulation runs
# Usage: .\threat_simulation_scheduler.ps1 -Scenarios "geo-anomaly,session-hijack,malware-beacon" -IntervalSeconds 60 -Repeat 5

param(
    [string]$Scenarios = "geo-anomaly,session-hijack",
    [int]$IntervalSeconds = 60,
    [int]$Repeat = 3
)

$scenarioList = $Scenarios -split ','

Write-Host "[Scheduler] Starting threat simulation runs..."
for ($i = 1; $i -le $Repeat; $i++) {
    foreach ($scenario in $scenarioList) {
        Write-Host "[Scheduler] Run $i/$Repeat Simulating $scenario"
        node threat_simulator.js $scenario
        Start-Sleep -Seconds $IntervalSeconds
    }
}
Write-Host "[Scheduler] All scheduled simulations complete."
