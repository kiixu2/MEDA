from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.stock_transaction import MedicationStockTransaction
from app.models.medication import Medication
from app.models.user import User
from app.schemas.stock_transaction import (
    StockTransactionCreate, StockTransactionResponse
)
from app.utils.security import get_current_user
from app.utils.permissions import require_patient_access

router = APIRouter(prefix="/stock-transactions", tags=["Stock Transactions"])


@router.post("", response_model=StockTransactionResponse, status_code=201)
def create_transaction(
    data: StockTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    med = db.query(Medication).filter(
        Medication.medication_id == data.medication_id
    ).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")

    require_patient_access(current_user, med.patient_id, "manage_medications", db)

    # تحديث الكمية في Medications
    med.total_quantity = data.balance_after

    transaction = MedicationStockTransaction(
        performed_by_user_id=current_user.user_id,
        **data.model_dump()
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


@router.get("/medication/{medication_id}", response_model=List[StockTransactionResponse])
def get_medication_transactions(
    medication_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    med = db.query(Medication).filter(
        Medication.medication_id == medication_id
    ).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")

    require_patient_access(current_user, med.patient_id, "manage_medications", db)

    return db.query(MedicationStockTransaction).filter(
        MedicationStockTransaction.medication_id == medication_id
    ).all()