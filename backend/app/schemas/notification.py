from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class NotificationBase(BaseModel):
    user_id: int
    title: str
    message: str
    notification_type: Optional[str] = "Medication_Reminder"
    scheduled_for: datetime


class NotificationCreate(NotificationBase):
    dose_log_id: Optional[int] = None


class NotificationResponse(NotificationBase):
    notification_id: int
    dose_log_id: Optional[int] = None
    status: str
    sent_at: Optional[datetime] = None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True