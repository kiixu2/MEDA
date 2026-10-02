from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Guardianship(Base):
    __tablename__ = "guardianship"

    # المفتاح الأساسي المركب (guardian_id + dependent_id)
    guardian_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        primary_key=True,
        nullable=False
    )
    dependent_id = Column(
        Integer,
        ForeignKey("users.user_id"),
        primary_key=True,
        nullable=False
    )

    relationship_type = Column(String(50), nullable=False)

    can_view_history = Column(Boolean, default=False, nullable=False)
    can_manage_medications = Column(Boolean, default=False, nullable=False)
    can_receive_notifications = Column(Boolean, default=True, nullable=False)

    status = Column(String(20), default="Pending", nullable=False)
    granted_at = Column(DateTime(timezone=True), server_default=func.now())
    revoked_at = Column(DateTime(timezone=True), nullable=True)

    # علاقات مع Users
    guardian = relationship(
        "User",
        foreign_keys=[guardian_id],
        backref="guardianships_as_guardian"
    )
    dependent = relationship(
        "User",
        foreign_keys=[dependent_id],
        backref="guardianships_as_dependent"
    )

    # قيود
    __table_args__ = (
        CheckConstraint(
            "guardian_id <> dependent_id",
            name="ck_guardianship_not_self"
        ),
        CheckConstraint(
            "status IN ('Pending', 'Active', 'Revoked')",
            name="ck_guardianship_status"
        ),
    )