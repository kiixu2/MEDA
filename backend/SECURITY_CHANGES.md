# ملخص التعديلات (v2.1)

**الأمان:** مفتاح JWT وCORS من البيئة · فحص وصول موحد (`utils/permissions.py`) يعتمد علاقة فعلية بالمريض (ذات الدور وحده لا يكفي) ·
وصاية Pending دائماً بموافقة المريض (القاصر: Admin) · إشراف طبي بموافقة المريض · قفل الحساب بعد 5 محاولات ·
التسجيل ينتج Patient فقط وكلمة مرور 8+ · `is_active` يُفحص في كل طلب · الدور/الأطباء/الحالة/الرصيد تؤخذ من الخادم لا العميل.

**أخطاء أُصلحت:** `return Non` في حذف السجل · الممرض/الوصي (Patient) محظورون خطأً · 500 عند مفتاح أجنبي مفقود (الآن 404/409) ·
حذف جدول/دواء له تابعون (الآن 409) · تبديل الموافقة (consent) كان يكسر القيد الفريد · إنشاء إشعار لأي مستخدم · `GET /doctors` بلا مصادقة.

**جديد:** `/guardianships/{id}/approve` و`/pending-requests` · `/medical-supervisors` (طلب/موافقة/إنهاء) · `/patient-profiles/me/nurse` ·
`/doses/patient/{id}` و`/schedules/patient/{id}` · `/appointments/doctor/me` · `interval_hours` و`days_of_week_mask` في الجداول ·
معالج `IntegrityError` عام · `/health` يفحص القاعدة · `tests/` و`scripts/smoke_test.py` · `.gitattributes`.

**لم يُنفَّذ بعد:** Alembic · pagination · كتابة `audit_logs` تلقائياً · خصم المخزون عند أخذ الجرعة · تعديل/إيقاف `patient_medications` ·
مسار لإنشاء حسابات Doctor/Nurse/Admin من الواجهة (حالياً عبر `seed_db.py`) · إنشاء حساب قاصر بواسطة وليّه.
