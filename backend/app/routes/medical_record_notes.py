from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.medical_record_note import MedicalRecordNote
from app.models.medical_record import PatientMedicalRecord
from app.models.user import User
from app.schemas.medical_record_note import (
    MedicalRecordNoteCreate, MedicalRecordNoteResponse
)
from app.utils.security import get_current_user, require_roles
from app.utils.permissions import require_patient_access

router = APIRouter(prefix="/medical-record-notes", tags=["Medical Record Notes"])


@router.post("", response_model=MedicalRecordNoteResponse, status_code=201)
def create_note(
    data: MedicalRecordNoteCreate,
    # 🛡️ التعديل الأمني: الطبيب والممرض فقط يكتبون الملاحظات الطبية
    current_user: User = Depends(require_roles(["Doctor", "Nurse"])),
    db: Session = Depends(get_db)
):
    record = db.query(PatientMedicalRecord).filter(
        PatientMedicalRecord.record_id == data.record_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    note = MedicalRecordNote(
        created_by_user_id=current_user.user_id,
        **data.model_dump()
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/record/{record_id}", response_model=List[MedicalRecordNoteResponse])
def get_record_notes(
    record_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    record = db.query(PatientMedicalRecord).filter(
        PatientMedicalRecord.record_id == record_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # الأطباء والممرضين يقرون عادي، المريض أو الوصي يحتاجون تحقق
    if current_user.role not in ["Doctor", "Nurse"]:
        require_patient_access(current_user, record.patient_id, "view_history", db)

    return db.query(MedicalRecordNote).filter(
        MedicalRecordNote.record_id == record_id
    ).all()


@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: int,
    # 🛡️ التعديل الأمني: الطبيب والممرض فقط يملكون حق الحذف
    current_user: User = Depends(require_roles(["Doctor", "Nurse"])),
    db: Session = Depends(get_db)
):
    note = db.query(MedicalRecordNote).filter(
        MedicalRecordNote.note_id == note_id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # 💡 التعديل الأمني: ما يقدر يحذف إلا الملاحظة اللي هو كتبها بنفسه
    if note.created_by_user_id != current_user.user_id:
        raise HTTPException(
            status_code=403, 
            detail="You can only delete notes you created"
        )

    db.delete(note)
    db.commit()
    return None