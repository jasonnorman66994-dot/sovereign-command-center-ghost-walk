import datetime

def simulate_bec_alert():
    alert = {
        "type": "New Inbox Rule",
        "folder": "Archive",
        "rule": "Forward to external@attacker.com",
        "timestamp": datetime.datetime.now().isoformat(),
        "source": "simulate_bec_rules.py"
    }
    print(f"[BEC] ALERT: {alert}")
    return alert

def simulate_internal_spam():
    spam = {
        "from": "jason.n@omnicorp-cyber.com",
        "to": ["finance.audit@omnicorp.com", "hr.manager@omnicorp.com"],
        "subject": "Urgent: Review Q2 Budget",
        "body": "Please see the attached document.",
        "timestamp": datetime.datetime.now().isoformat(),
        "source": "simulate_bec_rules.py"
    }
    print(f"[BEC] INTERNAL SPAM: {spam}")
    return spam

if __name__ == "__main__":
    simulate_bec_alert()
    simulate_internal_spam()
