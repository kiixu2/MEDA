from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.dose_log import DoseLog
from app.models.schedule import MedicationSchedule
from app.models.patient_medication import PatientMedication
from app.models.user import User
from app.schemas.dose_log import (
    DoseLogCreate, DoseLogResponse
)
from app.utils.security import get_current_user
from app.utils.permissions import require_patient_access

router = APIRouter(prefix="/doses", tags=["Dose Logs"])

# 💡 دالة مساعدة للتأكد من الصلاحية
def check_dose_permission(user: User, schedule_id: int, db: Session):
    schedule = db.query(MedicationSchedule).filter(MedicationSchedule.schedule_id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    pm = db.query(PatientMedication).filter(PatientMedication.patient_medication_id == schedule.patient_medication_id).first()
    
    if user.role not in ["Doctor", "Nurse"]:
        require_patient_access(user, pm.patient_id, "manage_medications", db)
    return schedule

@router.post("", response_model=DoseLogResponse, status_code=201)
def create_dose_log(
    data: DoseLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    check_dose_permission(current_user, data.schedule_id, db)
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
    return db.query(DoseLog).join(MedicationSchedule).join(PatientMedication).filter(
        PatientMedication.patient_id == current_user.user_id
    ).all()


@router.post("/{log_id}/take", response_model=DoseLogResponse)
def mark_dose_taken(
    log_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    log = db.query(DoseLog).filter(DoseLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Dose log not found")
        
    check_dose_permission(current_user, log.schedule_id, db)
    log.status = "Taken"
    log.action_timestamp = datetime.utcnow()
    db.commit()
    db.refresh(log)
    return log