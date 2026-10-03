from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class MedicalSupervisor(Base):
    __tablename__ = "medical_supervisors"

    supervisor_id = Column(Integer, primary_key=True, index=True)
    doctor_user_id = Column(Integer, ForeignKey("doctors.user_id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patient_profiles.patient_id"), nullable=False)
    status = Column(String(20), default="Active")
    assigned_at_utc = Column(DateTime(timezone=True), server_default=func.now())
    ended_at_utc = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String(500), nullable=True)

    doctor = relationship("Doctor", backref="supervisions")
    patient = relationship("PatientProfile", backref="supervisors")