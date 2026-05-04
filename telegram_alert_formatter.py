import json

def format_telegram_alert(payload: dict) -> str:
    def esc(text):
        if text is None:
            return ""
        return str(text).replace("-", "\\-").replace(".", "\\.").replace("_", "\\_")

    user = payload["user"]
    event = payload["event"]
    tech = payload["technical_indicators"]
    links = payload["investigation_links"]
    assigned = payload["assigned_to"]

    message = f"""
🚨 *IDENTITY SECURITY ALERT*  
Potential account compromise detected.

👤 *User:* {esc(user['email'])}  
🆔 *User ID:* {esc(user['user_id'])}  
🏢 *Department:* {esc(user['department'])}  
🔐 *Role:* {esc(user['role'])}

---

⚠️ *Event Type:* {esc(event['event_type'])}  
{esc(event['description'])}

🕒 *Timestamp:* {esc(payload['timestamp_utc'])}  
🌐 *Source IP:* {esc(event['source_ip'])}  
🏢 *ASN / Location:* {esc(event['asn'])} / {esc(event['geo_location'])}  
📱 *Client App:* {esc(event['client_app'])}  
🔐 *Auth Method:* {esc(event['auth_method'])}

---

🧩 *Indicators:*  
- {esc(event['risk_detections'][0])}  
- {esc(event['risk_detections'][1])}  
- {esc(event['risk_detections'][2])}

---

🛑 *Recommended Actions:*  
1\. Revoke all active sessions  
2\. Block the account  
3\. Reset password  
4\. Reset MFA bindings  
5\. Review OAuth grants  
6\. Check inbox rules

---

🛠️ *Investigation Links:*  
[Sign-in Logs]({links['signin_logs']})  
[OAuth Apps]({links['oauth_apps']})  
[Inbox Rules]({links['inbox_rules']})  
[Sentinel Query]({links['sentinel_query']})

---

📣 *Severity:* {esc(payload['severity'])}  
👮 *Assigned To:* {esc(assigned['analyst'])}
"""
    return message

if __name__ == "__main__":
    # Example usage
    with open("example_alert.json") as f:
        payload = json.load(f)
    print(format_telegram_alert(payload))
