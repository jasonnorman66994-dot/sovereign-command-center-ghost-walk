import os
import mysql.connector
import numpy as np
from datetime import datetime, timedelta
from pyod.models.iforest import IForest
import requests

# Connect to DB
conn = mysql.connector.connect(host='localhost', user='authuser', password='authpass', database='auth_db')
cursor = conn.cursor(dictionary=True)

# Get recent login data
cursor.execute("""
SELECT id, user_id, email, ip_address, country, city, latitude, longitude, device_fingerprint, timestamp
FROM auth_logs
WHERE timestamp >= NOW() - INTERVAL 7 DAY
""")
rows = cursor.fetchall()

# Prepare features for anomaly detection
features = []
ids = []
for row in rows:
    # Example: encode country, city, device, and time as features
    features.append([
        hash(row['country']) % 1000,
        hash(row['city']) % 1000,
        hash(row['device_fingerprint']) % 100000,
        datetime.strptime(str(row['timestamp']), '%Y-%m-%d %H:%M:%S').hour
    ])
    ids.append(row['id'])
features = np.array(features)

# Run Isolation Forest
if len(features) > 10:
    clf = IForest()
    clf.fit(features)
    scores = clf.decision_function(features)
    anomalies = clf.predict(features)
    for i, is_anomaly in enumerate(anomalies):
        if is_anomaly:
            # Write alert to DB
            cursor.execute("""
                INSERT INTO security_alerts (timestamp, alert_type, severity, user_id, ip_address, description, evidence)
                VALUES (NOW(), %s, %s, %s, %s, %s, %s)
            """, (
                'Anomaly Detected', 'HIGH', rows[i]['user_id'], rows[i]['ip_address'],
                f"Unusual login pattern for user {rows[i]['user_id']} at {rows[i]['timestamp']}",
                str(rows[i])
            ))
            conn.commit()
            # Send to Slack
            slack_webhook = os.environ.get('SLACK_WEBHOOK_URL', '')
            if slack_webhook:
                requests.post(
                    slack_webhook,
                    json={"text": f"[ALERT] Anomaly detected for user {rows[i]['user_id']} at {rows[i]['timestamp']}"}
                )

cursor.close()
conn.close()
print('Anomaly detection job complete.')
