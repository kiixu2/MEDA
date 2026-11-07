from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.medical_record import PatientMedicalRecord
from app.models.user import User
from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordResponse
from app.utils.security import get_current_user, require_roles
from app.utils.permissions import require_patient_access

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])


@router.post("", response_model=MedicalRecordResponse, status_code=201)
def create_record(
    data: MedicalRecordCreate,
    # 🛡️ الحماية: الطبيب والممرض فقط يمكنهم إنشاء سجل طبي
    current_user: User = Depends(require_roles(["Doctor", "Nurse"])),
    db: Session = Depends(get_db)
):
    # 💡 التعديل الأمني: نأخذ الـ doctor_user_id من التوكن، ونمسحه لو كان موجود في البيانات المرسلة
    record_data = data.model_dump()
    record_data.pop("doctor_user_id", None) # نمسحه لو جاي من المستخدم
    record_data.pop("created_by_user_id", None) # نمسحه لو جاي من المستخدم
    
    record = PatientMedicalRecord(
        **record_data,
        doctor_user_id=current_user.user_id, # نأخذه من التوكن (آمن)
        created_by_user_id=current_user.user_id # نأخذه من التوكن (آمن)
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("", response_model=List[MedicalRecordResponse])
def get_my_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(PatientMedicalRecord).filter(
        PatientMedicalRecord.patient_id == current_user.user_id
    ).all()


@router.get("/patient/{patient_id}", response_model=List[MedicalRecordResponse])
def get_patient_records(
    patient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # الأطباء والممرضين يسمح لهم بالرؤية، والوصي يسمح له إذا عنده صلاحية
    if current_user.role not in ["Doctor", "Nurse"]:
        require_patient_access(current_user, patient_id, "view_history", db)
        
    return db.query(PatientMedicalRecord).filter(
        PatientMedicalRecord.patient_id == patient_id
    ).all()


@router.delete("/{record_id}", status_code=204)
def delete_record(
    record_id: int,
    # 🛡️ الحماية: الطبيب فقط هو من يحق له الحذف، وليس الوصي أو المريض
    current_user: User = Depends(require_roles(["Doctor"])),
    db: Session = Depends(get_db)
):
    record = db.query(PatientMedicalRecord).filter(
        PatientMedicalRecord.record_id == record_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # 💡 التعديل الأمني: الطبيب لا يمكنه حذف إلا السجل الذي أنشأه هو
    if record.created_by_user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, 
            detail="You can only delete medical records you created"
        )
        
    db.delete(record)
    db.commit()
    return Non