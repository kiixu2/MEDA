from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentResponse
from app.utils.permissions import (
    require_patient_access, get_patient_profile_or_404, MANAGE_MEDICATIONS
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/appointments", tags=["Appointments"])


@router.post("", response_model=AppointmentResponse, status_code=201)
def create_appointment(
    data: AppointmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """المريض نفسه، أو وصي بصلاحية، أو طبيب مشرف يحجز موعداً."""
    get_patient_profile_or_404(db, data.patient_id)
    require_patient_access(current_user, data.patient_id, MANAGE_MEDICATIONS, db)

    # الطبيب الذي يحجز يحجز لنفسه فقط
    doctor_id = current_user.user_id if current_user.role == "Doctor" else data.doctor_user_id
    if not db.query(Doctor).filter(Doctor.user_id == doctor_id).first():
        raise HTTPException(status_code=404, detail="Doctor not found")

    new_app = Appointment(
        patient_id=data.patient_id,
        doctor_user_id=doctor_id,
        appointment_date=data.appointment_date,
        notes=data.notes,
        status="Scheduled",
    )
    db.add(new_app)
    db.commit()
    db.refresh(new_app)
    return new_app


@router.get("/my-appointments", response_model=List[AppointmentResponse])
def get_my_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Appointment).filter(
        Appointment.patient_id == current_user.user_id
    ).order_by(Appointment.appointment_date).all()


@router.get("/doctor/me", response_model=List[AppointmentResponse])
def get_my_doctor_appointments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """مواعيد الطبيب (التي حُجزت معه)."""
    return db.query(Appointment).filter(
        Appointment.doctor_user_id == current_user.user_id
    ).order_by(Appointment.appointment_date).all()
