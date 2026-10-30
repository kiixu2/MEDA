from sqlalchemy import Column, Integer, String, Numeric, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class MedicationCatalog(Base):
    __tablename__ = "medication_catalog"

    medication_id = Column(Integer, primary_key=True, index=True)
    generic_name = Column(String(200), nullable=False)
    brand_name = Column(String(200), nullable=True)
    dosage_form = Column(String(100), nullable=False)
    route = Column(String(100), nullable=True)
    concentration = Column(Numeric(12, 3), nullable=True)
    concentration_unit = Column(String(30), nullable=True)
    quantity_unit = Column(String(30), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at_utc = Column(DateTime(timezone=True), server_default=func.now())

    # 👇 العلاقة هنا صارت سليمة
    patient_medications = relationship("PatientMedication", back_populates="medication")