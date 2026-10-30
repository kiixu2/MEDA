from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.appointment import Appointment
from app.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.utils.security import get_current_user, require_roles
from app.utils.permissions import require_patient_access

router = APIRouter(prefix="/appointments", tags=["Appointments"])

@router.post("", response_model=AppointmentResponse, status_code=201)
def create_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(require_roles(["Doctor", "Caregiver"])), # الطبيب أو الوصي
    db: Session = Depends(get_db)
):
    if current_user.role == "Caregiver":
         require_patient_access(current_user, data.patient_id, "manage_medications", db)

    new_app = Appointment(**data.model_dump())
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app

@router.get("/my-appointments", response_model=List[AppointmentResponse])
def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Appointment).filter(Appointment.patient_id == current_user.user_id).all()