# metrics_lib.py

def calculate_mttr(incidents):
    # Dummy implementation for demo
    if not incidents:
        return 0
    return sum(i.count for i in incidents) / len(incidents)

def calculate_gdpr_compliance_health():
    # Dummy implementation for demo
    return 95
