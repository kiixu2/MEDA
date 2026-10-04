from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.allergy import PatientAllergy
from app.models.user import User
from app.schemas.allergy import AllergyCreate, AllergyResponse
from app.utils.security import get_current_user
from app.utils.permissions import require_patient_access

router = APIRouter(prefix="/allergies", tags=["Allergies"])


@router.post("", response_model=AllergyResponse, status_code=201)
def create_allergy(
    data: AllergyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_patient_access(current_user, data.patient_id, "view_history", db)
    allergy = PatientAllergy(
        added_by_user_id=current_user.user_id,
        **data.model_dump()
    )
    db.add(allergy)
    db.commit()
    db.refresh(allergy)
    return allergy


@router.get("", response_model=List[AllergyResponse])
def get_my_allergies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(PatientAllergy).filter(
        PatientAllergy.patient_id == current_user.user_id
    ).all()


@router.get("/patient/{patient_id}", response_model=List[AllergyResponse])
def get_patient_allergies(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_patient_access(current_user, patient_id, "view_history", db)
    return db.query(PatientAllergy).filter(
        PatientAllergy.patient_id == patient_id
    ).all()


@router.delete("/{allergy_id}", status_code=204)
def delete_allergy(
    allergy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    allergy = db.query(PatientAllergy).filter(
        PatientAllergy.allergy_id == allergy_id
    ).first()
    if not allergy:
        raise HTTPException(status_code=404, detail="Allergy not found")
    require_patient_access(current_user, allergy.patient_id, "view_history", db)
    db.delete(allergy)
    db.commit()
    return None