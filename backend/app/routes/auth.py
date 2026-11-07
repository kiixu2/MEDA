from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # تحقق من الإيميل
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    # تحقق من اسم المستخدم
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    # تحقق من الجوال
    if db.query(User).filter(User.phone_number == user_data.phone_number).first():
        raise HTTPException(status_code=400, detail="Phone already registered")

    # 🛡️ التعديل الأمني 1: نجبر أي مستخدم يسجل من التطبيق يكون "Patient" فقط
    # الأطباء والممرضين يتم إنشاؤهم عبر السكريبت أو لوحة التحكم
    new_user = User(
        full_name=user_data.full_name,
        username=user_data.username,
        email=user_data.email,
        phone_number=user_data.phone_number,
        date_of_birth=user_data.date_of_birth,
        gender=user_data.gender,
        password_hash=hash_password(user_data.password),
        role="Patient", # 👈 تم التعديل هنا
        # 🛡️ التعديل الأمني 2: إزالة last_login_at_utc من هنا لأنه لم يقم بتسجيل الدخول بعد
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    # هنا صحيح نحدث وقت الدخول
    user.last_login_at_utc = datetime.utcnow()
    db.commit()

    token = create_access_token({"sub": str(user.user_id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}