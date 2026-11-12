from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import MAX_FAILED_LOGINS, LOCKOUT_MINUTES
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from app.utils.clock import utcnow
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    email = user_data.email.lower()

    if db.query(User).filter(func.lower(User.email) == email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.phone_number == user_data.phone_number).first():
        raise HTTPException(status_code=400, detail="Phone already registered")

    # 🛡️ التسجيل العام ينتج Patient فقط
    new_user = User(
        full_name=user_data.full_name,
        username=user_data.username,
        email=email,
        phone_number=user_data.phone_number,
        date_of_birth=user_data.date_of_birth,
        gender=user_data.gender,
        password_hash=hash_password(user_data.password),
        role="Patient",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        func.lower(User.email) == credentials.email.lower()
    ).first()

    now = utcnow()

    # 🛡️ قفل الحساب المؤقت بعد محاولات فاشلة متكررة
    if user and user.locked_until_utc and user.locked_until_utc > now:
        raise HTTPException(
            status_code=423,
            detail="Account temporarily locked due to repeated failed logins. Try again later."
        )

    if not user or not verify_password(credentials.password, user.password_hash):
        if user:
            user.failed_login_count = (user.failed_login_count or 0) + 1
            user.last_failed_login_at_utc = now
            if user.failed_login_count >= MAX_FAILED_LOGINS:
                user.locked_until_utc = now + timedelta(minutes=LOCKOUT_MINUTES)
                user.failed_login_count = 0
            db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")

    user.failed_login_count = 0
    user.locked_until_utc = None
    user.last_login_at_utc = now
    db.commit()

    token = create_access_token({"sub": str(user.user_id), "role": user.role})
    return {"access_token": token, "token_type": "bearer", "user": user}
