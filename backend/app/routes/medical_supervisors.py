from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.medical_supervisor import MedicalSupervisor
from app.models.user import User
from app.schemas.medical_supervisor import MedicalSupervisorCreate, MedicalSupervisorResponse
from app.utils.security import get_current_user

router = APIRouter(prefix="/medical-supervisors", tags=["Medical Supervisors"])


@router.post("", response_model=MedicalSupervisorResponse, status_code=201)
def create_supervisor(
    data: MedicalSupervisorCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "Doctor":
        raise HTTPException(status_code=403, detail="Only doctors can supervise")
    supervisor = MedicalSupervisor(**data.model_dump())
    db.add(supervisor)
    db.commit()
    db.refresh(supervisor)
    return supervisor


@router.get("/my-patients", response_model=List[MedicalSupervisorResponse])
def get_my_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(MedicalSupervisor).filter(
        MedicalSupervisor.doctor_user_id == current_user.user_id,
        MedicalSupervisor.status == "Active"
    ).all()


@router.get("/my-doctors", response_model=List[MedicalSupervisorResponse])
def get_my_doctors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(MedicalSupervisor).filter(
        MedicalSupervisor.patient_id == current_user.user_id,
        MedicalSupervisor.status == "Active"
    ).all()