from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.medication_catalog import MedicationCatalog
from app.models.user import User
from app.schemas.medication_catalog import MedicationCatalogCreate, MedicationCatalogResponse
from app.utils.security import get_current_user, require_roles

router = APIRouter(prefix="/medication-catalog", tags=["Medication Catalog"])


@router.post("", response_model=MedicationCatalogResponse, status_code=201)
def create_catalog_entry(
    data: MedicationCatalogCreate,
    # 🛡️ الكتالوج مرجع طبي: الأدمن والأطباء فقط يضيفون إليه
    current_user: User = Depends(require_roles(["Admin", "Doctor"])),
    db: Session = Depends(get_db)
):
    entry = MedicationCatalog(**data.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.get("", response_model=List[MedicationCatalogResponse])
def get_catalog(
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(MedicationCatalog).filter(MedicationCatalog.is_active == True)
    if search:
        query = query.filter(MedicationCatalog.generic_name.ilike(f"%{search}%"))
    return query.all()


@router.get("/{medication_id}", response_model=MedicationCatalogResponse)
def get_catalog_entry(
    medication_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    entry = db.query(MedicationCatalog).filter(
        MedicationCatalog.medication_id == medication_id
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Not found")
    return entry