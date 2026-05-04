from fastapi import APIRouter, Depends, Request
from app.core.audit import log_audit_event
from app.core.training_set import update_training_set
from app.core.broadcast import broadcast_resolution
from app.core.notifications import send_telegram_alert

router = APIRouter()

def verify_sovereign_scope():
    # Dummy user for demo; replace with real auth logic
    return {"sub": "demo_user"}

@router.post("/remediate/whitelist")
async def whitelist_incident(
    request: Request,
    incident_id: str,
    reason: str,
    user: dict = Depends(verify_sovereign_scope)
):
    print("[DEBUG] whitelist_incident called")
    ip = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    print(f"[DEBUG] IP: {ip}, User-Agent: {user_agent}")
    try:
        log_audit_event(
            "WHITELIST",
            user.get("sub", "unknown"),
            incident_id,
            reason,
            ip=ip,
            user_agent=user_agent
        )
        print("[DEBUG] log_audit_event succeeded")
    except Exception as e:
        print(f"[ERROR] log_audit_event failed: {e}")
    msg = (
        f"*Whitelist Override Triggered*\n"
        f"Incident: `{incident_id}`\n"
        f"User: `{user.get('sub', 'unknown')}`\n"
        f"Reason: {reason}\n"
        f"IP: {ip or '-'}\n"
        f"User-Agent: {user_agent or '-'}"
    )
    try:
        send_telegram_alert(msg)
        print("[DEBUG] send_telegram_alert succeeded")
    except Exception as e:
        print(f"[ERROR] send_telegram_alert failed: {e}")
    try:
        await update_training_set(incident_id, label="FALSE_POSITIVE")
        print("[DEBUG] update_training_set succeeded")
    except Exception as e:
        print(f"[ERROR] update_training_set failed: {e}")
    try:
        await broadcast_resolution(incident_id)
        print("[DEBUG] broadcast_resolution succeeded")
    except Exception as e:
        print(f"[ERROR] broadcast_resolution failed: {e}")
    print("[DEBUG] whitelist_incident completed")
    return {"status": "whitelisted", "incident": incident_id}
