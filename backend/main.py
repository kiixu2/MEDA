from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models
from app.routes import (
    auth, medications, schedules, doses, notifications,
    guardianships, patient_profiles, doctors,
    medical_records, allergies, stock_transactions,
    medical_supervisors, consent_records, audit_logs,
    ai_extraction_logs, ai_consultations,
    medication_catalog, patient_medications,
    nurses, medical_record_notes
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MEDA API", version="2.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(medications.router)
app.include_router(schedules.router)
app.include_router(doses.router)
app.include_router(notifications.router)
app.include_router(guardianships.router)
app.include_router(patient_profiles.router)
app.include_router(doctors.router)
app.include_router(nurses.router)
app.include_router(medical_records.router)
app.include_router(medical_record_notes.router)
app.include_router(allergies.router)
app.include_router(stock_transactions.router)
app.include_router(medical_supervisors.router)
app.include_router(consent_records.router)
app.include_router(audit_logs.router)
app.include_router(ai_extraction_logs.router)
app.include_router(ai_consultations.router)
app.include_router(medication_catalog.router)
app.include_router(patient_medications.router)


@app.get("/")
def home():
    return {"message": "Welcome to MEDA v2"}


@app.get("/health")
def health_check():
    return {"status": "OK", "database": "connected"}