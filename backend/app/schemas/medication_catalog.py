from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class MedicationCatalogBase(BaseModel):
    generic_name: str
    brand_name: Optional[str] = None
    dosage_form: str
    route: Optional[str] = None
    concentration: Optional[Decimal] = None
    concentration_unit: Optional[str] = None
    quantity_unit: str


class MedicationCatalogCreate(MedicationCatalogBase):
    pass


class MedicationCatalogResponse(MedicationCatalogBase):
    medication_id: int
    is_active: bool
    created_at_utc: datetime

    class Config:
        from_attributes = True