# PowerShell script to send a test email using Gmail SMTP
# Replace the values below with your actual details

$smtpServer = "smtp.gmail.com"
$smtpPort = 587
$from = "jasonnorman66994@gmail.com"           # Sender Gmail address
$to = "jasonnorman66994@outlook.com"           # Recipient email address
$workstationID = "LA-WS-1234"
$patchVersion = "KB-2026-0411"
$targetID = "TEST_001"
$phishUrl = "http://localhost:3000/auth?tid=$targetID"
$subject = "Urgent: Security Patch $patchVersion for Workstation $workstationID"
$body = @"
<p>Attention: A critical security vulnerability has been identified on <b>$workstationID</b>.</p>
<p>Please <a href=\"$phishUrl\">click here to verify your identity</a> and apply the mandatory patch ($patchVersion).</p>
<p>Failure to comply will result in a temporary suspension of network access.</p>
"@
$username = "jasonnorman66994@gmail.com"      # Gmail username
$password = "zuuxxkkerewywihn"         # Gmail App Password (not your main password)


$logFile = "./send_gmail_test.log"
function Write-Log {
	param([string]$msg)
	$timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
	"$timestamp $msg" | Out-File -FilePath $logFile -Append -Encoding utf8
	Write-Host $msg
}

Write-Log "[INFO] Starting Gmail SMTP test..."
$securePassword = ConvertTo-SecureString $password -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential($username, $securePassword)

try {
	Send-MailMessage -From $from -To $to -Subject $subject -Body $body -SmtpServer $smtpServer -Port $smtpPort -UseSsl -Credential $cred -ErrorAction Stop -Attachments "C:\Users\HomePC\OneDrive\mine2026\wave3_lure_template.html"
	Write-Log "[SUCCESS] Email sent successfully to $to."
} catch {
	Write-Log "[ERROR] Failed to send email: $($_.Exception.Message)"
	Write-Log "[ERROR] Exception details: $($_ | Out-String)"
}

# To automate, call this script from your pipeline or scheduler.
# For production, use environment variables or a secure vault for credentials.