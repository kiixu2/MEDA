from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    appointment_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patient_profiles.patient_id"), nullable=False)
    doctor_user_id = Column(Integer, ForeignKey("doctors.user_id"), nullable=False)
    appointment_date = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="Scheduled") # Scheduled, Completed, Cancelled
    notes = Column(String(500), nullable=True)
    created_at_utc = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    patient = relationship("PatientProfile", backref="appointments")
    doctor = relationship("Doctor", backref="appointments")