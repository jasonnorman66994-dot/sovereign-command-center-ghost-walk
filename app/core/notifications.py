import os
import requests
import datetime

LOG_FILE = os.path.join(os.path.dirname(__file__), '../../telegram_debug.log')
def log_debug(msg):
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{datetime.datetime.now().isoformat()} {msg}\n")

def escape_markdown_v2(text: str) -> str:
    # Escape all special MarkdownV2 characters
    # See: https://core.telegram.org/bots/api#markdownv2-style
    chars = r'_ * [ ] ( ) ~ ` > # + - = | { } . !'
    for c in chars.split():
        text = text.replace(c, f'\\{c}')
    return text

def send_telegram_alert(message: str):
    log_debug("[DEBUG] send_telegram_alert called")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    log_debug(f"[DEBUG] TELEGRAM_BOT_TOKEN: {token}")
    log_debug(f"[DEBUG] TELEGRAM_CHAT_ID: {chat_id}")
    if not token or not chat_id:
        log_debug("[WARNING] Telegram bot token or chat ID not set in environment.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": escape_markdown_v2(message),
        "parse_mode": "MarkdownV2",
        "disable_web_page_preview": True
    }
    log_debug(f"[DEBUG] Telegram payload: {payload}")
    try:
        resp = requests.post(url, json=payload, timeout=5)
        log_debug(f"[DEBUG] Telegram response status: {resp.status_code}")
        log_debug(f"[DEBUG] Telegram response body: {resp.text}")
        if resp.status_code != 200:
            log_debug(f"[WARNING] Telegram error: {resp.text}")
    except Exception as e:
        log_debug(f"[EXCEPTION] Telegram alert exception: {repr(e)}")
        log_debug(f"[WARNING] Telegram send failed: {e}")
