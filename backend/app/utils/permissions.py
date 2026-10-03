from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.guardianship import Guardianship
from app.models.user import User


def get_accessible_patient_ids(current_user: User, db: Session) -> list:
    """يرجع كل الـpatient_ids اللي المستخدم يقدر يوصل لها"""
    # نفسه
    ids = [current_user.user_id]
    
    # المرضى اللي هو وصي عليهم
    guardianships = db.query(Guardianship).filter(
        Guardianship.guardian_id == current_user.user_id,
        Guardianship.status == "Active"
    ).all()
    
    for g in guardianships:
        ids.append(g.dependent_id)
    
    return ids


def check_patient_access(
    current_user: User,
    patient_id: int,
    permission: str,
    db: Session
) -> bool:
    """
    يتحقق هل المستخدم يقدر يوصل لمريض معين
    permission: 'view_history' | 'manage_medications' | 'notifications'
    """
    # لو هو نفسه
    if current_user.user_id == patient_id:
        return True
    
    # لو وصي عليه
    guardianship = db.query(Guardianship).filter(
        Guardianship.guardian_id == current_user.user_id,
        Guardianship.dependent_id == patient_id,
        Guardianship.status == "Active"
    ).first()
    
    if not guardianship:
        return False
    
    # نتحقق من الصلاحية
    if permission == "view_history" and not guardianship.can_view_history:
        return False
    if permission == "manage_medications" and not guardianship.can_manage_medications:
        return False
    if permission == "notifications" and not guardianship.can_receive_notifications:
        return False
    
    return True


def require_patient_access(
    current_user: User,
    patient_id: int,
    permission: str,
    db: Session
):
    """يرفع خطأ لو ما عنده صلاحية"""
    if not check_patient_access(current_user, patient_id, permission, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this patient's data"
        )