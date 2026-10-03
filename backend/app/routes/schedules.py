from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.schedule import MedicationSchedule
from app.models.medication import Medication
from app.models.user import User
from app.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse
)
from app.utils.security import get_current_user
from app.utils.permissions import require_patient_access

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.post("", response_model=ScheduleResponse, status_code=201)
def create_schedule(
    data: ScheduleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # نتأكد إن الدواء موجود
    med = db.query(Medication).filter(
        Medication.medication_id == data.medication_id
    ).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    
    # نتأكد إن المستخدم يقدر يعدل على هذا الدواء
    require_patient_access(current_user, med.patient_id, "manage_medications", db)
    
    new_schedule = MedicationSchedule(**data.model_dump())
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule


@router.get("", response_model=List[ScheduleResponse])
def get_all_schedules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # نجيب كل مواعيد المستخدم
    return db.query(MedicationSchedule).join(Medication).filter(
        Medication.patient_id == current_user.user_id
    ).all()


@router.get("/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.schedule_id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    med = db.query(Medication).filter(
        Medication.medication_id == schedule.medication_id
    ).first()
    
    require_patient_access(current_user, med.patient_id, "manage_medications", db)
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.schedule_id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    med = db.query(Medication).filter(
        Medication.medication_id == schedule.medication_id
    ).first()
    
    require_patient_access(current_user, med.patient_id, "manage_medications", db)

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(schedule, key, value)

    db.commit()
    db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=204)
def delete_schedule(
    schedule_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.schedule_id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    med = db.query(Medication).filter(
        Medication.medication_id == schedule.medication_id
    ).first()
    
    require_patient_access(current_user, med.patient_id, "manage_medications", db)
    
    db.delete(schedule)
    db.commit()
    return None