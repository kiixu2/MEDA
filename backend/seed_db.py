from app.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.patient_profile import PatientProfile
from app.models.doctor import Doctor
from app.models.medication_catalog import MedicationCatalog
from app.models.patient_medication import PatientMedication
from app.utils.security import hash_password
from datetime import date

def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(User).first():
            print("Database already has data. Skipping seed.")
            return

        # 1. Create Patient
        patient = User(
            full_name="مريض تجريبي", username="patient_test", email="patient@test.com",
            phone_number="777111222", date_of_birth=date(1990, 1, 1), gender="Male",
            password_hash=hash_password("password123"), role="Patient"
        )
        db.add(patient)
        db.commit()
        db.refresh(patient)
        db.add(PatientProfile(patient_id=patient.user_id, blood_type="O+"))
        db.commit()

        # 2. Create Doctor
        doctor = User(
            full_name="دكتور تجريبي", username="doctor_test", email="doctor@test.com",
            phone_number="777333444", date_of_birth=date(1980, 1, 1), gender="Male",
            password_hash=hash_password("password123"), role="Doctor"
        )
        db.add(doctor)
        db.commit()
        db.refresh(doctor)
        db.add(Doctor(user_id=doctor.user_id, license_number="DOC-12345", specialty="Cardiology"))
        db.commit()

        # 3. Create Medication Catalog
        med = MedicationCatalog(
            generic_name="Paracetamol", brand_name="Panadol", dosage_form="Tablet",
            route="Oral", concentration=500, concentration_unit="mg", quantity_unit="Tablet"
        )
        db.add(med)
        db.commit()
        db.refresh(med)

        # 4. Create Patient Medication
        pm = PatientMedication(
            patient_id=patient.user_id, medication_id=med.medication_id,
            prescribed_by_doctor_id=doctor.user_id, prescribed_quantity=30,
            quantity_on_hand=30, low_stock_threshold=5, instructions="حبة بعد الفطور",
            status="Active", start_date=date.today()
        )
        db.add(pm)
        db.commit()
        db.refresh(pm)

        print("✅ Database seeded successfully!")
        print(f"👉 PatientMedication ID: {pm.patient_medication_id}")
        print("👨‍⚕️ Doctor: doctor@test.com / password123")
        print("🤒 Patient: patient@test.com / password123")

    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding DB: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()