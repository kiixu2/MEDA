"""
نقطة واحدة لكل فحوص الوصول لبيانات المريض.

القاعدة: المستخدم يصل لبيانات مريض فقط إذا كان:
  1. هو المريض نفسه، أو
  2. وصياً (Guardianship) بحالة Active وعنده الصلاحية المطلوبة، أو
  3. طبيباً لديه إشراف (MedicalSupervisor) بحالة Active على هذا المريض، أو
  4. ممرضاً معيّناً للمريض (assigned_nurse_id).

الدور وحده (Doctor / Nurse) لا يمنح أي وصول.
"""
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.guardianship import Guardianship
from app.models.medical_supervisor import MedicalSupervisor
from app.models.patient_profile import PatientProfile
from app.models.user import User

VIEW_HISTORY = "view_history"
MANAGE_MEDICATIONS = "manage_medications"
_VALID_PERMISSIONS = {VIEW_HISTORY, MANAGE_MEDICATIONS}


def get_accessible_patient_ids(current_user: User, db: Session) -> list:
    ids = {current_user.user_id}
    for g in db.query(Guardianship).filter(
        Guardianship.guardian_user_id == current_user.user_id,
        Guardianship.status == "Active"
    ).all():
        ids.add(g.dependent_patient_id)
    if current_user.role == "Doctor":
        for s in db.query(MedicalSupervisor).filter(
            MedicalSupervisor.doctor_user_id == current_user.user_id,
            MedicalSupervisor.status == "Active"
        ).all():
            ids.add(s.patient_id)
    if current_user.role == "Nurse":
        for p in db.query(PatientProfile).filter(
            PatientProfile.assigned_nurse_id == current_user.user_id
        ).all():
            ids.add(p.patient_id)
    return list(ids)


def check_patient_access(current_user: User, patient_id: int, permission: str, db: Session) -> bool:
    if permission not in _VALID_PERMISSIONS:
        # صلاحية غير معروفة = خطأ برمجي، نرفض بدل ما نسمح بالخطأ
        raise ValueError(f"Unknown permission: {permission}")

    # 1. المريض نفسه
    if current_user.user_id == patient_id:
        return True

    # 2. وصي نشط عنده الصلاحية
    g = db.query(Guardianship).filter(
        Guardianship.guardian_user_id == current_user.user_id,
        Guardianship.dependent_patient_id == patient_id,
        Guardianship.status == "Active"
    ).first()
    if g:
        if permission == VIEW_HISTORY and g.can_view_history:
            return True
        if permission == MANAGE_MEDICATIONS and g.can_manage_medications:
            return True

    # 3. طبيب مشرف
    if current_user.role == "Doctor":
        supervised = db.query(MedicalSupervisor).filter(
            MedicalSupervisor.doctor_user_id == current_user.user_id,
            MedicalSupervisor.patient_id == patient_id,
            MedicalSupervisor.status == "Active"
        ).first()
        if supervised:
            return True

    # 4. ممرض معيّن
    if current_user.role == "Nurse":
        profile = db.query(PatientProfile).filter(
            PatientProfile.patient_id == patient_id,
            PatientProfile.assigned_nurse_id == current_user.user_id
        ).first()
        if profile:
            return True

    return False


def require_patient_access(current_user: User, patient_id: int, permission: str, db: Session):
    if not check_patient_access(current_user, patient_id, permission, db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this patient's data"
        )


def get_patient_profile_or_404(db: Session, patient_id: int) -> PatientProfile:
    """يتأكد أن للمريض ملفاً (patient_profile) - مطلوب لأن كل الجداول الطبية مربوطة به."""
    profile = db.query(PatientProfile).filter(PatientProfile.patient_id == patient_id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Patient profile not found")
    return profile


def require_any_patient_access(current_user: User, patient_id: int, db: Session):
    """للقراءة: يكفي أي من الصلاحيتين (عرض السجل أو إدارة الأدوية)."""
    if not (
        check_patient_access(current_user, patient_id, VIEW_HISTORY, db)
        or check_patient_access(current_user, patient_id, MANAGE_MEDICATIONS, db)
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this patient's data"
        )
