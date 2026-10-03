from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.medication import Medication
from app.schemas.medication import (
    MedicationCreate, MedicationUpdate, MedicationResponse
)

router = APIRouter(prefix="/medications", tags=["Medications"])


@router.post("", response_model=MedicationResponse, status_code=201)
def create_medication(med_data: MedicationCreate, db: Session = Depends(get_db)):
    new_med = Medication(**med_data.model_dump())
    db.add(new_med)
    db.commit()
    db.refresh(new_med)
    return new_med


@router.get("", response_model=List[MedicationResponse])
def get_all_medications(db: Session = Depends(get_db)):
    return db.query(Medication).all()


@router.get("/{medication_id}", response_model=MedicationResponse)
def get_medication(medication_id: int, db: Session = Depends(get_db)):
    med = db.query(Medication).filter(Medication.medication_id == medication_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    return med


@router.put("/{medication_id}", response_model=MedicationResponse)
def update_medication(
    medication_id: int,
    med_data: MedicationUpdate,
    db: Session = Depends(get_db)
):
    med = db.query(Medication).filter(Medication.medication_id == medication_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")

    for key, value in med_data.model_dump(exclude_unset=True).items():
        setattr(med, key, value)

    db.commit()
    db.refresh(med)
    return med


@router.delete("/{medication_id}", status_code=204)
def delete_medication(medication_id: int, db: Session = Depends(get_db)):
    med = db.query(Medication).filter(Medication.medication_id == medication_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    db.delete(med)
    db.commit()
    return None