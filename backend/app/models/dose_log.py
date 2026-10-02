from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class DoseLog(Base):
    __tablename__ = "dose_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(
        Integer,
        ForeignKey("medication_schedules.schedule_id"),
        nullable=False,
        index=True
    )
    scheduled_datetime = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(20), default="Pending", nullable=False)
    action_timestamp = Column(DateTime(timezone=True), nullable=True)
    notes = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    schedule = relationship("MedicationSchedule", backref="dose_logs")

    __table_args__ = (
        UniqueConstraint(
            "schedule_id", "scheduled_datetime",
            name="uq_dose_logs_schedule_datetime"
        ),
    )