from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PatientAllergy(Base):
    __tablename__ = "patient_allergies"

    allergy_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    allergen_name = Column(String(200), nullable=False)
    allergen_category = Column(String(100), nullable=True)
    reaction = Column(String(500), nullable=True)
    severity_level = Column(String(20), nullable=True)
    status = Column(String(20), default="Active")
    diagnosed_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("User", backref="allergies")