# Emergency Admin Account Recovery & Backdoor Removal Playbook

## Step 1: Emergency Account Use

 Log in with a "Break Glass" account (excluded from Conditional Access and MFA).
 Ensure this account is not compromised and is monitored.

## Step 2: Delete the Backdoor

 Identify and immediately delete `backup-admin@company.onmicrosoft.com` and any user accounts created in the last 30 minutes:
    ```powershell
$recentUsers = Get-MgUser -Filter "createdDateTime ge $(Get-Date).AddMinutes(-30).ToString('o')"
$recentUsers | ForEach-Object { Remove-MgUser -UserId $_.Id }
Remove-MgUser -UserId "backup-admin@company.onmicrosoft.com```

## Step 3: Reset the PIM/Trust

Revoke all active Privileged Identity Management (PIM) elevations:

```powershell

Get-MgRoleManagementDirectoryRoleEligibilityScheduleInstance | ForEach-Object { Revoke-MgRoleManagementDirectoryRoleEligibilityScheduleInstance -RoleEligibilityScheduleInstanceId $_.Id }  
Example output or notes here
Force re-authentication for all admin accounts:
powershell
Get-MgUser -Filter "userType eq 'Member' and accountEnabled eq true and userPrincipalName ne  breakglass@company.com'" | ForEach-Object { Invoke-MgInvalidateUserRefreshToken -UserId $_.Id 
## Step 4: Check for Service Principals
List all service principals created in the last 30 minutes and those with `AppRoleAssignment.
ReadWrite.All`:
powershell
Review the OAuth Apps investigation link in the alert for suspicious applications.

---
**Note:** Always document actions and coordinate with your incident response team. Rotate credentials and review audit logs after remediation
