# PowerShell script to add a custom domain to the Windows hosts file
$hostsPath = "C:\Windows\System32\drivers\etc\hosts"
$entry = "127.0.0.1  kinonlisplazmaoplayor.xyz"

# Check if entry already exists
$hostsContent = Get-Content $hostsPath -ErrorAction SilentlyContinue
if ($hostsContent -notcontains $entry) {
    Add-Content -Path $hostsPath -Value $entry
    Write-Output "Added entry to hosts file: $entry"
} else {
    Write-Output "Entry already exists in hosts file."
}
