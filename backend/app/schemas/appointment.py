from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AppointmentBase(BaseModel):
    patient_id: int
    doctor_user_id: int
    appointment_date: datetime
    status: Optional[str] = "Scheduled"
    notes: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class AppointmentResponse(AppointmentBase):
    appointment_id: int
    created_at_utc: datetime

    class Config:
        from_attributes = True