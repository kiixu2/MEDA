from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.ai_extraction_log import AIExtractionLog
from app.models.user import User
from app.schemas.ai_extraction_log import AIExtractionLogCreate, AIExtractionLogResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/ai-extractions", tags=["AI Extraction"])


@router.post("", response_model=AIExtractionLogResponse, status_code=201)
def create_extraction(
    data: AIExtractionLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = AIExtractionLog(user_id=current_user.user_id, **data.model_dump())
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


@router.get("/me", response_model=List[AIExtractionLogResponse])
def get_my_extractions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(AIExtractionLog).filter(
        AIExtractionLog.user_id == current_user.user_id
    ).all()