from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.guardianship import Guardianship
from app.models.user import User


def get_accessible_patient_ids(current_user: User, db: Session) -> list:
    ids = [current_user.user_id]
    guardianships = db.query(Guardianship).filter(
        Guardianship.guardian_user_id == current_user.user_id,
        Guardianship.status == "Active"
    ).all()
    for g in guardianships:
        ids.append(g.dependent_patient_id)
    return ids


def check_patient_access(current_user, patient_id, permission, db):
    if current_user.user_id == patient_id:
        return True
    guardianship = db.query(Guardianship).filter(
        Guardianship.guardian_user_id == current_user.user_id,
        Guardianship.dependent_patient_id == patient_id,
        Guardianship.status == "Active"
    ).first()
    if not guardianship:
        return False
    if permission == "view_history" and not guardianship.can_view_history:
        return False
    if permission == "manage_medications" and not guardianship.can_manage_medications:
        return False
    return True


def require_patient_access(current_user, patient_id, permission, db):
    if not check_patient_access(current_user, patient_id, permission, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this patient's data"
        )