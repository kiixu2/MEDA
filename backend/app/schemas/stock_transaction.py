from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal


class StockTransactionCreate(BaseModel):
    """balance_after يُحسب في الخادم ولا يُقبل من العميل."""
    medication_id: int
    transaction_type: str
    quantity_change: Decimal
    reason: Optional[str] = None


class StockTransactionResponse(BaseModel):
    transaction_id: int
    medication_id: int
    transaction_type: str
    quantity_change: Decimal
    balance_after: Decimal
    reason: Optional[str] = None
    performed_by_user_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
