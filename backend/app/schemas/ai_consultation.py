from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AIConsultationBase(BaseModel):
    patient_query: str
    ai_response: str
    disclaimer_shown: Optional[bool] = True


class AIConsultationCreate(AIConsultationBase):
    pass


class AIConsultationResponse(AIConsultationBase):
    consultation_id: int
    user_id: int
    created_at_utc: datetime

    class Config:
        from_attributes = True