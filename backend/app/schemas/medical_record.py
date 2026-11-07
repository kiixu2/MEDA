from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date


class MedicalRecordBase(BaseModel):
    condition: str
    patient_status: str
    severity: Optional[str] = None
    diagnosed_date: Optional[date] = None
    symptoms: Optional[str] = None
    treatment_plan: Optional[str] = None
    attachment_storage_key: Optional[str] = None


class MedicalRecordCreate(MedicalRecordBase):
    patient_id: int
    # 🛡️ تم إزالة doctor_user_id لأنه يُؤخذ من التوكن تلقائياً لضمان الأمان


class MedicalRecordResponse(MedicalRecordBase):
    record_id: int
    patient_id: int
    doctor_user_id: int
    created_by_user_id: int
    created_at_utc: datetime

    class Config:
        from_attributes = True