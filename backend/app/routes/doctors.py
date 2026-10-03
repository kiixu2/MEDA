from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.doctor import DoctorCreate, DoctorResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post("", response_model=DoctorResponse, status_code=201)
def create_doctor_profile(
    data: DoctorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "Doctor":
        raise HTTPException(status_code=403, detail="Only doctors can create this profile")

    existing = db.query(Doctor).filter(Doctor.user_id == current_user.user_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Doctor profile already exists")

    doctor = Doctor(user_id=current_user.user_id, **data.model_dump())
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("", response_model=List[DoctorResponse])
def get_all_doctors(db: Session = Depends(get_db)):
    return db.query(Doctor).all()


@router.get("/me", response_model=DoctorResponse)
def get_my_doctor_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.user_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    return doctor