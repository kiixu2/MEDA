from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.patient_medication import PatientMedication
from app.models.user import User
from app.schemas.patient_medication import PatientMedicationCreate, PatientMedicationResponse
from app.utils.security import get_current_user
from app.utils.permissions import require_patient_access

router = APIRouter(prefix="/patient-medications", tags=["Patient Medications"])

@router.post("", response_model=PatientMedicationResponse, status_code=201)
def create_patient_medication(
    data: PatientMedicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # 💡 التعديل هنا: نسمح للطبيب أو الممرض بالإضافة
    if current_user.role not in ["Doctor", "Nurse"]:
        require_patient_access(current_user, data.patient_id, "manage_medications", db)
        
    pm = PatientMedication(**data.model_dump())
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
    # هنا برضه نسمح للطبيب والممرض بالرؤية
    if current_user.role not in ["Doctor", "Nurse"]:
        require_patient_access(current_user, patient_id, "manage_medications", db)
        
    return db.query(PatientMedication).filter(
        PatientMedication.patient_id == patient_id
    ).all()