from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Nurse(Base):
    __tablename__ = "nurses"

    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        primary_key=True,
        nullable=False
    )
    license_number = Column(String(100), unique=True, nullable=False)
    department = Column(String(150), nullable=True)
    hospital_clinic_name = Column(String(200), nullable=True)
    verification_status = Column(String(20), default="Pending")
    created_at_utc = Column(DateTime(timezone=True), server_default=func.now())
    updated_at_utc = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="nurse_profile", uselist=False)