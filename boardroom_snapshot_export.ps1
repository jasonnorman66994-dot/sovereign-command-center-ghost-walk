# Boardroom Snapshot Export Script (PowerShell)
# Exports MTTD, incident timeline, and key metrics to CSV for boardroom use

$dbPath = "./harvester_data.db"
$sqlitePath = "C:/Users/HomePC/Downloads/sqlite-tools-win-x64-3530000/sqlite3.exe"
$snapshotFile = "./boardroom_snapshot_$(Get-Date -Format yyyyMMdd_HHmmss).csv"

# --- Calculate MTTD ---
$mttd = & $sqlitePath $dbPath "SELECT AVG(julianday(timestamp) - julianday((SELECT MIN(timestamp) FROM telemetry))) * 24 * 60 FROM telemetry WHERE event_type = 'Credential_Harvest'"

# --- Incident Timeline ---
$timeline = & $sqlitePath $dbPath "SELECT timestamp, event_type, email, ip FROM telemetry ORDER BY timestamp ASC"

# --- Export ---
"Metric,Value" | Out-File $snapshotFile -Encoding utf8
"MTTD (min),$([math]::Round($mttd,2))" | Out-File $snapshotFile -Append -Encoding utf8

"" | Out-File $snapshotFile -Append -Encoding utf8
"Timestamp,Event Type,Email,IP" | Out-File $snapshotFile -Append -Encoding utf8
$timeline | ForEach-Object { $_ -replace "\|", "," } | Out-File $snapshotFile -Append -Encoding utf8

Write-Host "Boardroom snapshot exported to $snapshotFile" -ForegroundColor Green
