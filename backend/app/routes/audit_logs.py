from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.audit_log import AuditLog
from app.models.user import User
from app.schemas.audit_log import AuditLogResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


@router.get("/me", response_model=List[AuditLogResponse])
def get_my_audit_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(AuditLog).filter(
        AuditLog.actor_user_id == current_user.user_id
    ).order_by(AuditLog.performed_at_utc.desc()).limit(100).all()