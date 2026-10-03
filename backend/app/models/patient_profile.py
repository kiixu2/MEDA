from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    patient_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        primary_key=True,
        nullable=False
    )
    blood_type = Column(String(5), nullable=True)
    emergency_contact_name = Column(String(150), nullable=True)
    emergency_contact_phone = Column(String(30), nullable=True)
    time_zone_id = Column(String(128), default="UTC")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="patient_profile", uselist=False)