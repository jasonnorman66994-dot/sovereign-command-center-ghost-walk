import json
from datetime import datetime

def simulate_credential_dump():
    # Simulate rundll32.exe credential dumping event
    event = {
        "host": "WS-IT-043",
        "user": "jason.n@omnicorp-cyber.com",
        "process": "rundll32.exe",
        "timestamp": datetime.utcnow().isoformat(),
        "event": "CREDENTIAL_DUMP"
    }
    with open("credential_dump_event.json", "w") as f:
        json.dump([event], f, indent=2)
    print("Credential dumping event simulated (rundll32.exe).")

if __name__ == "__main__":
    simulate_credential_dump()
