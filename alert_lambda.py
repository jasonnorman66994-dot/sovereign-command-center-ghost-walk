import json
import os
import requests
from telegram_alert_formatter import format_telegram_alert

def lambda_handler(event, context):
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
    TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    try:
        payload = event["body"] if "body" in event else event
        if isinstance(payload, str):
            payload = json.loads(payload)
    except Exception as e:
        return {"statusCode": 400, "body": f"Invalid JSON: {e}"}

    try:
        message = format_telegram_alert(payload)
        resp = requests.post(TELEGRAM_URL, data={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": "MarkdownV2"
        })
        if resp.status_code != 200:
            return {"statusCode": 500, "body": f"Telegram error: {resp.text}"}
        return {"statusCode": 200, "body": "ok"}
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
