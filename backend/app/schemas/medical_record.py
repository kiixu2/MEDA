from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class MedicalRecordBase(BaseModel):
    condition_name: str
    condition_type: Optional[str] = None
    diagnosed_date: Optional[date] = None
    current_status: Optional[str] = "Active"
    severity_level: Optional[str] = None
    symptoms: Optional[str] = None
    treatment_plan: Optional[str] = None
    doctor_name: Optional[str] = None
    notes: Optional[str] = None


class MedicalRecordCreate(MedicalRecordBase):
    patient_id: int


class MedicalRecordResponse(MedicalRecordBase):
    record_id: int
    patient_id: int
    created_at: datetime

    class Config:
        from_attributes = True