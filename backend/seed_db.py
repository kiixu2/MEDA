"""
بيانات تجريبية للتطوير فقط (آمن للتشغيل أكثر من مرة: ينشئ الناقص فقط).

  python seed_db.py

كلمة المرور من MEDA_SEED_PASSWORD (الافتراضي: Password123 - للتطوير فقط!).
المستخدمون:
  admin@test.com      Admin
  doctor@test.com     Doctor   (مشرف نشط على patient@test.com)
  nurse@test.com      Nurse    (معيّن لـ patient@test.com)
  patient@test.com    Patient  (بالغ)
  caregiver@test.com  Patient  (وصي نشط على patient@test.com)
  stranger@test.com   Patient  (لا علاقة له بأحد - لاختبار الرفض)
"""
import os
from datetime import date

from app.database import SessionLocal, engine, Base
from app import models  # noqa: F401
from app.models.user import User
from app.models.patient_profile import PatientProfile
from app.models.doctor import Doctor
from app.models.nurse import Nurse
from app.models.guardianship import Guardianship
from app.models.medical_supervisor import MedicalSupervisor
from app.models.medication_catalog import MedicationCatalog
from app.models.patient_medication import PatientMedication
from app.utils.clock import utcnow
from app.utils.security import hash_password

PASSWORD = os.getenv("MEDA_SEED_PASSWORD", "Password123")


def get_or_create_user(db, email, username, full_name, phone, role, dob):
    user = db.query(User).filter(User.email == email).first()
    if user:
        # نُحدّث كلمة المرور لتطابق PASSWORD (مفيد لو القاعدة قديمة)
        user.password_hash = hash_password(PASSWORD)
        user.is_active = True
        user.failed_login_count = 0
        user.locked_until_utc = None
        db.commit()
        return user
    user = User(
        full_name=full_name, username=username, email=email, phone_number=phone,
        date_of_birth=dob, gender="Male", password_hash=hash_password(PASSWORD), role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = get_or_create_user(db, "admin@test.com", "admin_test", "أدمن تجريبي", "777000111", "Admin", date(1985, 1, 1))
        doctor = get_or_create_user(db, "doctor@test.com", "doctor_test", "دكتور تجريبي", "777333444", "Doctor", date(1980, 1, 1))
        nurse = get_or_create_user(db, "nurse@test.com", "nurse_test", "ممرض تجريبي", "777555666", "Nurse", date(1990, 5, 5))
        patient = get_or_create_user(db, "patient@test.com", "patient_test", "مريض تجريبي", "777111222", "Patient", date(1950, 1, 1))
        caregiver = get_or_create_user(db, "caregiver@test.com", "caregiver_test", "وصي تجريبي", "777222333", "Patient", date(1985, 3, 3))
        stranger = get_or_create_user(db, "stranger@test.com", "stranger_test", "شخص غريب", "777888999", "Patient", date(1992, 2, 2))

        if not db.query(PatientProfile).filter(PatientProfile.patient_id == patient.user_id).first():
            db.add(PatientProfile(patient_id=patient.user_id, blood_type="O+"))
        if not db.query(Doctor).filter(Doctor.user_id == doctor.user_id).first():
            db.add(Doctor(user_id=doctor.user_id, license_number="DOC-12345", specialty="Cardiology"))
        if not db.query(Nurse).filter(Nurse.user_id == nurse.user_id).first():
            db.add(Nurse(user_id=nurse.user_id, license_number="NUR-12345", department="General"))
        db.commit()

        profile = db.query(PatientProfile).filter(PatientProfile.patient_id == patient.user_id).first()
        profile.assigned_nurse_id = nurse.user_id

        if not db.query(MedicalSupervisor).filter(
            MedicalSupervisor.doctor_user_id == doctor.user_id,
            MedicalSupervisor.patient_id == patient.user_id).first():
            db.add(MedicalSupervisor(doctor_user_id=doctor.user_id, patient_id=patient.user_id, status="Active"))

        if not db.query(Guardianship).filter(
            Guardianship.guardian_user_id == caregiver.user_id,
            Guardianship.dependent_patient_id == patient.user_id).first():
            db.add(Guardianship(
                guardian_user_id=caregiver.user_id, dependent_patient_id=patient.user_id,
                relationship_type="Son", can_view_history=True, can_manage_medications=True,
                status="Active", granted_at_utc=utcnow()))

        med = db.query(MedicationCatalog).filter(MedicationCatalog.generic_name == "Paracetamol").first()
        if not med:
            med = MedicationCatalog(
                generic_name="Paracetamol", brand_name="Panadol", dosage_form="Tablet",
                route="Oral", concentration=500, concentration_unit="mg", quantity_unit="Tablet")
            db.add(med)
        db.commit()
        db.refresh(med)

        pm = db.query(PatientMedication).filter(
            PatientMedication.patient_id == patient.user_id,
            PatientMedication.medication_id == med.medication_id).first()
        if not pm:
            pm = PatientMedication(
                patient_id=patient.user_id, medication_id=med.medication_id,
                prescribed_by_doctor_id=doctor.user_id, prescribed_quantity=30,
                quantity_on_hand=30, low_stock_threshold=5, instructions="حبة بعد الفطور",
                status="Active", start_date=date.today())
            db.add(pm)
            db.commit()
            db.refresh(pm)

        print("✅ Database seeded successfully!")
        print(f"   password for all test users: {PASSWORD}")
        for u in (admin, doctor, nurse, patient, caregiver, stranger):
            print(f"   {u.role:8} id={u.user_id:<3} {u.email}")
        print(f"   PatientMedication ID: {pm.patient_medication_id}")
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding DB: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
