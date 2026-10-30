from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date, Time, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class MedicationSchedule(Base):
    __tablename__ = "medication_schedules"

    schedule_id = Column(Integer, primary_key=True, index=True)
    patient_medication_id = Column(Integer, ForeignKey("patient_medications.patient_medication_id"), nullable=False)
    
    frequency_type = Column(String(30), nullable=False)
    interval_hours = Column(Integer, nullable=True)
    days_of_week_mask = Column(Integer, nullable=True)
    dose_time_local = Column(Time, nullable=False)
    dose_quantity = Column(Numeric(10, 2), nullable=False)
    dose_unit = Column(String(20), default="Tablet")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 👇 التعديل هنا
    patient_medication = relationship("PatientMedication", back_populates="schedules")
    dose_logs = relationship("DoseLog", back_populates="schedule")