from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.schedule import MedicationSchedule
from app.schemas.schedule import (
    ScheduleCreate, ScheduleUpdate, ScheduleResponse
)

router = APIRouter(prefix="/schedules", tags=["Schedules"])


@router.post("", response_model=ScheduleResponse, status_code=201)
def create_schedule(data: ScheduleCreate, db: Session = Depends(get_db)):
    new_schedule = MedicationSchedule(**data.model_dump())
    db.add(new_schedule)
    db.commit()
    db.refresh(new_schedule)
    return new_schedule


@router.get("", response_model=List[ScheduleResponse])
def get_all_schedules(db: Session = Depends(get_db)):
    return db.query(MedicationSchedule).all()


@router.get("/{schedule_id}", response_model=ScheduleResponse)
def get_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.schedule_id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedule


@router.put("/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: int,
    data: ScheduleUpdate,
    db: Session = Depends(get_db)
):
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.schedule_id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(schedule, key, value)

    db.commit()
    db.refresh(schedule)
    return schedule


@router.delete("/{schedule_id}", status_code=204)
def delete_schedule(schedule_id: int, db: Session = Depends(get_db)):
    schedule = db.query(MedicationSchedule).filter(
        MedicationSchedule.schedule_id == schedule_id
    ).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    db.delete(schedule)
    db.commit()
    return None