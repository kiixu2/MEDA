from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.nurse import Nurse
from app.models.user import User
from app.schemas.nurse import NurseCreate, NurseResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/nurses", tags=["Nurses"])


@router.post("", response_model=NurseResponse, status_code=201)
def create_nurse_profile(
    data: NurseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "Nurse":
        raise HTTPException(status_code=403, detail="Only nurses can create this profile")
    existing = db.query(Nurse).filter(Nurse.user_id == current_user.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Nurse profile already exists")
    nurse = Nurse(user_id=current_user.user_id, **data.model_dump())
    db.add(nurse)
    db.commit()
    db.refresh(nurse)
    return nurse


@router.get("", response_model=List[NurseResponse])
def get_all_nurses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Nurse).all()


@router.get("/me", response_model=NurseResponse)
def get_my_nurse_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    nurse = db.query(Nurse).filter(Nurse.user_id == current_user.user_id).first()
    if not nurse:
        raise HTTPException(status_code=404, detail="Nurse profile not found")
    return nurse