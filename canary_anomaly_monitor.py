import json
import os
import requests
from pathlib import Path

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_GROUP_CHAT_ID", "")
LOG_DIR = "./logs/canary_baseline/"
LA_IP_BLOCK = ["34.201.10.22", "34.201.10.23"]

# Scan for anomalies in the latest canary login file
def check_for_anomalies():
    files = sorted(Path(LOG_DIR).glob("canary_login_*.json"), reverse=True)
    if not files:
        print("No canary login files found.")
        return
    with open(files[0], "r") as f:
        logins = json.load(f)
    for event in logins:
        if event["ip"] not in LA_IP_BLOCK:
            send_telegram_alert(event)

def send_telegram_alert(event):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not set. Skipping alert.")
        return
    msg = f"[CANARY ANOMALY] {event['user']} login from {event['ip']} (device: {event['device']})"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg}
    try:
        requests.post(url, data=payload)
        print(f"Telegram alert sent: {msg}")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")

if __name__ == "__main__":
    check_for_anomalies()
