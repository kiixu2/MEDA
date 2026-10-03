from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.ai_consultation import AIConsultation
from app.models.user import User
from app.schemas.ai_consultation import AIConsultationCreate, AIConsultationResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/ai-consultations", tags=["AI Consultations"])


@router.post("", response_model=AIConsultationResponse, status_code=201)
def create_consultation(
    data: AIConsultationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    consultation = AIConsultation(user_id=current_user.user_id, **data.model_dump())
    db.add(consultation)
    db.commit()
    db.refresh(consultation)
    return consultation


@router.get("/me", response_model=List[AIConsultationResponse])
def get_my_consultations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(AIConsultation).filter(
        AIConsultation.user_id == current_user.user_id
    ).all()