from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PatientProfileBase(BaseModel):
    blood_type: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    time_zone_id: Optional[str] = "UTC"


class PatientProfileCreate(PatientProfileBase):
    pass


class PatientProfileResponse(PatientProfileBase):
    patient_id: int
    created_at: datetime

    class Config:
        from_attributes = True