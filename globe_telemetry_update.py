import json

def push_threat_arc():
    # Simulate pushing a threat arc from Los Angeles to London
    arc = {
        "from": {"city": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
        "to": {"city": "London", "lat": 51.5074, "lon": -0.1278},
        "event": "Impossible Travel: TOKEN_REVOCATION",
        "ip": "51.140.12.99",
        "user": "jason.n@omnicorp-cyber.com"
    }
    with open("globe_threat_arc.json", "w") as f:
        json.dump([arc], f, indent=2)
    print("Threat arc pushed to 3D Globe: Los Angeles → London.")

if __name__ == "__main__":
    push_threat_arc()
