from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MedicalSupervisorCreate(BaseModel):
    """الطبيب يطلب الإشراف على مريض (doctor_user_id يؤخذ من التوكن)."""
    patient_id: int
    notes: Optional[str] = None


class MedicalSupervisorResponse(BaseModel):
    supervisor_id: int
    doctor_user_id: int
    patient_id: int
    status: Optional[str] = None
    notes: Optional[str] = None
    assigned_at_utc: datetime
    ended_at_utc: Optional[datetime] = None

    class Config:
        from_attributes = True
