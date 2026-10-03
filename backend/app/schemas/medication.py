from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class MedicationBase(BaseModel):
    name: str
    dosage_form: str
    total_quantity: Optional[Decimal] = 0
    refill_threshold: Optional[Decimal] = 5


class MedicationCreate(MedicationBase):
    patient_id: int


class MedicationUpdate(BaseModel):
    name: Optional[str] = None
    dosage_form: Optional[str] = None
    total_quantity: Optional[Decimal] = None
    refill_threshold: Optional[Decimal] = None


class MedicationResponse(MedicationBase):
    medication_id: int
    patient_id: int
    created_at: datetime

    class Config:
        from_attributes = True