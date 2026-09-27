from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="MEDA API")

# ====== نموذج الدواء ======
class Medication(BaseModel):
    name: str
    dosage: str
    time: str

# ====== قاعدة بيانات مؤقتة (في الذاكرة) ======
medications_db = []

# ====== API: الصفحة الرئيسية ======
@app.get("/")
def home():
    return {"message": "Welcome to MEDA"}

# ====== API: عرض كل الأدوية ======
@app.get("/medications")
def get_all_medications():
    return {
        "count": len(medications_db),
        "medications": medications_db
    }

# ====== API: إضافة دواء جديد ======
@app.post("/medications")
def add_medication(med: Medication):
    new_med = {
        "id": len(medications_db) + 1,
        "name": med.name,
        "dosage": med.dosage,
        "time": med.time
    }
    medications_db.append(new_med)
    return {
        "message": "Medication added successfully",
        "medication": new_med
    }