from app.models.user import User
from app.models.guardianship import Guardianship
from app.models.medication import Medication
from app.models.schedule import MedicationSchedule
from app.models.dose_log import DoseLog
from app.models.notification import Notification
from app.models.patient_profile import PatientProfile
from app.models.doctor import Doctor
from app.models.nurse import Nurse
from app.models.medical_record import PatientMedicalRecord
from app.models.medical_record_note import MedicalRecordNote
from app.models.allergy import PatientAllergy
from app.models.stock_transaction import MedicationStockTransaction
from app.models.medical_supervisor import MedicalSupervisor
from app.models.consent_record import ConsentRecord
from app.models.audit_log import AuditLog
from app.models.ai_extraction_log import AIExtractionLog
from app.models.ai_consultation import AIConsultation
from app.models.medication_catalog import MedicationCatalog
from app.models.patient_medication import PatientMedication

__all__ = [
    "User", "Guardianship", "Medication", "MedicationSchedule",
    "DoseLog", "Notification", "PatientProfile", "Doctor", "Nurse",
    "PatientMedicalRecord", "MedicalRecordNote",
    "PatientAllergy", "MedicationStockTransaction",
    "MedicalSupervisor", "ConsentRecord", "AuditLog",
    "AIExtractionLog", "AIConsultation",
    "MedicationCatalog", "PatientMedication",
]
from app.models.appointment import Appointment
# وأضيفي "Appointment" داخل قائمة __all__