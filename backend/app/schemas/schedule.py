from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime, date, time
from decimal import Decimal


class ScheduleBase(BaseModel):
    frequency_type: str
    interval_hours: Optional[int] = Field(default=None, gt=0, le=720)
    days_of_week_mask: Optional[int] = Field(default=None, ge=0, le=127)
    dose_quantity: Decimal = Field(gt=0)
    dose_unit: Optional[str] = "Tablet"
    dose_time_local: time
    start_date: date
    end_date: Optional[date] = None
    is_active: Optional[bool] = True
    notes: Optional[str] = None

    @model_validator(mode="after")
    def _check_dates(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class ScheduleCreate(ScheduleBase):
    patient_medication_id: int


class ScheduleUpdate(BaseModel):
    frequency_type: Optional[str] = None
    interval_hours: Optional[int] = Field(default=None, gt=0, le=720)
    days_of_week_mask: Optional[int] = Field(default=None, ge=0, le=127)
    dose_quantity: Optional[Decimal] = Field(default=None, gt=0)
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
