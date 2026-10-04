from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, date


class UserBase(BaseModel):
    full_name: str
    username: str
    email: EmailStr
    phone_number: str
    date_of_birth: date
    gender: str


class UserCreate(UserBase):
    password: str
    role: str = "Patient"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    user_id: int
    role: str
    is_active: bool
    created_at_utc: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse