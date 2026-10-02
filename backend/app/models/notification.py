from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    notification_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )
    dose_log_id = Column(
        Integer,
        ForeignKey("dose_logs.log_id"),
        nullable=True
    )
    title = Column(String(150), nullable=False)
    message = Column(String(500), nullable=False)
    notification_type = Column(String(50), default="Medication_Reminder")
    status = Column(String(20), default="Scheduled")
    scheduled_for = Column(DateTime(timezone=True), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", backref="notifications")
    dose_log = relationship("DoseLog", backref="notifications")