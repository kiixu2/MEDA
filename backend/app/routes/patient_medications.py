from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.medication_catalog import MedicationCatalog
from app.models.patient_medication import PatientMedication
from app.models.user import User
from app.schemas.patient_medication import PatientMedicationCreate, PatientMedicationResponse
from app.utils.permissions import (
    require_patient_access, require_any_patient_access,
    get_patient_profile_or_404, MANAGE_MEDICATIONS
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/patient-medications", tags=["Patient Medications"])


@router.post("", response_model=PatientMedicationResponse, status_code=201)
def create_patient_medication(
    data: PatientMedicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    get_patient_profile_or_404(db, data.patient_id)
    # 🛡️ المريض نفسه، أو وصي بصلاحية، أو طبيب مشرف، أو ممرض معيّن
    require_patient_access(current_user, data.patient_id, MANAGE_MEDICATIONS, db)

    if not db.query(MedicationCatalog).filter(
        MedicationCatalog.medication_id == data.medication_id,
        MedicationCatalog.is_active == True  # noqa: E712
    ).first():
        raise HTTPException(status_code=404, detail="Medication not found in catalog")

    pm = PatientMedication(**data.model_dump())
    # 🛡️ الطبيب الواصف يُؤخذ من التوكن فقط
    pm.prescribed_by_doctor_id = current_user.user_id if current_user.role == "Doctor" else None
    db.add(pm)
    db.commit()
    db.refresh(pm)
    return pm


@router.get("", response_model=List[PatientMedicationResponse])
def get_my_patient_medications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(PatientMedication).filter(
        PatientMedication.patient_id == current_user.user_id,
        PatientMedication.status == "Active"
    ).all()


@router.get("/patient/{patient_id}", response_model=List[PatientMedicationResponse])
def get_patient_medications(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_any_patient_access(current_user, patient_id, db)
    return db.query(PatientMedication).filter(
        PatientMedication.patient_id == patient_id
    ).all()
