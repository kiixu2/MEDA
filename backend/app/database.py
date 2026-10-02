from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# مسار قاعدة البيانات (SQLite - ملف محلي)
SQLALCHEMY_DATABASE_URL = "sqlite:///./meda.db"

# إنشاء الاتصال بقاعدة البيانات
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# جلسة التعامل مع قاعدة البيانات
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# الأساس اللي بتورث منه كل الجداول
Base = declarative_base()


# دالة للحصول على جلسة قاعدة البيانات
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()