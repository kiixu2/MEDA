from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DoctorBase(BaseModel):
    license_number: str
    specialty: str
    hospital_clinic_name: Optional[str] = None


class DoctorCreate(DoctorBase):
    pass


class DoctorResponse(DoctorBase):
    user_id: int
    verification_status: str
    created_at: datetime

    class Config:
        from_attributes = True