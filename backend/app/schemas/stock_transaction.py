from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class StockTransactionBase(BaseModel):
    medication_id: int
    transaction_type: str
    quantity_change: Decimal
    balance_after: Decimal
    reason: Optional[str] = None


class StockTransactionCreate(StockTransactionBase):
    pass


class StockTransactionResponse(StockTransactionBase):
    transaction_id: int
    performed_by_user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True