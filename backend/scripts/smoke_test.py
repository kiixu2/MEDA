"""
تجربة سريعة على خادم يعمل فعلاً (بدون أي مكتبات خارجية).

  1) python seed_db.py
  2) uvicorn main:app --reload
  3) python scripts/smoke_test.py            (أو: python scripts/smoke_test.py http://127.0.0.1:8000)
"""
import json
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8000"
PASSWORD = "Password123"
results = []


def call(method, path, token=None, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw else None)
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw)
        except Exception:
            return e.code, raw.decode(errors="ignore")


def check(name, actual, expected):
    ok = actual in expected if isinstance(expected, (tuple, list, set)) else actual == expected
    results.append(ok)
    print(("  PASS " if ok else "  FAIL ") + f"{name}  (got {actual}, expected {expected})")


def login(email):
    status, body = call("POST", "/auth/login", body={"email": email, "password": PASSWORD})
    assert status == 200, f"login failed for {email}: {status} {body}"
    return body["access_token"], body["user"]["user_id"]


print(f"== MEDA smoke test on {BASE}")
check("health", call("GET", "/health")[0], 200)

patient, patient_id = login("patient@test.com")
doctor, doctor_id = login("doctor@test.com")
nurse, _ = login("nurse@test.com")
caregiver, _ = login("caregiver@test.com")
stranger, stranger_id = login("stranger@test.com")
admin, _ = login("admin@test.com")

print("-- التسجيل لا يعطي صلاحيات")
s, b = call("POST", "/auth/register", body={
    "full_name": "Smoke User", "username": "smoke_user_x", "email": "smoke_x@test.com",
    "phone_number": "700123456", "date_of_birth": "1990-01-01", "gender": "Male",
    "password": PASSWORD, "role": "Admin"})
check("register forces role=Patient", b.get("role") if s == 201 else "exists", ("Patient", "exists"))

print("-- بيانات المريض: من يصل ومن لا يصل")
check("patient reads own meds", call("GET", "/patient-medications", patient)[0], 200)
check("supervised doctor reads patient meds", call("GET", f"/patient-medications/patient/{patient_id}", doctor)[0], 200)
check("assigned nurse reads patient meds", call("GET", f"/patient-medications/patient/{patient_id}", nurse)[0], 200)
check("active guardian reads patient meds", call("GET", f"/patient-medications/patient/{patient_id}", caregiver)[0], 200)
check("stranger blocked from patient meds", call("GET", f"/patient-medications/patient/{patient_id}", stranger)[0], 403)
check("stranger blocked from records", call("GET", f"/medical-records/patient/{patient_id}", stranger)[0], 403)

print("-- وصاية: طلب ثم موافقة")
s, g = call("POST", "/guardianships", stranger, {
    "dependent_patient_id": patient_id, "relationship_type": "Friend",
    "can_view_history": True, "can_manage_medications": False})
check("guardianship request is Pending", g.get("status") if isinstance(g, dict) else s, "Pending")
check("still blocked before approval", call("GET", f"/patient-medications/patient/{patient_id}", stranger)[0], 403)
gid = g["guardianship_id"]
check("guardian cannot self-approve", call("PUT", f"/guardianships/{gid}/approve", stranger)[0], 404)
check("patient approves", call("PUT", f"/guardianships/{gid}/approve", patient, {})[0], 200)
check("view-only guardian now reads", call("GET", f"/patient-medications/patient/{patient_id}", stranger)[0], 200)
check("patient revokes", call("DELETE", f"/guardianships/{gid}", patient)[0], 204)
check("blocked again after revoke", call("GET", f"/patient-medications/patient/{patient_id}", stranger)[0], 403)

print("-- سجلات طبية")
check("patient cannot create record", call("POST", "/medical-records", patient, {
    "patient_id": patient_id, "condition": "X", "patient_status": "Y"})[0], 403)
s, rec = call("POST", "/medical-records", doctor, {
    "patient_id": patient_id, "doctor_user_id": 9999, "condition": "Hypertension", "patient_status": "Stable"})
check("supervised doctor creates record", s, 201)
check("doctor_user_id taken from token", rec.get("doctor_user_id") if isinstance(rec, dict) else None, doctor_id)
check("unsupervised: doctor blocked for stranger", call("POST", "/medical-records", doctor, {
    "patient_id": stranger_id, "condition": "X", "patient_status": "Y"})[0], (403, 404))
check("delete record -> 204", call("DELETE", f"/medical-records/{rec['record_id']}", doctor)[0], 204)

print("-- مسارات أخرى")
check("doctors list needs auth", call("GET", "/doctors")[0], (401, 403))
check("patient cannot add to catalog", call("POST", "/medication-catalog", patient, {
    "generic_name": "X", "dosage_form": "Tablet", "quantity_unit": "Tablet"})[0], 403)
check("stranger cannot notify patient", call("POST", "/notifications", stranger, {
    "user_id": patient_id, "title": "t", "message": "m", "scheduled_for": "2026-12-01T08:00:00"})[0], 403)

passed = sum(results)
print(f"\n{passed}/{len(results)} checks passed")
sys.exit(0 if passed == len(results) else 1)
