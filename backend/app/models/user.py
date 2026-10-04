from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(150), nullable=False)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(254), unique=True, nullable=False, index=True)
    phone_number = Column(String(30), unique=True, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(String(20), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="Patient")
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    phone_verified = Column(Boolean, default=False)
    failed_login_count = Column(Integer, default=0)
    locked_until_utc = Column(DateTime(timezone=True), nullable=True)
    last_login_at_utc = Column(DateTime(timezone=True), nullable=True)
    last_failed_login_at_utc = Column(DateTime(timezone=True), nullable=True)
    created_at_utc = Column(DateTime(timezone=True), server_default=func.now())
    updated_at_utc = Column(DateTime(timezone=True), onupdate=func.now())