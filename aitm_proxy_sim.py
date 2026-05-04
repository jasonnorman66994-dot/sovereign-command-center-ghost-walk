import json
from datetime import datetime

def simulate_aitm_proxy():
    # Simulate intercepting a login and capturing a session token
    token = {
        "user": "jason.n@omnicorp-cyber.com",
        "session_token": "SESSION-FAKE-TOKEN-12345",
        "timestamp": datetime.utcnow().isoformat(),
        "source_ip": "34.201.10.22",  # Los Angeles
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/18.19041"
    }
    with open("captured_tokens.json", "w") as f:
        json.dump([token], f, indent=2)
    print("AiTM proxy simulation complete. Token captured.")

if __name__ == "__main__":
    simulate_aitm_proxy()
