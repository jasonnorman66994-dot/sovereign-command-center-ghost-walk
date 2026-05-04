# PowerShell script to clear all rows from the 'events' table in harvest_events.db using System.Data.SQLite
Add-Type -Path "System.Data.SQLite.dll"

$dbPath = "harvest_events.db"
$connStr = "Data Source=$dbPath;Version=3;"

$conn = New-Object System.Data.SQLite.SQLiteConnection($connStr)
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = "DELETE FROM events;"
$rows = $cmd.ExecuteNonQuery()
Write-Host "Deleted $rows rows from 'events' table in $dbPath."

$conn.Close()