from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class MedicalRecordNote(Base):
    __tablename__ = "medical_record_notes"

    note_id = Column(Integer, primary_key=True, index=True)
    record_id = Column(
        Integer,
        ForeignKey("patient_medical_records.record_id"),
        nullable=False,
        index=True
    )
    note_type = Column(String(20), nullable=False)  # FollowUp | Additional
    note_text = Column(String(4000), nullable=False)
    created_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at_utc = Column(DateTime(timezone=True), server_default=func.now())

    record = relationship("PatientMedicalRecord", backref="notes")
    created_by = relationship("User", backref="record_notes")