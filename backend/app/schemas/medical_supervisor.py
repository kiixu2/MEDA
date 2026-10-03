from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MedicalSupervisorBase(BaseModel):
    doctor_user_id: int
    patient_id: int
    status: Optional[str] = "Active"
    notes: Optional[str] = None


class MedicalSupervisorCreate(MedicalSupervisorBase):
    pass


class MedicalSupervisorResponse(MedicalSupervisorBase):
    supervisor_id: int
    assigned_at_utc: datetime
    ended_at_utc: Optional[datetime] = None

    class Config:
        from_attributes = True