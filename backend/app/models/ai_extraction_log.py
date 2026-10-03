from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AIExtractionLog(Base):
    __tablename__ = "ai_extraction_logs"

    extraction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    raw_input = Column(String(4000), nullable=False)
    extracted_json = Column(String(4000), nullable=True)
    is_confirmed = Column(Boolean, default=False)
    confirmed_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    confirmed_at_utc = Column(DateTime(timezone=True), nullable=True)
    model_provider = Column(String(100), nullable=True)
    model_name = Column(String(150), nullable=True)
    model_version = Column(String(100), nullable=True)
    prompt_version = Column(String(100), nullable=True)
    created_at_utc = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", foreign_keys=[user_id], backref="ai_extractions")
    confirmed_by = relationship("User", foreign_keys=[confirmed_by_user_id])