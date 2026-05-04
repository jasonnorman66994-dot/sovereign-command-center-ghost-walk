# tests/simulate_incident.py
import requests
import json
import time

# Target the Sovereign Mock Endpoint
API_URL = "http://localhost:8000/api/v1/mock/inject-incident"

# The Incident Payload (Mimicking an EDR detection)
incident = {
    "id": "INC-9942",
    "coords": [34.05, -118.25], # Los Angeles
    "severity": "critical",
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "metadata": {
        "source": "EDR_AGENT_PROD",
        "description": "Unauthorized Egress to malicious IP 192.168.1.55"
    }
}

def inject():
    print(f"Injecting Incident {incident['id']}...")
    try:
        response = requests.post(API_URL, json=incident)
        if response.status_code == 200:
            print("Successfully injected telemetry.")
        else:
            print(f"Failed: {response.text}")
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    inject()
