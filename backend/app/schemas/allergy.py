from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class AllergyBase(BaseModel):
    allergen_name: str
    allergen_category: Optional[str] = None
    reaction: Optional[str] = None
    severity_level: Optional[str] = None
    status: Optional[str] = "Active"
    diagnosed_date: Optional[date] = None


class AllergyCreate(AllergyBase):
    patient_id: int


class AllergyResponse(AllergyBase):
    allergy_id: int
    patient_id: int
    created_at: datetime

    class Config:
        from_attributes = True