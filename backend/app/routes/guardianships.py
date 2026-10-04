from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.guardianship import Guardianship
from app.models.user import User
from app.schemas.guardianship import (
    GuardianshipCreate, GuardianshipUpdate, GuardianshipResponse
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/guardianships", tags=["Guardianship"])


@router.post("", response_model=GuardianshipResponse, status_code=201)
def create_guardianship(
    data: GuardianshipCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if data.dependent_patient_id == current_user.user_id:
        raise HTTPException(status_code=400, detail="Can't be guardian of yourself")

    existing = db.query(Guardianship).filter(
        Guardianship.guardian_user_id == current_user.user_id,
        Guardianship.dependent_patient_id == data.dependent_patient_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Guardianship already exists")

    new_g = Guardianship(
        guardian_user_id=current_user.user_id,
        dependent_patient_id=data.dependent_patient_id,
        relationship_type=data.relationship_type,
        can_view_history=data.can_view_history,
        can_manage_medications=data.can_manage_medications,
        status="Active",
        granted_at_utc=datetime.utcnow()
    )
    db.add(new_g)
    db.commit()
    db.refresh(new_g)
    return new_g


@router.get("/my-patients", response_model=List[GuardianshipResponse])
def get_my_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Guardianship).filter(
        Guardianship.guardian_user_id == current_user.user_id,
        Guardianship.status == "Active"
    ).all()


@router.get("/my-guardians", response_model=List[GuardianshipResponse])
def get_my_guardians(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Guardianship).filter(
        Guardianship.dependent_patient_id == current_user.user_id,
        Guardianship.status == "Active"
    ).all()


@router.put("/{guardianship_id}", response_model=GuardianshipResponse)
def update_guardianship(
    guardianship_id: int,
    data: GuardianshipUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    g = db.query(Guardianship).filter(
        Guardianship.guardianship_id == guardianship_id,
        Guardianship.guardian_user_id == current_user.user_id
    ).first()
    if not g:
        raise HTTPException(status_code=404, detail="Guardianship not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(g, key, value)

    db.commit()
    db.refresh(g)
    return g


@router.delete("/{guardianship_id}", status_code=204)
def revoke_guardianship(
    guardianship_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    g = db.query(Guardianship).filter(
        Guardianship.guardianship_id == guardianship_id,
        Guardianship.guardian_user_id == current_user.user_id
    ).first()
    if not g:
        raise HTTPException(status_code=404, detail="Guardianship not found")

    g.status = "Revoked"
    g.ended_at_utc = datetime.utcnow()
    db.commit()
    return None