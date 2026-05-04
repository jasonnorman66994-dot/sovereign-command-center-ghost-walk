import csv
import json
from datetime import datetime

def generate_telegram_payload(click_log_csv='click_log.csv', output_file='telegram-alert-payload.json'):
    # Use the most recent click event for the alert
    with open(click_log_csv, newline='', encoding='utf-8') as f:
        reader = list(csv.DictReader(f))
        if not reader:
            print('No click events found.')
            return
        latest = sorted(reader, key=lambda r: r['timestamp'], reverse=True)[0]
    # Build a minimal payload for the formatter
    payload = {
        "user": {
            "email": latest['email'],
            "user_id": latest['TargetID'],
            "department": latest.get('deviceId', ''),
            "role": "Target"
        },
        "event": {
            "event_type": "Phishing Link Clicked",
            "description": f"User clicked phishing link from device {latest['deviceId']}",
            "source_ip": latest['ip'],
            "asn": "N/A",
            "geo_location": "N/A",
            "client_app": "Browser",
            "auth_method": "N/A",
            "risk_detections": ["Phishing simulation click"]
        },
        "timestamp_utc": latest['timestamp'],
        "severity": "medium",
        "recommended_actions": [
            "Notify user and reset password",
            "Review device activity",
            "Check for lateral movement"
        ],
        "investigation_links": {},
        "assigned_to": {"analyst": "SOC Analyst"}
    }
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
    print(f"Telegram alert payload written to {output_file}")

if __name__ == '__main__':
    generate_telegram_payload()
