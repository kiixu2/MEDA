from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models
from app.routes import (
    auth, medications, schedules, doses, notifications,
    guardianships, patient_profiles, doctors,
    medical_records, allergies, stock_transactions
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="MEDA API", version="1.0.0")

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
app.include_router(medical_records.router)
app.include_router(allergies.router)
app.include_router(stock_transactions.router)


@app.get("/")
def home():
    return {"message": "Welcome to MEDA"}


@app.get("/health")
def health_check():
    return {"status": "OK", "database": "connected"}