from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.patient_profile import PatientProfile
from app.models.user import User
from app.schemas.patient_profile import PatientProfileCreate, PatientProfileResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/patient-profiles", tags=["Patient Profiles"])


@router.post("", response_model=PatientProfileResponse, status_code=201)
def create_profile(
    data: PatientProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = db.query(PatientProfile).filter(
        PatientProfile.patient_id == current_user.user_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Profile already exists")

    profile = PatientProfile(
        patient_id=current_user.user_id,
        **data.model_dump()
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


@router.get("/me", response_model=PatientProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(PatientProfile).filter(
        PatientProfile.patient_id == current_user.user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/me", response_model=PatientProfileResponse)
def update_my_profile(
    data: PatientProfileCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(PatientProfile).filter(
        PatientProfile.patient_id == current_user.user_id
    ).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)
    return profile