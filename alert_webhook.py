from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel, ValidationError
import json
import requests
from telegram_alert_formatter import format_telegram_alert

app = FastAPI()

TELEGRAM_BOT_TOKEN = "<YOUR_BOT_TOKEN>"
TELEGRAM_CHAT_ID = "<YOUR_CHAT_ID>"
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

class IdentityThreatAlert(BaseModel):
    alert_type: str
    severity: str
    timestamp_utc: str
    user: dict
    event: dict
    technical_indicators: dict = None
    recommended_actions: list
    investigation_links: dict = None
    assigned_to: dict
    metadata: dict = None

@app.post("/alert")
async def receive_alert(request: Request):
    try:
        payload = await request.json()
        alert = IdentityThreatAlert(**payload)
    except (ValidationError, Exception) as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Format and send to Telegram
    message = format_telegram_alert(payload)
    resp = requests.post(TELEGRAM_URL, data={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "MarkdownV2"
    })
    if resp.status_code != 200:
        raise HTTPException(status_code=500, detail=f"Telegram error: {resp.text}")
    return {"status": "ok"}
