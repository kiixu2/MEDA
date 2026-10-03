from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AuditLogBase(BaseModel):
    action_performed: str
    table_name: str
    record_id: Optional[str] = None
    old_values_json: Optional[str] = None
    new_values_json: Optional[str] = None
    ip_address: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    audit_id: int
    actor_user_id: Optional[int] = None
    performed_at_utc: datetime

    class Config:
        from_attributes = True