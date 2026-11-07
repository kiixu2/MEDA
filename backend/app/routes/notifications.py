from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import (
    NotificationCreate, NotificationResponse
)
from app.utils.security import get_current_user, require_roles

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("", response_model=NotificationResponse, status_code=201)
def create_notification(
    data: NotificationCreate,
    # 🛡️ التعديل الأمني: فقط الطبيب والممرض والأدمن يمكنهم إنشاء إشعار لمستخدم
    current_user: User = Depends(require_roles(["Admin", "Doctor", "Nurse"])),
    db: Session = Depends(get_db)
):
    new_notif = Notification(**data.model_dump())
    db.add(new_notif)
    db.commit()
    db.refresh(new_notif)
    return new_notif


@router.get("", response_model=List[NotificationResponse])
def get_my_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # المريض أو أي مستخدم يشوف إشعاراته فقط
    return db.query(Notification).filter(
        Notification.user_id == current_user.user_id
    ).all()


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(
        Notification.notification_id == notification_id,
        Notification.user_id == current_user.user_id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    notif.is_read = True
    notif.status = "Read"
    db.commit()
    db.refresh(notif)
    return notif


@router.delete("/{notification_id}", status_code=204)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    notif = db.query(Notification).filter(
        Notification.notification_id == notification_id,
        Notification.user_id == current_user.user_id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    db.delete(notif)
    db.commit()
    return None