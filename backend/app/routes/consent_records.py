from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.consent_record import ConsentRecord
from app.models.user import User
from app.schemas.consent_record import ConsentRecordCreate, ConsentRecordResponse
from app.utils.clock import utcnow
from app.utils.security import get_current_user

router = APIRouter(prefix="/consents", tags=["Consent Records"])


@router.post("", response_model=ConsentRecordResponse, status_code=201)
def create_consent(
    data: ConsentRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """منح أو سحب موافقة. القيد الفريد (user, type, version) يعني أن تغيير القرار يحدّث السجل نفسه."""
    now = utcnow()
    consent = db.query(ConsentRecord).filter(
        ConsentRecord.user_id == current_user.user_id,
        ConsentRecord.consent_type == data.consent_type,
        ConsentRecord.policy_version == data.policy_version,
    ).first()

    if consent:
        consent.granted = data.granted
        if data.granted:
            consent.granted_at_utc = now
            consent.revoked_at_utc = None
        else:
            consent.revoked_at_utc = now
    else:
        consent = ConsentRecord(
            user_id=current_user.user_id,
            consent_type=data.consent_type,
            policy_version=data.policy_version,
            granted=data.granted,
            granted_at_utc=now if data.granted else None,
            revoked_at_utc=None if data.granted else now,
        )
        db.add(consent)

    db.commit()
    db.refresh(consent)
    return consent


@router.get("/me", response_model=List[ConsentRecordResponse])
def get_my_consents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(ConsentRecord).filter(
        ConsentRecord.user_id == current_user.user_id
    ).all()
