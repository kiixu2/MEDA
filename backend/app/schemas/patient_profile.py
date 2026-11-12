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
    assigned_nurse_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class NurseAssign(BaseModel):
    """المريض يعيّن ممرضاً مسؤولاً عنه (هذا يمنح الممرض صلاحية الوصول)."""
    nurse_user_id: int
