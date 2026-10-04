from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GuardianshipBase(BaseModel):
    relationship_type: str
    can_view_history: Optional[bool] = False
    can_manage_medications: Optional[bool] = False


class GuardianshipCreate(GuardianshipBase):
    dependent_patient_id: int


class GuardianshipUpdate(BaseModel):
    relationship_type: Optional[str] = None
    can_view_history: Optional[bool] = None
    can_manage_medications: Optional[bool] = None
    status: Optional[str] = None


class GuardianshipResponse(GuardianshipBase):
    guardianship_id: int
    guardian_user_id: int
    dependent_patient_id: int
    status: str
    granted_at_utc: Optional[datetime] = None
    ended_at_utc: Optional[datetime] = None

    class Config:
        from_attributes = True