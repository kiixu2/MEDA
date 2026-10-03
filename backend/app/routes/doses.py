from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.dose_log import DoseLog
from app.schemas.dose_log import (
    DoseLogCreate, DoseLogUpdate, DoseLogResponse
)

router = APIRouter(prefix="/doses", tags=["Dose Logs"])


@router.post("", response_model=DoseLogResponse, status_code=201)
def create_dose_log(data: DoseLogCreate, db: Session = Depends(get_db)):
    new_log = DoseLog(**data.model_dump())
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


@router.get("", response_model=List[DoseLogResponse])
def get_all_dose_logs(db: Session = Depends(get_db)):
    return db.query(DoseLog).all()


@router.get("/{log_id}", response_model=DoseLogResponse)
def get_dose_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(DoseLog).filter(DoseLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Dose log not found")
    return log


@router.post("/{log_id}/take", response_model=DoseLogResponse)
def mark_dose_taken(log_id: int, db: Session = Depends(get_db)):
    log = db.query(DoseLog).filter(DoseLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Dose log not found")
    log.status = "Taken"
    log.action_timestamp = datetime.utcnow()
    db.commit()
    db.refresh(log)
    return log


@router.post("/{log_id}/skip", response_model=DoseLogResponse)
def mark_dose_skipped(log_id: int, db: Session = Depends(get_db)):
    log = db.query(DoseLog).filter(DoseLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Dose log not found")
    log.status = "Skipped"
    log.action_timestamp = datetime.utcnow()
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{log_id}", status_code=204)
def delete_dose_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(DoseLog).filter(DoseLog.log_id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Dose log not found")
    db.delete(log)
    db.commit()
    return None