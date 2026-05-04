from typing import List, Optional
from pydantic import BaseModel, Field
import uuid
import json
import os

# Pydantic model for remediation request
class RemediationRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    action_type: str
    status: str = "PENDING"
    approvals: List[str] = Field(default_factory=list)
    required_approvals: int = 2

# Simple JSON file-based DB for demo
DB_FILE = "remediation_requests.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2)

def save_remediation(request: RemediationRequest):
    db = load_db()
    db[request.request_id] = request.dict()
    save_db(db)

def get_remediation(request_id: str) -> Optional[RemediationRequest]:
    db = load_db()
    data = db.get(request_id)
    if data:
        return RemediationRequest(**data)
    return None

def update_status(request_id: str, status: str):
    db = load_db()
    if request_id in db:
        db[request_id]["status"] = status
        save_db(db)

# Example usage:
# req = RemediationRequest(user_id="user@domain.com", action_type="reset_password")
# save_remediation(req)
# loaded = get_remediation(req.request_id)
# loaded.approvals.append("manager1")
# save_remediation(loaded)
# update_status(req.request_id, "EXECUTED")
