from fastapi import FastAPI
from typing import List
import os
from metrics_lib import calculate_mttr, calculate_gdpr_compliance_health
from zero_trust_hashing import zero_trust_hash


class MockIncident:
    def __init__(self, date, count):
        self.date = date
        self.count = count

class MockDB:
    def get_incident_history(self, days=30):
        # Return mock data for demonstration
        from datetime import datetime, timedelta
        return [MockIncident((datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'), i+1) for i in range(days)]

db = MockDB()

app = FastAPI()

# --- Existing code ...

# Management metrics endpoint
@app.get("/api/dashboard/metrics")
async def get_management_metrics(days: int = 30):

    # Fetch incidents from the DB
    incidents = db.get_incident_history(days=days)

    # Example: Replace real_passwords with Zero Trust Hashing Service
    passwords = ['hunter2', 'letmein', 'password123']
    hashed_passwords = [zero_trust_hash(pw) for pw in passwords]

    # Aggregate data for time-series visualization
    metrics = {
        "dates": [i.date for i in incidents],
        "incident_counts": [i.count for i in incidents],
        "avg_mttr": calculate_mttr(incidents),
        "compliance_score": calculate_gdpr_compliance_health()
    }

    return metrics
import subprocess
import sys
# Send Telegram alert via Python wrapper

SMTP_HOST = os.getenv('SMTP_HOST', '127.0.0.1')
def send_telegram_alert(payload_file='telegram-alert-payload.json'):
    try:
        # Generate the payload dynamically
        result_gen = subprocess.run(
            [sys.executable, 'generate_telegram_payload.py'],
            capture_output=True,
            text=True,
            check=True,
            encoding='utf-8',
            errors='replace'
        )
        print(result_gen.stdout)
        if result_gen.stderr:
            print(result_gen.stderr)
        # Send the alert
        env = os.environ.copy()
        env['PYTHONUTF8'] = '1'
        result = subprocess.run(
            [sys.executable, 'send_telegram_alert.py', payload_file],
            capture_output=True,
            text=True,
            check=True,
            env=env,
            encoding='utf-8',
            errors='replace'
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print(f'Failed to send Telegram alert: {e.stderr}')

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import requests
import os


# Email config (Production-ready: use environment variables)
SMTP_HOST = os.getenv('SMTP_HOST', '127.0.0.1')
SMTP_PORT = int(os.getenv('SMTP_PORT', '1025'))
SMTP_USER = os.getenv('SMTP_USER', 'devrelay_user')
SMTP_PASS = os.getenv('SMTP_PASS', 'devrelay_password')
FROM_ADDR = os.getenv('FROM_ADDR', 'jasonnorman66994@gmail.com')
TO_ADDR = os.getenv('TO_ADDR', 'jasonnorman66994@gmail.com')

# Report files
HTML_REPORT = 'phish_click_report.html'
EXCEL_REPORT = 'phish_campaign_report.xlsx'

# SIEM Webhook config
SIEM_WEBHOOK_URL = 'http://localhost:8080/alerts'  # Local SOC listener

# Send email with attachments
def send_email():
    msg = MIMEMultipart()
    msg['Subject'] = 'Phishing Campaign Report'
    msg['From'] = FROM_ADDR
    msg['To'] = TO_ADDR
    body = (
        'Attached are the latest phishing campaign analytics and click reports.\n\n'
        'If you no longer wish to receive these emails, reply with "UNSUBSCRIBE" or click the unsubscribe link below.\n\n'
        'Unsubscribe: https://your-unsubscribe-link.example.com\n\n'
        '---\n'
        'Security Research Project\n'
        '1234 Research Ave, Suite 100\n'
        'Your City, State ZIP\n'
        'USA\n'
    )
    msg.attach(MIMEText(body, 'plain'))
    # Attach HTML report
    if os.path.exists(HTML_REPORT):
        with open(HTML_REPORT, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={HTML_REPORT}')
            msg.attach(part)
    # Attach Excel report
    if os.path.exists(EXCEL_REPORT):
        with open(EXCEL_REPORT, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={EXCEL_REPORT}')
            msg.attach(part)
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_ADDR, TO_ADDR, msg.as_string())
        print(f'Report email sent to {TO_ADDR}')
    except Exception as e:
        print(f'Failed to send report email: {e}')

# Send click events to SIEM
# (Sends each row in click_log.csv as a JSON POST)
def send_to_siem():
    import csv
    import json
    CLICK_LOG = 'click_log.csv'
    if not os.path.exists(CLICK_LOG):
        print('No click log found for SIEM export.')
        return
    with open(CLICK_LOG, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 10:
                break
            try:
                print(f"[VERBOSE] Attempting POST to {SIEM_WEBHOOK_URL}")
                print(f"[VERBOSE] Payload: {row}")
                resp = requests.post(SIEM_WEBHOOK_URL, json=row, timeout=5)
                print(f"[VERBOSE] Response status: {resp.status_code}")
                print(f"[VERBOSE] Response body: {resp.text}")
            except Exception as e:
                print(f'[ERROR] Failed to send to SIEM: {e}')

if __name__ == '__main__':
    print('[INFO] Running send_phish_reports.py main block')
    send_email()
    print('[INFO] Calling send_to_siem()')
    send_to_siem()
    print('[INFO] Calling send_telegram_alert()')
    send_telegram_alert('telegram-alert-payload.json')
