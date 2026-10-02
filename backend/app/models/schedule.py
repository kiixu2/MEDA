from sqlalchemy import (
    Column, Integer, String, Numeric, Boolean, Date, Time,
    DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class MedicationSchedule(Base):
    __tablename__ = "medication_schedules"

    schedule_id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(
        Integer,
        ForeignKey("medications.medication_id"),
        nullable=False,
        index=True
    )
    frequency_type = Column(String(30), nullable=False)  # Daily, Weekly, etc.
    dose_quantity = Column(Numeric(10, 2), nullable=False)
    dose_unit = Column(String(20), default="Tablet")
    dose_time = Column(Time, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    medication = relationship("Medication", backref="schedules")