from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id = Column(Integer, primary_key=True, index=True)
    actor_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True, index=True)
    action_performed = Column(String(30), nullable=False)
    table_name = Column(String(128), nullable=False, index=True)
    record_id = Column(String(100), nullable=True)
    old_values_json = Column(String(2000), nullable=True)
    new_values_json = Column(String(2000), nullable=True)
    request_id = Column(String(36), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    performed_at_utc = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    actor = relationship("User", backref="audit_logs")