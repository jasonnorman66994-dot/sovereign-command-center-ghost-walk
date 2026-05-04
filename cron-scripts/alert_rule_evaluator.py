import mysql.connector
from datetime import datetime
import requests

conn = mysql.connector.connect(host='db', user='authuser', password='authpass', database='auth_db')
cursor = conn.cursor(dictionary=True)

# Get enabled alert rules
cursor.execute("SELECT * FROM alert_rules WHERE enabled = TRUE")
rules = cursor.fetchall()


import json

for rule in rules:
    cursor.execute(rule['sql_condition'])
    results = cursor.fetchall()
    if results:
        for row in results:
            desc = f"Rule triggered: {rule['description']} | Details: {row}"
            # Try to extract user_id and ip_address if present in row, else None
            user_id = row.get('user_id') if 'user_id' in row else None
            ip_address = row.get('ip_address') if 'ip_address' in row else None
            evidence_json = json.dumps(row)
            cursor.execute("""
                INSERT INTO security_alerts (timestamp, alert_type, severity, user_id, ip_address, description, evidence)
                VALUES (NOW(), %s, %s, %s, %s, %s, %s)
            """, (
                'Custom Rule', rule['severity'], user_id, ip_address, desc, evidence_json
            ))
            conn.commit()
            # Send to Telegram
            telegram_token = "8333246413:AAHuWsWj3I_Io-JpHZ3Gbwldmb60yiu2_bg"
            chat_id = "7406674050"
            telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            payload = {"chat_id": chat_id, "text": f"[ALERT] {desc}"}
            print(f"Sending Telegram alert to {chat_id}...")
            try:
                resp = requests.post(telegram_url, data=payload, timeout=10)
                print(f"Telegram response: {resp.status_code} {resp.text}")
            except Exception as e:
                print(f"Failed to send Telegram alert: {e}")

cursor.close()
conn.close()
print('Custom alert rule evaluation complete.')
