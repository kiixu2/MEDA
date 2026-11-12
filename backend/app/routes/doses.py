from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dose_log import DoseLog
from app.models.patient_medication import PatientMedication
from app.models.schedule import MedicationSchedule
from app.models.user import User
from app.schemas.dose_log import DoseLogCreate, DoseLogResponse
from app.utils.clock import utcnow
from app.utils.permissions import (
    require_patient_access, require_any_patient_access, MANAGE_MEDICATIONS
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/doses", tags=["Dose Logs"])


def _patient_id_for_schedule(db: Session, schedule_id: int) -> int:
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.schedule_id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    pm = db.query(PatientMedication).filter(
        PatientMedication.patient_medication_id == schedule.patient_medication_id
    ).first()
    if not pm:
        raise HTTPException(status_code=404, detail="Patient medication not found")
    return pm.patient_id


def _get_log_with_access(db: Session, user: User, log_id: int) -> DoseLog:
    log = db.query(DoseLog).filter(DoseLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Dose log not found")
    patient_id = _patient_id_for_schedule(db, log.schedule_id)
    require_patient_access(user, patient_id, MANAGE_MEDICATIONS, db)
    return log


@router.post("", response_model=DoseLogResponse, status_code=201)
def create_dose_log(
    data: DoseLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    patient_id = _patient_id_for_schedule(db, data.schedule_id)
    require_patient_access(current_user, patient_id, MANAGE_MEDICATIONS, db)

    new_log = DoseLog(**data.model_dump(), status="Pending")  # الحالة تبدأ Pending دائماً
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.get("", response_model=List[DoseLogResponse])
def get_my_dose_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(DoseLog).join(MedicationSchedule).join(PatientMedication).filter(
        PatientMedication.patient_id == current_user.user_id
    ).all()


@router.get("/patient/{patient_id}", response_model=List[DoseLogResponse])
def get_patient_dose_logs(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_any_patient_access(current_user, patient_id, db)
    return db.query(DoseLog).join(MedicationSchedule).join(PatientMedication).filter(
        PatientMedication.patient_id == patient_id
    ).all()


@router.post("/{log_id}/take", response_model=DoseLogResponse)
def mark_dose_taken(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = _get_log_with_access(db, current_user, log_id)
    if log.status != "Pending":
        raise HTTPException(status_code=400, detail=f"Dose is already {log.status}")

    log.status = "Taken"
    log.action_timestamp = utcnow()
    db.commit()
    db.refresh(log)
    return log


@router.post("/{log_id}/skip", response_model=DoseLogResponse)
def mark_dose_skipped(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = _get_log_with_access(db, current_user, log_id)
    if log.status != "Pending":
        raise HTTPException(status_code=400, detail=f"Dose is already {log.status}")

    log.status = "Skipped"
    log.action_timestamp = utcnow()
    db.commit()
    db.refresh(log)
    return log
