from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AIConsultation(Base):
    __tablename__ = "ai_consultations"

    consultation_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    patient_query = Column(String(4000), nullable=False)
    ai_response = Column(String(4000), nullable=False)
    disclaimer_shown = Column(Boolean, default=True)
    model_provider = Column(String(100), nullable=True)
    model_name = Column(String(150), nullable=True)
    model_version = Column(String(100), nullable=True)
    created_at_utc = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="ai_consultations")