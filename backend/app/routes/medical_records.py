from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.medical_record import PatientMedicalRecord
from app.models.medical_record_note import MedicalRecordNote
from app.models.user import User
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordResponse
from app.utils.permissions import (
    require_patient_access, get_patient_profile_or_404, VIEW_HISTORY
)
from app.utils.security import get_current_user, require_roles

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])


@router.post("", response_model=MedicalRecordResponse, status_code=201)
def create_record(
    data: MedicalRecordCreate,
    # 🛡️ الطبيب فقط (العمود doctor_user_id مربوط بجدول الأطباء)
    current_user: User = Depends(require_roles(["Doctor"])),
    db: Session = Depends(get_db)
):
    get_patient_profile_or_404(db, data.patient_id)
    # 🛡️ لازم يكون الطبيب مشرفاً فعلياً على هذا المريض
    require_patient_access(current_user, data.patient_id, VIEW_HISTORY, db)

    record = PatientMedicalRecord(
        **data.model_dump(),
        doctor_user_id=current_user.user_id,
        created_by_user_id=current_user.user_id,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=List[MedicalRecordResponse])
def get_my_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(PatientMedicalRecord).filter(
        PatientMedicalRecord.patient_id == current_user.user_id
    ).all()


@router.get("/patient/{patient_id}", response_model=List[MedicalRecordResponse])
def get_patient_records(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_patient_access(current_user, patient_id, VIEW_HISTORY, db)
    return db.query(PatientMedicalRecord).filter(
        PatientMedicalRecord.patient_id == patient_id
    ).all()


@router.delete("/{record_id}", status_code=204)
def delete_record(
    record_id: int,
    # 🛡️ الطبيب الذي أنشأ السجل فقط
    current_user: User = Depends(require_roles(["Doctor"])),
    db: Session = Depends(get_db)
):
    record = db.query(PatientMedicalRecord).filter(
        PatientMedicalRecord.record_id == record_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if record.created_by_user_id != current_user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You can only delete medical records you created"
        )

    # نحذف الملاحظات التابعة أولاً (وإلا يفشل الحذف بسبب المفتاح الأجنبي)
    db.query(MedicalRecordNote).filter(
        MedicalRecordNote.record_id == record_id
    ).delete(synchronize_session=False)
    db.delete(record)
    db.commit()
    return None
