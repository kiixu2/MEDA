from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class AllergyBase(BaseModel):
    allergen: str
    allergy_category: Optional[str] = None
    allergy_status_severity: str
    reaction: Optional[str] = None
    diagnosed_date: Optional[date] = None


class AllergyCreate(AllergyBase):
    patient_id: int


class AllergyResponse(AllergyBase):
    allergy_id: int
    patient_id: int
    added_by_user_id: int
    updated_by_user_id: Optional[int] = None
    created_at_utc: datetime

    class Config:
        from_attributes = True