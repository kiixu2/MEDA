from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models
from app.routes import auth, medications, schedules, doses, notifications

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

@app.get("/")
def home():
    return {"message": "Welcome to MEDA"}


@app.get("/health")
def health_check():
    return {"status": "OK", "database": "connected"}
