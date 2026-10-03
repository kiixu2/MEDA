from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class MedicationStockTransaction(Base):
    __tablename__ = "medication_stock_transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.medication_id"), nullable=False, index=True)
    transaction_type = Column(String(30), nullable=False)
    quantity_change = Column(Numeric(10, 2), nullable=False)
    balance_after = Column(Numeric(10, 2), nullable=False)
    performed_by_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    medication = relationship("Medication", backref="stock_transactions")