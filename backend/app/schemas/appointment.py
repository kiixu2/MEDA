from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AppointmentCreate(BaseModel):
    patient_id: int
    doctor_user_id: int
    appointment_date: datetime
    notes: Optional[str] = None


class AppointmentResponse(BaseModel):
    appointment_id: int
    patient_id: int
    doctor_user_id: int
    appointment_date: datetime
    status: Optional[str] = None
    notes: Optional[str] = None
    created_at_utc: datetime

    class Config:
        from_attributes = True
