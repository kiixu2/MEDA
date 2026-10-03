from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AIExtractionLogBase(BaseModel):
    raw_input: str
    extracted_json: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None


class AIExtractionLogCreate(AIExtractionLogBase):
    pass


class AIExtractionLogResponse(AIExtractionLogBase):
    extraction_id: int
    user_id: int
    is_confirmed: bool
    created_at_utc: datetime

    class Config:
        from_attributes = True
        