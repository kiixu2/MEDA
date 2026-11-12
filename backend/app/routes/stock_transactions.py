from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.medication import Medication
from app.models.stock_transaction import MedicationStockTransaction
from app.models.user import User
from app.schemas.stock_transaction import StockTransactionCreate, StockTransactionResponse
from app.utils.permissions import require_patient_access, MANAGE_MEDICATIONS
from app.utils.security import get_current_user

router = APIRouter(prefix="/stock-transactions", tags=["Stock Transactions"])


def _get_med_or_404(db: Session, medication_id: int) -> Medication:
    med = db.query(Medication).filter(Medication.medication_id == medication_id).first()
    if not med:
        raise HTTPException(status_code=404, detail="Medication not found")
    return med


@router.post("", response_model=StockTransactionResponse, status_code=201)
def create_transaction(
    data: StockTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    med = _get_med_or_404(db, data.medication_id)
    require_patient_access(current_user, med.patient_id, MANAGE_MEDICATIONS, db)

    # 🛡️ الرصيد الجديد يُحسب في الخادم (لا نثق بقيمة العميل)
    current_qty = Decimal(med.total_quantity or 0)
    new_balance = current_qty + data.quantity_change
    if new_balance < 0:
        raise HTTPException(status_code=400, detail="Insufficient stock: balance cannot be negative")

    med.total_quantity = new_balance
    transaction = MedicationStockTransaction(
        performed_by_user_id=current_user.user_id,
        balance_after=new_balance,
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
    med = _get_med_or_404(db, medication_id)
    require_patient_access(current_user, med.patient_id, MANAGE_MEDICATIONS, db)

    return db.query(MedicationStockTransaction).filter(
        MedicationStockTransaction.medication_id == medication_id
    ).all()
