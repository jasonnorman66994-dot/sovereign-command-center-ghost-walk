import json
from pathlib import Path

LOG_DIR = "./logs/canary_baseline/"
PULSE_BLUE = "#1E90FF"

# Simulate pushing live Canary sessions to the 3D Globe

def push_canary_stream():
    files = sorted(Path(LOG_DIR).glob("canary_login_*.json"), reverse=True)
    if not files:
        print("No canary login files found.")
        return
    with open(files[0], "r") as f:
        logins = json.load(f)
    globe_events = []
    for event in logins:
        globe_events.append({
            "user": event["user"],
            "ip": event["ip"],
            "device": event["device"],
            "color": PULSE_BLUE,
            "event": "CANARY_SESSION"
        })
    with open("globe_canary_stream.json", "w") as f:
        json.dump(globe_events, f, indent=2)
    print("Canary stream pushed to 3D Globe (Pulse Blue).")

if __name__ == "__main__":
    push_canary_stream()
