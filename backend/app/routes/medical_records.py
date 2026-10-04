from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.medical_record import PatientMedicalRecord
from app.models.user import User
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordResponse
from app.utils.security import get_current_user
from app.utils.permissions import require_patient_access

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])


@router.post("", response_model=MedicalRecordResponse, status_code=201)
def create_record(
    data: MedicalRecordCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_patient_access(current_user, data.patient_id, "view_history", db)
    record = PatientMedicalRecord(
        created_by_user_id=current_user.user_id,
        **data.model_dump()
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
    require_patient_access(current_user, patient_id, "view_history", db)
    return db.query(PatientMedicalRecord).filter(
        PatientMedicalRecord.patient_id == patient_id
    ).all()


@router.delete("/{record_id}", status_code=204)
def delete_record(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(PatientMedicalRecord).filter(
        PatientMedicalRecord.record_id == record_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    require_patient_access(current_user, record.patient_id, "view_history", db)
    db.delete(record)
    db.commit()
    return None