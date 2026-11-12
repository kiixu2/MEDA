from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DoseLogCreate(BaseModel):
    """الحالة تبدأ دائماً Pending - لا تُقبل من العميل."""
    schedule_id: int
    scheduled_datetime: datetime
    notes: Optional[str] = None


class DoseLogUpdate(BaseModel):
    status: Optional[str] = None
    action_timestamp: Optional[datetime] = None
    notes: Optional[str] = None


class DoseLogResponse(BaseModel):
    log_id: int
    schedule_id: int
    scheduled_datetime: datetime
    status: str
    notes: Optional[str] = None
    action_timestamp: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
