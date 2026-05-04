import json
from datetime import datetime

def simulate_sovereign_response():
    with open("session_replay_drift.json", "r") as f:
        replay = json.load(f)[0]
    # Simulate detection logic
    baseline_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/18.19041"
    baseline_ip = "34.201.10.22"  # Los Angeles
    if replay["user_agent"] != baseline_ua or replay["source_ip"] != baseline_ip:
        event = {
            "event": "TOKEN_REVOCATION",
            "user": replay["user"],
            "timestamp": datetime.utcnow().isoformat(),
            "reason": "Impossible Travel / Fingerprint Drift",
            "location": "London",
            "ip": replay["source_ip"],
            "user_agent": replay["user_agent"]
        }
        with open("sovereign_events.json", "w") as f:
            json.dump([event], f, indent=2)
        print("TOKEN_REVOCATION event triggered. Impossible Travel alert generated.")
    else:
        print("No anomaly detected.")

if __name__ == "__main__":
    simulate_sovereign_response()
