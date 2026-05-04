# app/core/audit.py
import logging
from datetime import datetime

logger = logging.getLogger("sovereign.audit")

# Optionally, configure file handler for persistent audit logs
file_handler = logging.FileHandler("/var/log/sovereign_audit.log")
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)

def log_audit_event(event_type: str, user: str, incident_id: str, reason: str = "", ip: str = None, user_agent: str = None):
    logger.info(
        f"AUDIT | {event_type} | User: {user} | Incident: {incident_id} | Reason: {reason} | IP: {ip or '-'} | UserAgent: {user_agent or '-'}"
    )
