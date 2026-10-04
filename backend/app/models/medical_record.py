from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PatientMedicalRecord(Base):
    __tablename__ = "patient_medical_records"

    record_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.patient_id"),
        nullable=False,
        index=True
    )
    doctor_user_id = Column(
        Integer,
        ForeignKey("doctors.user_id"),
        nullable=False
    )
    created_by_user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )
    condition = Column(String(200), nullable=False)
    patient_status = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=True)  # Mild | Moderate | Severe
    diagnosed_date = Column(Date, nullable=True)
    symptoms = Column(String(2000), nullable=True)
    treatment_plan = Column(String(2000), nullable=True)
    attachment_storage_key = Column(String(500), nullable=True)
    created_at_utc = Column(DateTime(timezone=True), server_default=func.now())
    updated_at_utc = Column(DateTime(timezone=True), onupdate=func.now())

    patient = relationship("PatientProfile", backref="medical_records")
    doctor = relationship("Doctor", backref="medical_records")
    created_by = relationship("User", backref="created_records")