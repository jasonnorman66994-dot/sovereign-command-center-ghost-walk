# PowerShell script to automate DLL replacement, unblock, and permission fix

$projectRoot = $PSScriptRoot
$dllName = "System.Data.SQLite.dll"
$dllPath = Join-Path $projectRoot $dllName

# 1. Delete existing DLL if present
if (Test-Path $dllPath) {
    Remove-Item $dllPath -Force
    Write-Host "Deleted old $dllName from project root." -ForegroundColor Yellow
}

# 2. Prompt for new DLL source path
$source = Read-Host "Enter the full path to the new $dllName (e.g. C:\Users\HomePC\Downloads\sqlite-dll-win-x64-*.dll)"
if (!(Test-Path $source)) {
    Write-Host "Source DLL not found: $source" -ForegroundColor Red
    exit 1
}

# 3. Copy new DLL to project root
Copy-Item -Path $source -Destination $dllPath -Force
Write-Host "$dllName copied to project root: $dllPath" -ForegroundColor Green

# 4. Unblock the DLL
Unblock-File -Path $dllPath
Write-Host "Unblocked $dllName." -ForegroundColor Green

# 5. Grant read permission to current user
$user = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$acl = Get-Acl $dllPath
$accessRule = New-Object System.Security.AccessControl.FileSystemAccessRule($user, "Read", "Allow")
$acl.SetAccessRule($accessRule)
Set-Acl $dllPath $acl
Write-Host "Granted read permission to $user." -ForegroundColor Green

Write-Host "\nDLL replacement and permission fix complete. Now run your PowerShell DB scripts as Administrator." -ForegroundColor Cyan
