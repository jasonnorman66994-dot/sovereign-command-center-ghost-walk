import json
from datetime import datetime

def replay_session_with_drift():
    # Load captured token
    with open("captured_tokens.json", "r") as f:
        tokens = json.load(f)
    token = tokens[0]
    # Simulate replay from London with fingerprint drift
    replay = {
        "user": token["user"],
        "session_token": token["session_token"],
        "timestamp": datetime.utcnow().isoformat(),
        "source_ip": "51.140.12.99",  # London
        "user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "event": "SESSION_REPLAY_DRIFT"
    }
    with open("session_replay_drift.json", "w") as f:
        json.dump([replay], f, indent=2)
    print("Session replay with fingerprint drift complete. Replay event saved.")

if __name__ == "__main__":
    replay_session_with_drift()
