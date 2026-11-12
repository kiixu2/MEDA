from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date


class UserBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    phone_number: str = Field(min_length=5, max_length=30)
    date_of_birth: date
    gender: str = Field(max_length=20)


class UserCreate(UserBase):
    # 🛡️ لا يوجد role هنا: كل من يسجل من التطبيق يصبح Patient.
    # الأطباء/الممرضين/الأدمن يُنشؤون عبر seed_db.py أو لوحة إدارة.
    password: str = Field(min_length=8, max_length=128)


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
