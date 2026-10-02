from sqlalchemy import (
    Column, Integer, String, Numeric, DateTime, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Medication(Base):
    __tablename__ = "medications"

    medication_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )
    name = Column(String(100), nullable=False)
    dosage_form = Column(String(50), nullable=False)
    total_quantity = Column(Numeric(10, 2), default=0)
    refill_threshold = Column(Numeric(10, 2), default=5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    patient = relationship("User", backref="medications")