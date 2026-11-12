"""
إعدادات المشروع - كلها تُقرأ من متغيرات البيئة (Environment Variables).

المتغيرات:
  MEDA_SECRET_KEY    مفتاح توقيع JWT (إجباري في الإنتاج)
  MEDA_ENV           development (الافتراضي) أو production
  MEDA_CORS_ORIGINS  قائمة مصادر مسموحة مفصولة بفاصلة
  MEDA_DATABASE_URL  رابط قاعدة البيانات (الافتراضي: ملف meda.db بجانب main.py)
  MEDA_ACCESS_TOKEN_MINUTES  مدة صلاحية التوكن بالدقائق
"""
import logging
import os
import secrets

logger = logging.getLogger("meda")

ENV = os.getenv("MEDA_ENV", "development").lower()

_secret = os.getenv("MEDA_SECRET_KEY")
if not _secret:
    if ENV == "production":
        raise RuntimeError("MEDA_SECRET_KEY must be set when MEDA_ENV=production")
    # في التطوير: مفتاح عشوائي لكل تشغيل (التوكنات القديمة تنتهي عند إعادة تشغيل الخادم)
    _secret = secrets.token_urlsafe(64)
    logger.warning(
        "MEDA_SECRET_KEY is not set - using a random key for this process only. "
        "Set it in your environment to keep tokens valid across restarts."
    )
SECRET_KEY = _secret

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("MEDA_ACCESS_TOKEN_MINUTES", str(60 * 8)))

# CORS: مصادر محددة بدل "*"
_default_origins = (
    "http://127.0.0.1:5500,http://localhost:5500,"
    "http://127.0.0.1:3000,http://localhost:3000,"
    "http://127.0.0.1:8000,http://localhost:8000"
)
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("MEDA_CORS_ORIGINS", _default_origins).split(",")
    if o.strip()
]

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # مجلد backend
DATABASE_URL = os.getenv(
    "MEDA_DATABASE_URL",
    "sqlite:///" + os.path.join(_BASE_DIR, "meda.db").replace("\\", "/"),
)

# قفل الحساب بعد محاولات فاشلة
MAX_FAILED_LOGINS = 5
LOCKOUT_MINUTES = 15
