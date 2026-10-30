from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.schedule import MedicationSchedule
from app.models.patient_medication import PatientMedication
from app.models.user import User
from app.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse
)
from app.utils.security import get_current_user
from app.utils.permissions import require_patient_access

router = APIRouter(prefix="/schedules", tags=["Schedules"])

# 💡 دالة مساعدة للتحقق من الصلاحية (عشان ما نكرر الكود)
def check_schedule_permission(user: User, patient_id: int, db: Session):
    if user.role not in ["Doctor", "Nurse"]:
        require_patient_access(user, patient_id, "manage_medications", db)

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

    # 💡 نسمح للطبيب والممرض بالمرور
    check_schedule_permission(current_user, pm.patient_id, db)

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
    return db.query(MedicationSchedule).join(PatientMedication).filter(
        PatientMedication.patient_id == current_user.user_id
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

    pm = db.query(PatientMedication).filter(
        PatientMedication.patient_medication_id == schedule.patient_medication_id
    ).first()
    
    check_schedule_permission(current_user, pm.patient_id, db)
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

    pm = db.query(PatientMedication).filter(
        PatientMedication.patient_medication_id == schedule.patient_medication_id
    ).first()
    
    check_schedule_permission(current_user, pm.patient_id, db)

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

    pm = db.query(PatientMedication).filter(
        PatientMedication.patient_medication_id == schedule.patient_medication_id
    ).first()
    
    check_schedule_permission(current_user, pm.patient_id, db)

    db.delete(schedule)
    db.commit()
    return None