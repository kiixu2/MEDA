from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date, time
from decimal import Decimal


class ScheduleBase(BaseModel):
    frequency_type: str
    dose_quantity: Decimal
    dose_unit: Optional[str] = "Tablet"
    dose_time: time
    start_date: date
    end_date: Optional[date] = None
    is_active: Optional[bool] = True


class ScheduleCreate(ScheduleBase):
    medication_id: int


class ScheduleUpdate(BaseModel):
    frequency_type: Optional[str] = None
    dose_quantity: Optional[Decimal] = None
    dose_unit: Optional[str] = None
    dose_time: Optional[time] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class ScheduleResponse(ScheduleBase):
    schedule_id: int
    medication_id: int
    created_at: datetime

    class Config:
        from_attributes = True