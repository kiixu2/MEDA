from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base

# مسار قاعدة البيانات (SQLite - ملف محلي)
SQLALCHEMY_DATABASE_URL = "sqlite:///./meda.db"

# إنشاء الاتصال بقاعدة البيانات
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# 🛡️ التعديل الأمني: تفعيل حماية العلاقات (Foreign Keys) في SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

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