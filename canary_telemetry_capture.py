import os
import json
import datetime
import time
from pathlib import Path

CANARY_USERS = ["richard@omnicorp-cyber.com", "jason.n@omnicorp-cyber.com"]
LOG_DIR = "./logs/canary_baseline/"
Path(LOG_DIR).mkdir(parents=True, exist_ok=True)

# Simulate login metadata aggregation
def aggregate_logins():
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H%M")
    data = []
    for user in CANARY_USERS:
        # Simulate login event
        event = {
            "user": user,
            "timestamp": now,
            "ip": "34.201.10.22" if user == "richard@omnicorp-cyber.com" else "34.201.10.23",
            "device": "WS-IT-043" if user == "jason.n@omnicorp-cyber.com" else "MOBILE-01",
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/18.19041"
        }
        data.append(event)
    with open(f"{LOG_DIR}canary_login_{now}.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"Canary login metadata aggregated: {LOG_DIR}canary_login_{now}.json")

if __name__ == "__main__":
    aggregate_logins()
