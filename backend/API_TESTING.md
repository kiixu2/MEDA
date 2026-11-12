# تجربة MEDA API

## 0) التشغيل
```bash
cd backend
pip install -r requirements.txt
python seed_db.py
uvicorn main:app --reload
```
افتح **http://127.0.0.1:8000/docs** (Swagger): اضغط **Authorize** والصق التوكن، وجرّب أي مسار بالضغط.

حسابات `seed_db.py` (كلمة المرور `Password123`):

| الإيميل | الدور | العلاقة |
|---|---|---|
| `patient@test.com` | Patient | مريض بالغ (له دواء) |
| `doctor@test.com` | Doctor | مشرف نشط على المريض |
| `nurse@test.com` | Nurse | ممرض معيّن للمريض |
| `caregiver@test.com` | Patient | وصي نشط على المريض (عرض + إدارة) |
| `stranger@test.com` | Patient | لا علاقة له بأحد (لاختبار الرفض) |
| `admin@test.com` | Admin | يوافق على وصاية القاصرين |

## 1) أسرع طريقة: سكربت التجربة
```bash
python scripts/smoke_test.py          # يشغّل ~25 فحصاً ويطبع PASS/FAIL
pytest                                # الاختبارات الآلية الكاملة
```

## 2) أوامر curl
> **ويندوز PowerShell:** اكتب `curl.exe` (وليس `curl`)، واستخدم Git Bash لتجنب مشاكل علامات الاقتباس،
> أو احفظ الـ JSON في ملف واستعمل `-d "@body.json"`.

```bash
BASE=http://127.0.0.1:8000

# دخول (يرجع access_token)
curl -s -X POST $BASE/auth/login -H "Content-Type: application/json" \
  -d '{"email":"patient@test.com","password":"Password123"}'

# احفظ التوكنات في متغيرات (يحتاج jq؛ أو انسخ التوكن يدوياً)
login() { curl -s -X POST $BASE/auth/login -H "Content-Type: application/json" \
  -d "{\"email\":\"$1\",\"password\":\"Password123\"}" | jq -r .access_token; }
PAT=$(login patient@test.com); DOC=$(login doctor@test.com); NUR=$(login nurse@test.com)
STR=$(login stranger@test.com); ADM=$(login admin@test.com)
PID=$(curl -s $BASE/auth/login -H "Content-Type: application/json" \
  -d '{"email":"patient@test.com","password":"Password123"}' | jq .user.user_id)
```

### التسجيل (دائماً Patient حتى لو أرسلت role)
```bash
curl -s -X POST $BASE/auth/register -H "Content-Type: application/json" -d '{
 "full_name":"علي أحمد","username":"ali_1","email":"ali@test.com","phone_number":"700111222",
 "date_of_birth":"1990-05-01","gender":"Male","password":"Password123","role":"Admin"}'
# المتوقع: 201 و "role":"Patient"
```

### الأدوية والجداول والجرعات (كمريض)
```bash
curl -s $BASE/patient-medications -H "Authorization: Bearer $PAT"          # خذ patient_medication_id

curl -s -X POST $BASE/schedules -H "Authorization: Bearer $PAT" -H "Content-Type: application/json" -d '{
 "patient_medication_id":1,"frequency_type":"Daily","dose_quantity":1,
 "dose_time_local":"08:00:00","start_date":"2026-11-10"}'

curl -s -X POST $BASE/doses -H "Authorization: Bearer $PAT" -H "Content-Type: application/json" -d '{
 "schedule_id":1,"scheduled_datetime":"2026-11-10T08:00:00"}'

curl -s -X POST $BASE/doses/1/take -H "Authorization: Bearer $PAT"    # 200
curl -s -X POST $BASE/doses/1/take -H "Authorization: Bearer $PAT"    # 400 (مأخوذة سابقاً)
```

### الوصاية: طلب ← موافقة ← إلغاء
```bash
# الغريب يطلب (Pending)
curl -s -X POST $BASE/guardianships -H "Authorization: Bearer $STR" -H "Content-Type: application/json" \
  -d "{\"dependent_patient_id\":$PID,\"relationship_type\":\"Friend\",\"can_view_history\":true,\"can_manage_medications\":false}"

# بدون موافقة: يجب أن يرفض (403)
curl -s -o /dev/null -w "%{http_code}\n" $BASE/patient-medications/patient/$PID -H "Authorization: Bearer $STR"

# المريض يرى الطلبات ويوافق (ويحدد الصلاحيات)
curl -s $BASE/guardianships/pending-requests -H "Authorization: Bearer $PAT"
curl -s -X PUT $BASE/guardianships/GID/approve -H "Authorization: Bearer $PAT" -H "Content-Type: application/json" \
  -d '{"can_view_history":true,"can_manage_medications":false}'

# المريض يلغي
curl -s -X DELETE $BASE/guardianships/GID -H "Authorization: Bearer $PAT"
```
> للقاصر (أقل من 18) الموافقة بيد **Admin** فقط: `PUT /guardianships/GID/approve` بتوكن `$ADM`.

### الإشراف الطبي والسجلات (كطبيب)
```bash
# الطبيب يطلب الإشراف على مريض (يحتاج موافقة المريض)
curl -s -X POST $BASE/medical-supervisors -H "Authorization: Bearer $DOC" -H "Content-Type: application/json" -d "{\"patient_id\":$PID}"
curl -s $BASE/medical-supervisors/pending-requests -H "Authorization: Bearer $PAT"
curl -s -X PUT $BASE/medical-supervisors/SID/approve -H "Authorization: Bearer $PAT"

# سجل طبي (الطبيب المشرف فقط؛ doctor_user_id من التوكن)
curl -s -X POST $BASE/medical-records -H "Authorization: Bearer $DOC" -H "Content-Type: application/json" \
  -d "{\"patient_id\":$PID,\"condition\":\"Hypertension\",\"patient_status\":\"Stable\"}"
curl -s -X POST $BASE/medical-record-notes -H "Authorization: Bearer $DOC" -H "Content-Type: application/json" \
  -d '{"record_id":1,"note_type":"FollowUp","note_text":"مراجعة بعد أسبوعين"}'
```

### تعيين ممرض (المريض يعيّنه)
```bash
NID=$(curl -s $BASE/auth/login -H "Content-Type: application/json" -d '{"email":"nurse@test.com","password":"Password123"}' | jq .user.user_id)
curl -s -X PUT $BASE/patient-profiles/me/nurse -H "Authorization: Bearer $PAT" -H "Content-Type: application/json" -d "{\"nurse_user_id\":$NID}"
```

### المخزون (الرصيد يُحسب في الخادم)
```bash
curl -s -X POST $BASE/medications -H "Authorization: Bearer $PAT" -H "Content-Type: application/json" \
  -d '{"name":"Aspirin","dosage_form":"Tablet","total_quantity":10}'
curl -s -X POST $BASE/stock-transactions -H "Authorization: Bearer $PAT" -H "Content-Type: application/json" \
  -d '{"medication_id":1,"transaction_type":"Add","quantity_change":5}'          # balance_after = 15
```

> الأرقام (`1`، `GID`، `SID`) في الأمثلة تأتي من ردود الطلبات السابقة وقد تختلف عندك حسب محتوى قاعدتك.

## 3) ما يجب أن يفشل (علامة أن الأمان يعمل)

| الطلب | المتوقع |
|---|---|
| تسجيل بـ `"role":"Admin"` | 201 لكن الدور `Patient` |
| قراءة بيانات المريض بتوكن `stranger` | 403 |
| طبيب غير مشرف يقرأ سجلات المريض | 403 |
| المريض ينشئ سجلاً طبياً | 403 |
| وصي يوافق على طلبه بنفسه | 404 |
| `POST /notifications` لمستخدم آخر بدون علاقة | 403 |
| `GET /doctors` بدون توكن | 401/403 |
| 5 محاولات دخول خاطئة ثم الصحيحة | 423 (قفل 15 دقيقة) |
| `POST /doses/{id}/take` مرتين | 400 |
| مخزون سالب | 400 |
| حذف جدول له سجل جرعات | 409 |
