from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.medical_record import PatientMedicalRecord
from app.models.medical_record_note import MedicalRecordNote
from app.models.user import User
from app.schemas.medical_record_note import (
    MedicalRecordNoteCreate, MedicalRecordNoteResponse
)
from app.utils.permissions import require_patient_access, VIEW_HISTORY
from app.utils.security import get_current_user, require_roles

router = APIRouter(prefix="/medical-record-notes", tags=["Medical Record Notes"])


def _get_record_or_404(db: Session, record_id: int) -> PatientMedicalRecord:
    record = db.query(PatientMedicalRecord).filter(
        PatientMedicalRecord.record_id == record_id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record


@router.post("", response_model=MedicalRecordNoteResponse, status_code=201)
def create_note(
    data: MedicalRecordNoteCreate,
    # 🛡️ الطبيب والممرض فقط، وبشرط وجود علاقة فعلية مع المريض
    current_user: User = Depends(require_roles(["Doctor", "Nurse"])),
    db: Session = Depends(get_db)
):
    record = _get_record_or_404(db, data.record_id)
    require_patient_access(current_user, record.patient_id, VIEW_HISTORY, db)

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
    record = _get_record_or_404(db, record_id)
    require_patient_access(current_user, record.patient_id, VIEW_HISTORY, db)

    return db.query(MedicalRecordNote).filter(
        MedicalRecordNote.record_id == record_id
    ).all()


@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: int,
    current_user: User = Depends(require_roles(["Doctor", "Nurse"])),
    db: Session = Depends(get_db)
):
    note = db.query(MedicalRecordNote).filter(
        MedicalRecordNote.note_id == note_id
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # 🛡️ ما يحذف إلا كاتب الملاحظة
    if note.created_by_user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="You can only delete notes you created")

    db.delete(note)
    db.commit()
    return None
