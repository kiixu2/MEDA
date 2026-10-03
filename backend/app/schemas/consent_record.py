from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConsentRecordBase(BaseModel):
    consent_type: str
    policy_version: str
    granted: bool


class ConsentRecordCreate(ConsentRecordBase):
    pass


class ConsentRecordResponse(ConsentRecordBase):
    consent_id: int
    user_id: int
    granted_at_utc: Optional[datetime] = None
    revoked_at_utc: Optional[datetime] = None
    created_at_utc: datetime

    class Config:
        from_attributes = True