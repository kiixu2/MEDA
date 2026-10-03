from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PatientMedication(Base):
    __tablename__ = "patient_medications"

    patient_medication_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.patient_id"), nullable=False, index=True)
    medication_id = Column(Integer, ForeignKey("medication_catalog.medication_id"), nullable=False)
    prescribed_by_doctor_id = Column(Integer, ForeignKey("doctors.user_id"), nullable=True)
    prescribed_quantity = Column(Numeric(12, 3), nullable=True)
    quantity_on_hand = Column(Numeric(12, 3), nullable=False, default=0)
    low_stock_threshold = Column(Numeric(12, 3), nullable=False, default=0)
    instructions = Column(String(1000), nullable=True)
    notes = Column(String(1000), nullable=True)
    status = Column(String(20), nullable=False, default="Active")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    created_at_utc = Column(DateTime(timezone=True), server_default=func.now())
    updated_at_utc = Column(DateTime(timezone=True), onupdate=func.now())

    patient = relationship("PatientProfile", backref="patient_medications")
    prescriber = relationship("Doctor", backref="prescribed_medications")
    schedules = relationship("MedicationSchedule", backref="patient_medication")
    