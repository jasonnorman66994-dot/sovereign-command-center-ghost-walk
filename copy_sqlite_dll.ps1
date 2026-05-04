# PowerShell: Copy System.Data.SQLite.dll to working directory

$source = "C:\Users\HomePC\Downloads\system.data.sqlite.2.0.3\bin\x64\System.Data.SQLite.dll"
$destination = Join-Path -Path $PSScriptRoot -ChildPath "System.Data.SQLite.dll"

if (Test-Path $source) {
    Copy-Item -Path $source -Destination $destination -Force
    Write-Host "System.Data.SQLite.dll copied to project root: $destination" -ForegroundColor Green
}
else {
    Write-Host "Source DLL not found: $source" -ForegroundColor Red
}
