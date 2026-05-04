
import pyodbc
from datetime import datetime
import requests

# MSSQL connection string
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost;DATABASE=auth_db;UID=authuser;PWD=authpass'
)
cursor = conn.cursor()

# Get enabled alert rules
cursor.execute("SELECT rule_id, description, sql_condition, severity FROM alert_rules WHERE enabled = 1")
rules = cursor.fetchall()

for rule in rules:
    rule_id, description, sql_condition, severity = rule
    try:
        cursor.execute(sql_condition)
        results = cursor.fetchall()
        if results:
            for row in results:
                desc = f"Rule triggered: {description} | Details: {row}"
                cursor.execute("""
                    INSERT INTO security_alerts (timestamp, alert_type, severity, description, evidence)
                    VALUES (GETDATE(), ?, ?, ?, ?)
                """, ('Custom Rule', severity, desc, str(row)))
                conn.commit()
                print(f"[ALERT] {desc}")
                # Send to Telegram
                telegram_token = "<YOUR_TELEGRAM_BOT_TOKEN>"
                chat_id = "<YOUR_TELEGRAM_CHAT_ID>"
                telegram_url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
                payload = {"chat_id": chat_id, "text": f"[ALERT] {desc}"}
                try:
                    resp = requests.post(telegram_url, data=payload, timeout=10)
                    print(f"Telegram response: {resp.status_code} {resp.text}")
                except Exception as e:
                    print(f"Failed to send Telegram alert: {e}")
    except Exception as e:
        print(f"Error evaluating rule {rule_id}: {e}")

cursor.close()
conn.close()
print('Custom alert rule evaluation complete.')
