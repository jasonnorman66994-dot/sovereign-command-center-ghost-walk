import imaplib
import email
import time
import json
import subprocess
import os

# Logging setup
LOG_FILE = os.path.join(os.path.dirname(__file__), 'email_to_telegram.log')
def log(msg):
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    print(msg)

# CONFIGURATION
IMAP_SERVER = 'imap.gmail.com'  # Gmail IMAP server
EMAIL_ACCOUNT = 'jasonnorman66994@gmail.com'
EMAIL_PASSWORD = 'ezwockpgpzugahou'
MAILBOX = 'INBOX'
TELEGRAM_FORMATTER = os.path.join(os.path.dirname(__file__), 'telegram_formatter.py')
CHECK_INTERVAL = 60  # seconds

# Helper: Send alert to Telegram using your formatter

def send_to_telegram(payload):
    tmp_path = 'tmp_alert.json'
    with open(tmp_path, 'w') as f:
        json.dump(payload, f)
    log('Sending alert to Telegram using formatter...')
    try:
        subprocess.run(['python', TELEGRAM_FORMATTER, tmp_path], check=True)
        log('Alert sent to Telegram successfully.')
    except Exception as e:
        log(f'Error sending alert to Telegram: {e}')
    os.remove(tmp_path)

# Helper: Parse Defender alert from email body (assumes JSON payload)

def parse_alert_from_email(msg):
    for part in msg.walk():
        if part.get_content_type() == 'application/json':
            payload = part.get_payload(decode=True)
            log(f'Raw application/json payload: {payload}')
            try:
                return json.loads(payload)
            except Exception as e:
                log(f'JSON decode error (application/json): {e}')
        elif part.get_content_type() == 'text/plain':
            payload = part.get_payload(decode=True)
            log(f'Raw text/plain payload: {payload}')
            try:
                return json.loads(payload)
            except Exception as e:
                log(f'JSON decode error (text/plain): {e}')
    return None

def main():
    log('Starting email to Telegram alert bridge...')
    while True:
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
            mail.select(MAILBOX)
            typ, data = mail.search(None, 'UNSEEN')
            for num in data[0].split():
                typ, msg_data = mail.fetch(num, '(RFC822)')
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                alert = parse_alert_from_email(msg)
                if alert:
                    log('New alert received, sending to Telegram...')
                    send_to_telegram(alert)
                else:
                    log('No valid alert found in email.')
                mail.store(num, '+FLAGS', '\\Seen')
            mail.logout()
        except Exception as e:
            log(f'Error: {e}')
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
