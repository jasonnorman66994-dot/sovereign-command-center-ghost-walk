# tests/test_remediation_loop.py
import requests
import time

# 1. Trigger the Kill-Switch
API_URL = "http://localhost:8000/api/v1/remediate/kill-switch"
HEADERS = {"Authorization": "Bearer <YOUR_VALID_JWT>"} # Replace with a token from your auth shell

remediation_payload = {
    "resource_id": "INC-9942", # The ID of the incident we injected
    "action_type": "ISOLATE_POD",
    "confidence": 0.99
}

def run_loop():
    print("--- Initiating Sovereign Remediation Loop ---")
    
    # Send the trigger
    print(f"Sending remediation command for {remediation_payload['resource_id']}...")
    response = requests.post(API_URL, json=remediation_payload, headers=HEADERS)
    
    if response.status_code == 200:
        print("✅ Backend accepted remediation command.")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Backend rejected request. Status: {response.status_code}")
        print(f"Error: {response.text}")
        return

    print("--- Loop Complete: Check your Dashboard UI ---")

if __name__ == "__main__":
    run_loop()
