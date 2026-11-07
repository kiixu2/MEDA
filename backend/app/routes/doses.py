from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.database import get_db
from app.models.dose_log import DoseLog
from app.models.schedule import MedicationSchedule
from app.models.patient_medication import PatientMedication
from app.models.user import User
from app.models.medical_supervisor import MedicalSupervisor
from app.models.patient_profile import PatientProfile
from app.schemas.dose_log import (
    DoseLogCreate, DoseLogResponse
)
from app.utils.security import get_current_user
from app.utils.permissions import require_patient_access

router = APIRouter(prefix="/doses", tags=["Dose Logs"])

# 🛡️ دالة التحقق الأمني الصارمة (نفسها اللي في schedules)
def check_dose_permission(user: User, schedule_id: int, db: Session):
    schedule = db.query(MedicationSchedule).filter(MedicationSchedule.schedule_id == schedule_id).first()
    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    pm = db.query(PatientMedication).filter(PatientMedication.patient_medication_id == schedule.patient_medication_id).first()
    patient_id = pm.patient_id

    # 1. المريض نفسه
    if user.user_id == patient_id:
        return schedule
        
    # 2. الوصي
    if user.role == "Caregiver":
        require_patient_access(user, patient_id, "manage_medications", db)
        return schedule
        
    # 3. الطبيب المشرف
    if user.role == "Doctor":
        supervision = db.query(MedicalSupervisor).filter(
            MedicalSupervisor.doctor_user_id == user.user_id,
            MedicalSupervisor.patient_id == patient_id,
            MedicalSupervisor.status == "Active"
        ).first()
        if supervision:
            return schedule
        raise HTTPException(status_code=403, detail="You are not authorized as a supervisor for this patient")
        
    # 4. الممرض المعين
    if user.role == "Nurse":
        profile = db.query(PatientProfile).filter(PatientProfile.patient_id == patient_id).first()
        if profile and profile.assigned_nurse_id == user.user_id:
            return schedule
        raise HTTPException(status_code=403, detail="You are not assigned as a nurse for this patient")
        
    raise HTTPException(status_code=403, detail="Access denied")


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
def get_my_dose_logs(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # المريض يشوف سجله فقط
    return db.query(DoseLog).join(MedicationSchedule).join(PatientMedication).filter(
        PatientMedication.patient_id == current_user.user_id
    ).all()


@router.get("/patient/{patient_id}", response_model=List[DoseLogResponse])
def get_patient_dose_logs(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # الطبيب أو الممرض أو الوصي يشوفون سجل المريض (بعد التحقق)
    # نستخدم أول Schedule للمريض عشان نمرر الـ ID للدالة، أو نعدل الدالة
    # للتبسيط هنا، سنتحقق من الصلاحية بناءً على الـ patient_id مباشرة
    if current_user.user_id == patient_id:
        pass
    elif current_user.role == "Caregiver":
        require_patient_access(current_user, patient_id, "view_history", db)
    elif current_user.role == "Doctor":
        supervision = db.query(MedicalSupervisor).filter(
            MedicalSupervisor.doctor_user_id == current_user.user_id,
            MedicalSupervisor.patient_id == patient_id,
            MedicalSupervisor.status == "Active"
        ).first()
        if not supervision:
            raise HTTPException(status_code=403, detail="Not authorized")
    elif current_user.role == "Nurse":
        profile = db.query(PatientProfile).filter(PatientProfile.patient_id == patient_id).first()
        if not profile or profile.assigned_nurse_id != current_user.user_id:
            raise HTTPException(status_code=403, detail="Not authorized")
    else:
        raise HTTPException(status_code=403, detail="Access denied")

    return db.query(DoseLog).join(MedicationSchedule).join(PatientMedication).filter(
        PatientMedication.patient_id == patient_id
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
    
    if log.status == "Taken":
        raise HTTPException(status_code=400, detail="Dose already marked as taken")

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
        
    check_dose_permission(current_user, log.schedule_id, db)
    
    log.status = "Skipped"
    log.action_timestamp = datetime.utcnow()
    db.commit()
    db.refresh(log)
    return log