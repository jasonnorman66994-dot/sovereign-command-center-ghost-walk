# PowerShell script to unblock System.Data.SQLite.dll and set permissions

$path = Join-Path -Path $PSScriptRoot -ChildPath "System.Data.SQLite.dll"

if (Test-Path $path) {
    # Unblock the DLL if blocked
    Unblock-File -Path $path
    Write-Host "Unblocked System.Data.SQLite.dll." -ForegroundColor Green

    # Grant read permissions to current user
    $user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $acl = Get-Acl $path
    $accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($user, "Read", "Allow")
    $acl.SetAccessRule($accessRule)
    Set-Acl $path $acl
    Write-Host "Granted read permission to $user." -ForegroundColor Green
} else {
    Write-Host "System.Data.SQLite.dll not found in project root." -ForegroundColor Red
}
