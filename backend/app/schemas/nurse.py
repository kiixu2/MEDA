from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NurseBase(BaseModel):
    license_number: str
    department: Optional[str] = None
    hospital_clinic_name: Optional[str] = None


class NurseCreate(NurseBase):
    pass


class NurseResponse(NurseBase):
    user_id: int
    verification_status: str
    created_at_utc: datetime

    class Config:
        from_attributes = True