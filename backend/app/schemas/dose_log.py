from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DoseLogBase(BaseModel):
    schedule_id: int
    scheduled_datetime: datetime
    status: Optional[str] = "Pending"
    notes: Optional[str] = None


class DoseLogCreate(DoseLogBase):
    pass


class DoseLogUpdate(BaseModel):
    status: Optional[str] = None
    action_timestamp: Optional[datetime] = None
    notes: Optional[str] = None


class DoseLogResponse(DoseLogBase):
    log_id: int
    action_timestamp: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True