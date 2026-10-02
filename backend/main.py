from fastapi import FastAPI
from app.database import engine, Base

# استيراد كل الموديلات (مهم قبل create_all)
from app import models

# إنشاء الجداول في قاعدة البيانات
Base.metadata.create_all(bind=engine)

app = FastAPI(title="MEDA API")


@app.get("/")
def home():
    return {"message": "Welcome to MEDA"}


@app.get("/health")
def health_check():
    return {"status": "OK", "database": "connected"}
