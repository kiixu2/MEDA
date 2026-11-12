# MEDA
Smart medication management system for elderly people

## تشغيل الباك إند

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # ويندوز  (لينكس/ماك: source venv/bin/activate)
pip install -r requirements.txt
```

متغيرات البيئة (اختيارية في التطوير، **إجبارية في الإنتاج**):

| المتغير | الوصف |
|---|---|
| `MEDA_SECRET_KEY` | مفتاح توقيع JWT. بدونه يُولَّد مفتاح عشوائي لكل تشغيل (التوكنات تنتهي عند إعادة التشغيل). |
| `MEDA_ENV` | `development` (الافتراضي) أو `production` (يرفض التشغيل بدون المفتاح) |
| `MEDA_CORS_ORIGINS` | مصادر الواجهة المسموحة مفصولة بفاصلة (مثال: `https://app.example.com`) |
| `MEDA_DATABASE_URL` | رابط قاعدة البيانات (الافتراضي: `backend/meda.db`) |
| `MEDA_SEED_PASSWORD` | كلمة مرور حسابات التجربة (الافتراضي `Password123`) |

توليد مفتاح قوي: `python -c "import secrets; print(secrets.token_urlsafe(64))"`

```bash
python seed_db.py                 # بيانات تجريبية (آمن للتكرار)
uvicorn main:app --reload         # التوثيق التفاعلي: http://127.0.0.1:8000/docs
```

الاختبارات: `pip install -r requirements-dev.txt` ثم `pytest`

أوامر تجربة الـ API: [`backend/API_TESTING.md`](backend/API_TESTING.md)
