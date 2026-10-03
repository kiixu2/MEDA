from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    consent_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False, index=True)
    consent_type = Column(String(30), nullable=False)
    policy_version = Column(String(50), nullable=False)
    granted = Column(Boolean, nullable=False, default=False)
    granted_at_utc = Column(DateTime(timezone=True), nullable=True)
    revoked_at_utc = Column(DateTime(timezone=True), nullable=True)
    created_at_utc = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="consents")

    __table_args__ = (
        UniqueConstraint("user_id", "consent_type", "policy_version",
                         name="uq_consent_user_type_version"),
    )