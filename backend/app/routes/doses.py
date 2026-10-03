from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.dose_log import DoseLog
from app.models.schedule import MedicationSchedule
from app.models.medication import Medication
from app.models.user import User
from app.schemas.dose_log import (
    DoseLogCreate, DoseLogUpdate, DoseLogResponse
)
from app.utils.security import get_current_user
from app.utils.permissions import require_patient_access

router = APIRouter(prefix="/doses", tags=["Dose Logs"])


@router.post("", response_model=DoseLogResponse, status_code=201)
def create_dose_log(
    data: DoseLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.schedule_id == data.schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    med = db.query(Medication).filter(
        Medication.medication_id == schedule.medication_id
    ).first()
    
    require_patient_access(current_user, med.patient_id, "manage_medications", db)
    
    new_log = DoseLog(**data.model_dump())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.get("", response_model=List[DoseLogResponse])
def get_all_dose_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(DoseLog).join(MedicationSchedule).join(Medication).filter(
        Medication.patient_id == current_user.user_id
    ).all()


@router.get("/{log_id}", response_model=DoseLogResponse)
def get_dose_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = db.query(DoseLog).filter(DoseLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Dose log not found")
    
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.schedule_id == log.schedule_id
    ).first()
    med = db.query(Medication).filter(
        Medication.medication_id == schedule.medication_id
    ).first()
    
    require_patient_access(current_user, med.patient_id, "manage_medications", db)
    return log


@router.post("/{log_id}/take", response_model=DoseLogResponse)
def mark_dose_taken(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = db.query(DoseLog).filter(DoseLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Dose log not found")
    
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.schedule_id == log.schedule_id
    ).first()
    med = db.query(Medication).filter(
        Medication.medication_id == schedule.medication_id
    ).first()
    
    require_patient_access(current_user, med.patient_id, "manage_medications", db)
    
    log.status = "Taken"
    log.action_timestamp = datetime.utcnow()
    db.commit()
    db.refresh(log)
    return log


@router.post("/{log_id}/skip", response_model=DoseLogResponse)
def mark_dose_skipped(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = db.query(DoseLog).filter(DoseLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Dose log not found")
    
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.schedule_id == log.schedule_id
    ).first()
    med = db.query(Medication).filter(
        Medication.medication_id == schedule.medication_id
    ).first()
    
    require_patient_access(current_user, med.patient_id, "manage_medications", db)
    
    log.status = "Skipped"
    log.action_timestamp = datetime.utcnow()
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{log_id}", status_code=204)
def delete_dose_log(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = db.query(DoseLog).filter(DoseLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Dose log not found")
    
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.schedule_id == log.schedule_id
    ).first()
    med = db.query(Medication).filter(
        Medication.medication_id == schedule.medication_id
    ).first()
    
    require_patient_access(current_user, med.patient_id, "manage_medications", db)
    
    db.delete(log)
    db.commit()
    return None