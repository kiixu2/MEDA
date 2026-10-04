from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey,
    CheckConstraint, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Guardianship(Base):
    __tablename__ = "guardianship"

    guardianship_id = Column(Integer, primary_key=True, index=True)

    guardian_user_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
        index=True
    )

    dependent_patient_id = Column(
        Integer,
        ForeignKey("patient_profiles.patient_id"),
        nullable=False,
        index=True
    )

    # الاسم في Python: relationship_type
    # الاسم في DB: relationship (عشان ما يتعارض مع دالة relationship)
    relationship_type = Column("relationship", String(50), nullable=False)

    can_manage_medications = Column(Boolean, default=False, nullable=False)
    can_view_history = Column(Boolean, default=False, nullable=False)
    status = Column(String(20), default="Pending", nullable=False)
    granted_at_utc = Column(DateTime(timezone=True), nullable=True)
    ended_at_utc = Column(DateTime(timezone=True), nullable=True)

    guardian = relationship(
        "User",
        foreign_keys=[guardian_user_id],
        backref="guardianships_as_guardian"
    )
    dependent = relationship(
        "PatientProfile",
        foreign_keys=[dependent_patient_id],
        backref="guardianships_as_dependent"
    )

    __table_args__ = (
        UniqueConstraint(
            "guardian_user_id", "dependent_patient_id",
            name="uq_guardianship_relationship"
        ),
        CheckConstraint(
            "guardian_user_id <> dependent_patient_id",
            name="ck_guardianship_different_users"
        ),
        CheckConstraint(
            "status IN ('Pending', 'Active', 'Revoked', 'Ended')",
            name="ck_guardianship_status"
        ),
    )