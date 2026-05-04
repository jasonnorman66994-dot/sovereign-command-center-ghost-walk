# 🛑 EMERGENCY ADMIN LOCKDOWN SCRIPT
# Purpose: Revoke sessions and block sign-in for all Global Admins except the Break Glass account.

$BreakGlassAccount = "emergency-admin@company.onmicrosoft.com"
$AdminRole = Get-MgDirectoryRole | Where-Object {$_.DisplayName -eq "Global Administrator"}
$AllAdmins = Get-MgDirectoryRoleMember -DirectoryRoleId $AdminRole.Id

foreach ($Admin in $AllAdmins) {
    $User = Get-MgUser -UserId $Admin.Id
    
    if ($User.UserPrincipalName -ne $BreakGlassAccount) {
        Write-Host "🚨 LOCKING DOWN ADMIN: $($User.UserPrincipalName)" -ForegroundColor Red
        
        # 1. Kill all active sessions immediately
        Invoke-MgRevokeUserSignInSession -UserId $User.Id
        
        # 2. Disable the account to prevent re-authentication
        Update-MgUser -UserId $User.Id -AccountEnabled $false
    } else {
        Write-Host "✅ Skipping Break Glass Account: $($User.UserPrincipalName)" -ForegroundColor Green
    }
}

# 3. List recently created users (to find attacker backdoors)
Write-Host "`n🔍 Checking for newly created accounts (Last 1 hour):" -ForegroundColor Yellow
Get-MgUser -All | Where-Object {$_.CreatedDateTime -gt (Get-Date).AddHours(-1)} | Select-Object UserPrincipalName, CreatedDateTime
