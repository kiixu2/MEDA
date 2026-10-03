from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.notification import Notification
from app.schemas.notification import (
    NotificationCreate, NotificationResponse
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.post("", response_model=NotificationResponse, status_code=201)
def create_notification(data: NotificationCreate, db: Session = Depends(get_db)):
    new_notif = Notification(**data.model_dump())
    db.add(new_notif)
    db.commit()
    db.refresh(new_notif)
    return new_notif


@router.get("", response_model=List[NotificationResponse])
def get_all_notifications(db: Session = Depends(get_db)):
    return db.query(Notification).all()


@router.get("/user/{user_id}", response_model=List[NotificationResponse])
def get_user_notifications(user_id: int, db: Session = Depends(get_db)):
    return db.query(Notification).filter(Notification.user_id == user_id).all()


@router.post("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(notification_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(
        Notification.notification_id == notification_id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    notif.status = "Read"
    db.commit()
    db.refresh(notif)
    return notif


@router.delete("/{notification_id}", status_code=204)
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(
        Notification.notification_id == notification_id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notif)
    db.commit()
    return None