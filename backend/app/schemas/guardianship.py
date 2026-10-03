from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class GuardianshipBase(BaseModel):
    relationship_type: str
    can_view_history: Optional[bool] = False
    can_manage_medications: Optional[bool] = False
    can_receive_notifications: Optional[bool] = True


class GuardianshipCreate(GuardianshipBase):
    dependent_id: int  # المريض اللي الوصي يبي يتابعه


class GuardianshipUpdate(BaseModel):
    relationship_type: Optional[str] = None
    can_view_history: Optional[bool] = None
    can_manage_medications: Optional[bool] = None
    can_receive_notifications: Optional[bool] = None
    status: Optional[str] = None


class GuardianshipResponse(GuardianshipBase):
    guardian_id: int
    dependent_id: int
    status: str
    granted_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None

    class Config:
        from_attributes = True