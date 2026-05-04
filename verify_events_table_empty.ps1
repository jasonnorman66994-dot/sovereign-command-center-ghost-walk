# PowerShell script to verify the events table is empty in harvest_events.db
Add-Type -Path "System.Data.SQLite.dll"

$dbPath = "harvest_events.db"
$connStr = "Data Source=$dbPath;Version=3;"

$conn = New-Object System.Data.SQLite.SQLiteConnection($connStr)
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = "SELECT COUNT(*) FROM events;"
$count = $cmd.ExecuteScalar()
Write-Host "Rows in 'events' table: $count"

$conn.Close()
if ($count -eq 0) {
    Write-Host "✅ Database is empty and ready for the boardroom demo." -ForegroundColor Green
} else {
    Write-Host "⚠️  Database is NOT empty!" -ForegroundColor Red
}