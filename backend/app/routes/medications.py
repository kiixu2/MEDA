from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.medication import Medication
from app.models.user import User
from app.schemas.medication import (
    MedicationCreate, MedicationUpdate, MedicationResponse
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/medications", tags=["Medications"])


@router.post("", response_model=MedicationResponse, status_code=201)
def create_medication(
    med_data: MedicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    data = med_data.model_dump()
    data["patient_id"] = current_user.user_id  # ناخذ patient_id من الـToken
    new_med = Medication(**data)
    db.add(new_med)
    db.commit()
    db.refresh(new_med)
    return new_med


@router.get("", response_model=List[MedicationResponse])
def get_all_medications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # كل مريض يشوف أدويته فقط
    return db.query(Medication).filter(
        Medication.patient_id == current_user.user_id
    ).all()


@router.get("/{medication_id}", response_model=MedicationResponse)
def get_medication(
    medication_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    med = db.query(Medication).filter(
        Medication.medication_id == medication_id,
        Medication.patient_id == current_user.user_id
    ).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    return med


@router.put("/{medication_id}", response_model=MedicationResponse)
def update_medication(
    medication_id: int,
    med_data: MedicationUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    med = db.query(Medication).filter(
        Medication.medication_id == medication_id,
        Medication.patient_id == current_user.user_id
    ).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")

    for key, value in med_data.model_dump(exclude_unset=True).items():
        setattr(med, key, value)

    db.commit()
    db.refresh(med)
    return med


@router.delete("/{medication_id}", status_code=204)
def delete_medication(
    medication_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    med = db.query(Medication).filter(
        Medication.medication_id == medication_id,
        Medication.patient_id == current_user.user_id
    ).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    db.delete(med)
    db.commit()
    return None