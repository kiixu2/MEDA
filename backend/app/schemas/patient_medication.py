from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class PatientMedicationBase(BaseModel):
    patient_id: int
    medication_id: int
    # 🛡️ تم إزالة prescribed_by_doctor_id من هنا عشان منع الانتحال
    prescribed_quantity: Optional[Decimal] = None
    quantity_on_hand: Optional[Decimal] = 0
    low_stock_threshold: Optional[Decimal] = 0
    instructions: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "Active"
    start_date: date
    end_date: Optional[date] = None


class PatientMedicationCreate(PatientMedicationBase):
    pass


class PatientMedicationResponse(PatientMedicationBase):
    patient_medication_id: int
    prescribed_by_doctor_id: Optional[int] = None # 👈 يظهر هنا فقط للعرض
    created_at_utc: datetime

    class Config:
        from_attributes = True