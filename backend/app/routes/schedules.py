from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.dose_log import DoseLog
from app.models.patient_medication import PatientMedication
from app.models.schedule import MedicationSchedule
from app.models.user import User
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate, ScheduleResponse
from app.utils.permissions import (
    require_patient_access, require_any_patient_access, MANAGE_MEDICATIONS
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/schedules", tags=["Schedules"])


def _load_schedule(db: Session, schedule_id: int):
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
    return schedule, pm


@router.post("", response_model=ScheduleResponse, status_code=201)
def create_schedule(
    data: ScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    pm = db.query(PatientMedication).filter(
        PatientMedication.patient_medication_id == data.patient_medication_id
    ).first()
    if not pm:
        raise HTTPException(status_code=404, detail="Patient medication not found")

    require_patient_access(current_user, pm.patient_id, MANAGE_MEDICATIONS, db)

    new_schedule = MedicationSchedule(**data.model_dump())
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule


@router.get("", response_model=List[ScheduleResponse])
def get_my_schedules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(MedicationSchedule).join(PatientMedication).filter(
        PatientMedication.patient_id == current_user.user_id
    ).all()


@router.get("/patient/{patient_id}", response_model=List[ScheduleResponse])
def get_patient_schedules(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    require_any_patient_access(current_user, patient_id, db)
    return db.query(MedicationSchedule).join(PatientMedication).filter(
        PatientMedication.patient_id == patient_id
    ).all()


@router.get("/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schedule, pm = _load_schedule(db, schedule_id)
    require_any_patient_access(current_user, pm.patient_id, db)
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schedule, pm = _load_schedule(db, schedule_id)
    require_patient_access(current_user, pm.patient_id, MANAGE_MEDICATIONS, db)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(schedule, key, value)

    if schedule.end_date and schedule.end_date < schedule.start_date:
        raise HTTPException(status_code=422, detail="end_date must be on or after start_date")

    db.commit()
    db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=204)
def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schedule, pm = _load_schedule(db, schedule_id)
    require_patient_access(current_user, pm.patient_id, MANAGE_MEDICATIONS, db)

    # الجدول الذي له سجل جرعات لا يُحذف (نحافظ على التاريخ الطبي) - يُعطَّل بدلاً من ذلك
    if db.query(DoseLog).filter(DoseLog.schedule_id == schedule_id).first():
        raise HTTPException(
            status_code=409,
            detail="Schedule has dose history and cannot be deleted. Set is_active=false instead."
        )

    db.delete(schedule)
    db.commit()
    return None
