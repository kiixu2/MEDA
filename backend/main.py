import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.config import CORS_ORIGINS
from app.database import engine, Base, SessionLocal
from app import models  # noqa: F401  (يسجل كل الجداول في Base)
from app.routes import (
    auth, medications, schedules, doses, notifications,
    guardianships, patient_profiles, doctors,
    medical_records, allergies, stock_transactions,
    medical_supervisors, consent_records, audit_logs,
    ai_extraction_logs, ai_consultations,
    medication_catalog, patient_medications,
    nurses, medical_record_notes, appointments
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("meda")

# إنشاء الجداول (للتطوير. للإنتاج يُفضّل Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MEDA API", version="2.1.0")

# 🛡️ CORS: مصادر محددة من MEDA_CORS_ORIGINS (بدل "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,   # نستخدم Bearer token في الـ Header، لا كوكيز
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    # بدل 500 مبهم: تعارض بيانات (تكرار/مفتاح أجنبي غير موجود/قيد)
    logger.warning("IntegrityError on %s %s: %s", request.method, request.url.path, exc.orig)
    return JSONResponse(
        status_code=409,
        content={"detail": "Data conflict: a related record is missing, duplicated, or in use."},
    )


# Routes
for r in (
    auth, medications, schedules, doses, notifications, guardianships,
    patient_profiles, doctors, nurses, medical_records, medical_record_notes,
    allergies, stock_transactions, medical_supervisors, consent_records,
    audit_logs, ai_extraction_logs, ai_consultations, medication_catalog,
    patient_medications, appointments,
):
    app.include_router(r.router)


@app.get("/")
def home():
    return {"message": "Welcome to MEDA API v2.1"}


@app.get("/health")
def health_check():
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        return {"status": "OK", "database": "connected"}
    except Exception:
        logger.exception("Health check failed")
        return JSONResponse(status_code=503, content={"status": "ERROR", "database": "unavailable"})
