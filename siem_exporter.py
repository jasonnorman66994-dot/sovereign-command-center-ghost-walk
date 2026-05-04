import mysql.connector
import json
import requests
from datetime import datetime, timedelta

# SIEM endpoint (replace with your SIEM's HTTP endpoint)
SIEM_URL = 'https://your-siem-endpoint.example.com/ingest'

# Connect to DB
conn = mysql.connector.connect(host='localhost', user='authuser', password='authpass', database='auth_db')
cursor = conn.cursor(dictionary=True)

# Export new logs from the last hour
cursor.execute("""
SELECT * FROM auth_logs WHERE timestamp >= NOW() - INTERVAL 1 HOUR
""")
logs = cursor.fetchall()

# Export new alerts from the last hour
cursor.execute("""
SELECT * FROM security_alerts WHERE timestamp >= NOW() - INTERVAL 1 HOUR
""")
alerts = cursor.fetchall()

# Send to SIEM
payload = {
    'timestamp': datetime.utcnow().isoformat(),
    'logs': logs,
    'alerts': alerts
}
headers = {'Content-Type': 'application/json'}
response = requests.post(SIEM_URL, data=json.dumps(payload), headers=headers)
print('SIEM export status:', response.status_code)

cursor.close()
conn.close()
