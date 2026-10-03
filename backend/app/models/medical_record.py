from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PatientMedicalRecord(Base):
    __tablename__ = "patient_medical_records"

    record_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    condition_name = Column(String(200), nullable=False)
    condition_type = Column(String(50), nullable=True)
    diagnosed_date = Column(Date, nullable=True)
    current_status = Column(String(30), default="Active")
    severity_level = Column(String(20), nullable=True)
    symptoms = Column(String(1000), nullable=True)
    treatment_plan = Column(String(1000), nullable=True)
    doctor_name = Column(String(100), nullable=True)
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    patient = relationship("User", backref="medical_records")