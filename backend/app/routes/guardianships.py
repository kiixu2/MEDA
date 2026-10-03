from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.guardianship import Guardianship
from app.models.user import User
from app.schemas.guardianship import (
    GuardianshipCreate, GuardianshipUpdate, GuardianshipResponse
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/guardianships", tags=["Guardianship"])


@router.post("", response_model=GuardianshipResponse, status_code=201)
def create_guardianship(
    data: GuardianshipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # نتأكد إن المريض موجود
    dependent = db.query(User).filter(User.user_id == data.dependent_id).first()
    if not dependent:
        raise HTTPException(status_code=404, detail="Dependent user not found")
    
    # منع الوصاية الذاتية
    if data.dependent_id == current_user.user_id:
        raise HTTPException(
            status_code=400,
            detail="You can't be guardian of yourself"
        )
    
    # نتأكد ما فيه guardianship موجود
    existing = db.query(Guardianship).filter(
        Guardianship.guardian_id == current_user.user_id,
        Guardianship.dependent_id == data.dependent_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Guardianship already exists"
        )
    
    new_g = Guardianship(
        guardian_id=current_user.user_id,
        dependent_id=data.dependent_id,
        relationship_type=data.relationship_type,
        can_view_history=data.can_view_history,
        can_manage_medications=data.can_manage_medications,
        can_receive_notifications=data.can_receive_notifications,
        status="Active"
    )
    db.add(new_g)
    db.commit()
    db.refresh(new_g)
    return new_g


@router.get("/my-patients", response_model=List[GuardianshipResponse])
def get_my_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """كل المرضى اللي أنا وصي عليهم"""
    return db.query(Guardianship).filter(
        Guardianship.guardian_id == current_user.user_id,
        Guardianship.status == "Active"
    ).all()


@router.get("/my-guardians", response_model=List[GuardianshipResponse])
def get_my_guardians(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """كل الأوصياء اللي يتابعوني"""
    return db.query(Guardianship).filter(
        Guardianship.dependent_id == current_user.user_id,
        Guardianship.status == "Active"
    ).all()


@router.put("/{dependent_id}", response_model=GuardianshipResponse)
def update_guardianship(
    dependent_id: int,
    data: GuardianshipUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    g = db.query(Guardianship).filter(
        Guardianship.guardian_id == current_user.user_id,
        Guardianship.dependent_id == dependent_id
    ).first()
    if not g:
        raise HTTPException(status_code=404, detail="Guardianship not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(g, key, value)

    db.commit()
    db.refresh(g)
    return g


@router.delete("/{dependent_id}", status_code=204)
def revoke_guardianship(
    dependent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    g = db.query(Guardianship).filter(
        Guardianship.guardian_id == current_user.user_id,
        Guardianship.dependent_id == dependent_id
    ).first()
    if not g:
        raise HTTPException(status_code=404, detail="Guardianship not found")
    
    g.status = "Revoked"
    from datetime import datetime
    g.revoked_at = datetime.utcnow()
    db.commit()
    return None