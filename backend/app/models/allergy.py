from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PatientAllergy(Base):
    __tablename__ = "patient_allergies"

    allergy_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.patient_id"),
        nullable=False,
        index=True
    )
    allergen = Column(String(200), nullable=False)
    allergy_category = Column(String(100), nullable=True)
    allergy_status_severity = Column(String(50), nullable=False)
    reaction = Column(String(500), nullable=True)
    diagnosed_date = Column(Date, nullable=True)
    added_by_user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False
    )
    created_at_utc = Column(DateTime(timezone=True), server_default=func.now())
    updated_by_user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=True
    )
    updated_at_utc = Column(DateTime(timezone=True), onupdate=func.now())

    patient = relationship("PatientProfile", backref="allergies")
    added_by = relationship("User", foreign_keys=[added_by_user_id])
    updated_by = relationship("User", foreign_keys=[updated_by_user_id])