
from fastapi import FastAPI
from app.database import engine, Base

# استيراد الموديلات (مهم: قبل create_all)
from app.models import user

# إنشاء الجداول في قاعدة البيانات
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MEDA API")


@app.get("/")
def home():
    return {"message": "Welcome to MEDA"}


@app.get("/health")
def health_check():
    return {"status": "OK", "database": "connected"}