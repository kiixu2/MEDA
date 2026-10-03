from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.consent_record import ConsentRecord
from app.models.user import User
from app.schemas.consent_record import ConsentRecordCreate, ConsentRecordResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/consents", tags=["Consent Records"])


@router.post("", response_model=ConsentRecordResponse, status_code=201)
def create_consent(
    data: ConsentRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    consent = ConsentRecord(
        user_id=current_user.user_id,
        granted_at_utc=datetime.utcnow() if data.granted else None,
        revoked_at_utc=None if data.granted else datetime.utcnow(),
        **data.model_dump()
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