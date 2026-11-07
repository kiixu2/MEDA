from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date
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
    if data.dependent_patient_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Can't be guardian of yourself")

    # التأكد إن المريض موجود
    dependent = db.query(User).filter(User.user_id == data.dependent_patient_id).first()
    if not dependent:
        raise HTTPException(status_code=404, detail="Patient not found")

    existing = db.query(Guardianship).filter(
        Guardianship.guardian_user_id == current_user.user_id,
        Guardianship.dependent_patient_id == data.dependent_patient_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Guardianship request already exists")

    # 💡 الحل الذكي: حساب العمر لتحديد إذا كان قاصراً (طفل)
    today = date.today()
    age = today.year - dependent.date_of_birth.year - ((today.month, today.day) < (dependent.date_of_birth.month, dependent.date_of_birth.day))
    
    is_minor = age < 18

    # 🛡️ التعديل الأمني: إذا كان قاصر، نعطيها Active (لأنه ما عنده حساب). إذا بالغ، نعطيها Pending.
    new_g = Guardianship(
        guardian_user_id=current_user.user_id,
        dependent_patient_id=data.dependent_patient_id,
        relationship_type=data.relationship_type,
        can_view_history=True if is_minor else False,
        can_manage_medications=True if is_minor else False,
        status="Active" if is_minor else "Pending",
        granted_at_utc=datetime.utcnow() if is_minor else None
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
    return db.query(Guardianship).filter(
        Guardianship.guardian_user_id == current_user.user_id,
        Guardianship.status == "Active"
    ).all()


@router.get("/my-guardians", response_model=List[GuardianshipResponse])
def get_my_guardians(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Guardianship).filter(
        Guardianship.dependent_patient_id == current_user.user_id,
        Guardianship.status == "Active"
    ).all()

@router.get("/pending-requests", response_model=List[GuardianshipResponse])
def get_pending_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # للمريض البالغ: عرض طلبات الوصاية اللي ينتظر موافقته
    return db.query(Guardianship).filter(
        Guardianship.dependent_patient_id == current_user.user_id,
        Guardianship.status == "Pending"
    ).all()


@router.put("/{guardianship_id}/approve", response_model=GuardianshipResponse)
def approve_guardianship(
    guardianship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 🛡️ التعديل: المريض البالغ فقط هو من يوافق
    g = db.query(Guardianship).filter(
        Guardianship.guardianship_id == guardianship_id,
        Guardianship.dependent_patient_id == current_user.user_id,
        Guardianship.status == "Pending"
    ).first()
    if not g:
        raise HTTPException(status_code=404, detail="Pending request not found or unauthorized")

    g.status = "Active"
    g.can_view_history = True
    g.can_manage_medications = True
    g.granted_at_utc = datetime.utcnow()
    db.commit()
    db.refresh(g)
    return g


@router.put("/{guardianship_id}", response_model=GuardianshipResponse)
def update_guardianship(
    guardianship_id: int,
    data: GuardianshipUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 🛡️ التعديل: الوصي يقدر يعدل نوع العلاقة أو صلاحية معينة، لكن ممنوع يغير الـ Status
    g = db.query(Guardianship).filter(
        Guardianship.guardianship_id == guardianship_id,
        Guardianship.guardian_user_id == current_user.user_id
    ).first()
    if not g:
        raise HTTPException(status_code=404, detail="Guardianship not found")

    # إزالة الـ status من التحديث عشان ما يقدر الوصي يفعّل نفسه
    update_data = data.model_dump(exclude_unset=True)
    update_data.pop("status", None) 

    for key, value in update_data.items():
        setattr(g, key, value)

    db.commit()
    db.refresh(g)
    return g


@router.delete("/{guardianship_id}", status_code=204)
def revoke_guardianship(
    guardianship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 🛡️ التعديل: المريض أو الوصي يمديهم يلغون العلاقة
    g = db.query(Guardianship).filter(
        Guardianship.guardianship_id == guardianship_id
    ).first()
    
    if not g:
        raise HTTPException(status_code=404, detail="Guardianship not found")

    if current_user.user_id not in [g.guardian_user_id, g.dependent_patient_id]:
        raise HTTPException(status_code=403, detail="Unauthorized to revoke")

    g.status = "Revoked"
    g.ended_at_utc = datetime.utcnow()
    db.commit()
    return None