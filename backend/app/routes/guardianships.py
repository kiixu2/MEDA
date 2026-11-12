from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.guardianship import Guardianship
from app.models.user import User
from app.schemas.guardianship import (
    GuardianshipCreate, GuardianshipUpdate, GuardianshipApprove, GuardianshipResponse
)
from app.utils.clock import utcnow, is_minor
from app.utils.permissions import get_patient_profile_or_404
from app.utils.security import get_current_user

router = APIRouter(prefix="/guardianships", tags=["Guardianship"])


@router.post("", response_model=GuardianshipResponse, status_code=201)
def request_guardianship(
    data: GuardianshipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """طلب وصاية: دائماً Pending حتى يوافق المريض (أو الأدمن إذا كان قاصراً)."""
    if data.dependent_patient_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Can't be guardian of yourself")

    dependent = db.query(User).filter(User.user_id == data.dependent_patient_id).first()
    if not dependent:
        raise HTTPException(status_code=404, detail="Patient not found")
    # الوصاية مرتبطة بـ patient_profiles (مفتاح أجنبي) فلازم يكون للمريض ملف
    get_patient_profile_or_404(db, data.dependent_patient_id)

    existing = db.query(Guardianship).filter(
        Guardianship.guardian_user_id == current_user.user_id,
        Guardianship.dependent_patient_id == data.dependent_patient_id
    ).first()

    if existing:
        if existing.status in ("Pending", "Active"):
            raise HTTPException(status_code=400, detail="Guardianship request already exists")
        # كانت Revoked/Ended: نسمح بطلب جديد (يحتاج موافقة جديدة)
        existing.relationship_type = data.relationship_type
        existing.can_view_history = bool(data.can_view_history)
        existing.can_manage_medications = bool(data.can_manage_medications)
        existing.status = "Pending"
        existing.granted_at_utc = None
        existing.ended_at_utc = None
        db.commit()
        db.refresh(existing)
        return existing

    new_g = Guardianship(
        guardian_user_id=current_user.user_id,
        dependent_patient_id=data.dependent_patient_id,
        relationship_type=data.relationship_type,
        can_view_history=bool(data.can_view_history),
        can_manage_medications=bool(data.can_manage_medications),
        status="Pending",
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


@router.get("/my-requests", response_model=List[GuardianshipResponse])
def get_my_sent_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """الطلبات التي أرسلتها أنا كوصي ولم تُقبل بعد."""
    return db.query(Guardianship).filter(
        Guardianship.guardian_user_id == current_user.user_id,
        Guardianship.status == "Pending"
    ).all()


def _can_decide(user: User, g: Guardianship, db: Session) -> bool:
    """من يملك قرار الموافقة؟ المريض البالغ نفسه، أو الأدمن إذا كان المريض قاصراً."""
    dependent = db.query(User).filter(User.user_id == g.dependent_patient_id).first()
    if not dependent:
        return False
    if is_minor(dependent.date_of_birth):
        return user.role == "Admin"
    return user.user_id == g.dependent_patient_id


@router.get("/pending-requests", response_model=List[GuardianshipResponse])
def get_pending_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """طلبات تنتظر قراري: للمريض البالغ طلباته، وللأدمن طلبات القاصرين."""
    pending = db.query(Guardianship).filter(Guardianship.status == "Pending").all()
    return [g for g in pending if _can_decide(current_user, g, db)]


@router.put("/{guardianship_id}/approve", response_model=GuardianshipResponse)
def approve_guardianship(
    guardianship_id: int,
    data: Optional[GuardianshipApprove] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    g = db.query(Guardianship).filter(
        Guardianship.guardianship_id == guardianship_id,
        Guardianship.status == "Pending"
    ).first()
    # نفس الرد للحالتين (غير موجود / ليس لك) حتى لا نكشف وجود الطلب
    if not g or not _can_decide(current_user, g, db):
        raise HTTPException(status_code=404, detail="Pending request not found or unauthorized")

    # الصلاحيات الافتراضية = ما طلبه الوصي، والمريض يقدر يقلّلها أو يغيرها
    if data is not None:
        if data.can_view_history is not None:
            g.can_view_history = data.can_view_history
        if data.can_manage_medications is not None:
            g.can_manage_medications = data.can_manage_medications

    g.status = "Active"
    g.granted_at_utc = utcnow()
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
    g = db.query(Guardianship).filter(
        Guardianship.guardianship_id == guardianship_id
    ).first()
    if not g:
        raise HTTPException(status_code=404, detail="Guardianship not found")

    if current_user.user_id == g.guardian_user_id:
        allowed = {"relationship_type"}                      # الوصي: وصف العلاقة فقط
    elif current_user.user_id == g.dependent_patient_id:
        allowed = {"can_view_history", "can_manage_medications"}  # المريض: الصلاحيات فقط
    else:
        raise HTTPException(status_code=404, detail="Guardianship not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        if key in allowed and value is not None:
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
    """إلغاء/رفض الوصاية: يستطيعه الوصي أو المريض."""
    g = db.query(Guardianship).filter(
        Guardianship.guardianship_id == guardianship_id
    ).first()
    if not g or current_user.user_id not in (g.guardian_user_id, g.dependent_patient_id):
        raise HTTPException(status_code=404, detail="Guardianship not found")

    g.status = "Revoked"
    g.ended_at_utc = utcnow()
    db.commit()
    return None
