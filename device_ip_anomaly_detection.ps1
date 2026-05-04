# Device/IP Anomaly Detection Logic (PowerShell Example)
# This script fragment can be integrated into your telemetry pipeline or called from daily_report.ps1

# --- CONFIG ---
$dbPath = "./harvester_data.db"
$sqlitePath = "C:/Users/HomePC/Downloads/sqlite-tools-win-x64-3530000/sqlite3.exe"
$anomalyThresholdKm = 1000  # Flag if login is >1000km from home IP

# --- Helper: Calculate distance between two lat/lon points (Haversine formula) ---
function Get-DistanceKm($lat1, $lon1, $lat2, $lon2) {
    $R = 6371  # Earth radius in km
    $dLat = [math]::PI/180*($lat2-$lat1)
    $dLon = [math]::PI/180*($lon2-$lon1)
    $a = [math]::Sin($dLat/2)*[math]::Sin($dLat/2) + [math]::Cos([math]::PI/180*$lat1)*[math]::Cos([math]::PI/180*$lat2)*[math]::Sin($dLon/2)*[math]::Sin($dLon/2)
    $c = 2*[math]::Atan2([math]::Sqrt($a), [math]::Sqrt(1-$a))
    return $R * $c
}

# --- Main: Check for IP/geo anomalies for each user ---
$users = & $sqlitePath $dbPath "SELECT DISTINCT email FROM telemetry WHERE event_type = 'Credential_Harvest' AND email IS NOT NULL"
foreach ($user in $users) {
    $home = & $sqlitePath $dbPath "SELECT latitude, longitude FROM telemetry WHERE email = '$user' AND event_type = 'Credential_Harvest' ORDER BY timestamp ASC LIMIT 1"
    $latest = & $sqlitePath $dbPath "SELECT latitude, longitude, ip, timestamp FROM telemetry WHERE email = '$user' AND event_type = 'Credential_Harvest' ORDER BY timestamp DESC LIMIT 1"
    if ($home -and $latest) {
        $homeLat, $homeLon = $home -split '\|'
        $lat, $lon, $ip, $ts = $latest -split '\|'
        $dist = Get-DistanceKm $homeLat $homeLon $lat $lon
        if ($dist -gt $anomalyThresholdKm) {
            $msg = "[ANOMALY] User $user session from $ip ($lat,$lon) is $([math]::Round($dist,1))km from home. Timestamp: $ts"
            Write-Host $msg -ForegroundColor Red
            # Optionally: log, alert, or trigger globe overlay here
        }
    }
}
