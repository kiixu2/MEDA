from pydantic import BaseModel
from datetime import datetime


class MedicalRecordNoteBase(BaseModel):
    note_type: str
    note_text: str


class MedicalRecordNoteCreate(MedicalRecordNoteBase):
    record_id: int


class MedicalRecordNoteResponse(MedicalRecordNoteBase):
    note_id: int
    record_id: int
    created_by_user_id: int
    created_at_utc: datetime

    class Config:
        from_attributes = True