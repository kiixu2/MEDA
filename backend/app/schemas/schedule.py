from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, time
from decimal import Decimal

class ScheduleBase(BaseModel):
    frequency_type: str
    dose_quantity: Decimal
    dose_unit: Optional[str] = "Tablet"
    dose_time_local: time  # 👈 هنا التعديل
    start_date: date
    end_date: Optional[date] = None
    is_active: Optional[bool] = True
    notes: Optional[str] = None

class ScheduleCreate(ScheduleBase):
    patient_medication_id: int

class ScheduleUpdate(BaseModel):
    frequency_type: Optional[str] = None
    dose_quantity: Optional[Decimal] = None
    dose_unit: Optional[str] = None
    dose_time_local: Optional[time] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class ScheduleResponse(ScheduleBase):
    schedule_id: int
    patient_medication_id: int
    created_at: datetime

    class Config:
        from_attributes = True