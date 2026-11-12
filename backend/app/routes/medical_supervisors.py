from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.doctor import Doctor
from app.models.medical_supervisor import MedicalSupervisor
from app.models.user import User
from app.schemas.medical_supervisor import MedicalSupervisorCreate, MedicalSupervisorResponse
from app.utils.clock import utcnow
from app.utils.permissions import get_patient_profile_or_404
from app.utils.security import get_current_user, require_roles

router = APIRouter(prefix="/medical-supervisors", tags=["Medical Supervisors"])


@router.post("", response_model=MedicalSupervisorResponse, status_code=201)
def request_supervision(
    data: MedicalSupervisorCreate,
    current_user: User = Depends(require_roles(["Doctor"])),
    db: Session = Depends(get_db)
):
    """الطبيب يطلب الإشراف: Pending حتى يوافق المريض."""
    if not db.query(Doctor).filter(Doctor.user_id == current_user.user_id).first():
        raise HTTPException(status_code=400, detail="Create your doctor profile first")
    get_patient_profile_or_404(db, data.patient_id)

    existing = db.query(MedicalSupervisor).filter(
        MedicalSupervisor.doctor_user_id == current_user.user_id,
        MedicalSupervisor.patient_id == data.patient_id,
        MedicalSupervisor.status.in_(["Pending", "Active"])
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Supervision already requested or active")

    supervisor = MedicalSupervisor(
        doctor_user_id=current_user.user_id,   # من التوكن لا من العميل
        patient_id=data.patient_id,
        status="Pending",
        notes=data.notes,
    )
    db.add(supervisor)
    db.commit()
    db.refresh(supervisor)
    return supervisor


@router.get("/my-patients", response_model=List[MedicalSupervisorResponse])
def get_my_patients(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(MedicalSupervisor).filter(
        MedicalSupervisor.doctor_user_id == current_user.user_id,
        MedicalSupervisor.status == "Active"
    ).all()


@router.get("/my-doctors", response_model=List[MedicalSupervisorResponse])
def get_my_doctors(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(MedicalSupervisor).filter(
        MedicalSupervisor.patient_id == current_user.user_id,
        MedicalSupervisor.status == "Active"
    ).all()


@router.get("/pending-requests", response_model=List[MedicalSupervisorResponse])
def get_pending_requests(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """للمريض: طلبات إشراف الأطباء التي تنتظر موافقته."""
    return db.query(MedicalSupervisor).filter(
        MedicalSupervisor.patient_id == current_user.user_id,
        MedicalSupervisor.status == "Pending"
    ).all()


@router.put("/{supervisor_id}/approve", response_model=MedicalSupervisorResponse)
def approve_supervision(
    supervisor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """المريض نفسه فقط يوافق على الطبيب."""
    s = db.query(MedicalSupervisor).filter(
        MedicalSupervisor.supervisor_id == supervisor_id,
        MedicalSupervisor.patient_id == current_user.user_id,
        MedicalSupervisor.status == "Pending"
    ).first()
    if not s:
        raise HTTPException(status_code=404, detail="Pending request not found")
    s.status = "Active"
    s.assigned_at_utc = utcnow()
    db.commit()
    db.refresh(s)
    return s


@router.put("/{supervisor_id}/end", response_model=MedicalSupervisorResponse)
def end_supervision(
    supervisor_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """إنهاء/رفض الإشراف: المريض أو الطبيب نفسه."""
    s = db.query(MedicalSupervisor).filter(
        MedicalSupervisor.supervisor_id == supervisor_id
    ).first()
    if not s or current_user.user_id not in (s.patient_id, s.doctor_user_id):
        raise HTTPException(status_code=404, detail="Supervision not found")
    s.status = "Ended"
    s.ended_at_utc = utcnow()
    db.commit()
    db.refresh(s)
    return s
