from datetime import date

PASSWORD = "Password123"


def _register(client, email, username, phone, dob="1990-01-01", **extra):
    return client.post("/auth/register", json={
        "full_name": "Test User", "username": username, "email": email,
        "phone_number": phone, "date_of_birth": dob, "gender": "Male",
        "password": PASSWORD, **extra,
    })


# ---------- المصادقة ----------
def test_register_forces_patient_role(client):
    r = _register(client, "x@test.com", "x_user", "700000001", role="Admin")
    assert r.status_code == 201
    assert r.json()["role"] == "Patient"


def test_register_rejects_short_password(client):
    r = client.post("/auth/register", json={
        "full_name": "Test", "username": "short", "email": "s@test.com",
        "phone_number": "700000002", "date_of_birth": "1990-01-01",
        "gender": "Male", "password": "123"})
    assert r.status_code == 422


def test_login_lockout_after_failed_attempts(client):
    for _ in range(5):
        assert client.post("/auth/login", json={"email": "patient@test.com", "password": "wrong"}).status_code == 401
    r = client.post("/auth/login", json={"email": "patient@test.com", "password": PASSWORD})
    assert r.status_code == 423


def test_protected_route_requires_token(client):
    assert client.get("/doctors").status_code in (401, 403)
    assert client.get("/medications").status_code in (401, 403)


def test_invalid_token_rejected(client):
    r = client.get("/medications", headers={"Authorization": "Bearer not.a.token"})
    assert r.status_code == 401


# ---------- الوصاية ----------
def test_guardianship_requires_patient_approval(client, login):
    stranger, patient = login("stranger@test.com"), login("patient@test.com")

    r = client.post("/guardianships", headers=stranger.h, json={
        "dependent_patient_id": patient.id, "relationship_type": "Friend",
        "can_view_history": True, "can_manage_medications": True})
    assert r.status_code == 201
    g = r.json()
    assert g["status"] == "Pending"

    # قبل الموافقة: لا وصول
    assert client.get(f"/patient-medications/patient/{patient.id}", headers=stranger.h).status_code == 403
    assert client.get(f"/medical-records/patient/{patient.id}", headers=stranger.h).status_code == 403

    # الوصي لا يستطيع تفعيل نفسه ولا الموافقة
    assert client.put(f"/guardianships/{g['guardianship_id']}/approve", headers=stranger.h).status_code == 404
    client.put(f"/guardianships/{g['guardianship_id']}", headers=stranger.h, json={"status": "Active"})
    assert client.get(f"/patient-medications/patient/{patient.id}", headers=stranger.h).status_code == 403

    # المريض يوافق بصلاحية عرض فقط
    r = client.put(f"/guardianships/{g['guardianship_id']}/approve", headers=patient.h,
                   json={"can_view_history": True, "can_manage_medications": False})
    assert r.status_code == 200 and r.json()["status"] == "Active"
    assert client.get(f"/patient-medications/patient/{patient.id}", headers=stranger.h).status_code == 200
    assert client.post("/stock-transactions", headers=stranger.h,
                       json={"medication_id": 1, "transaction_type": "Add", "quantity_change": 1}).status_code in (403, 404)


def test_guardian_cannot_escalate_own_permissions(client, login):
    caregiver, patient = login("caregiver@test.com"), login("patient@test.com")
    gid = client.get("/guardianships/my-patients", headers=caregiver.h).json()[0]["guardianship_id"]
    # الوصي يحاول رفع صلاحياته: تُتجاهل
    patient_view = client.put(f"/guardianships/{gid}", headers=patient.h,
                              json={"can_manage_medications": False})
    assert patient_view.json()["can_manage_medications"] is False
    r = client.put(f"/guardianships/{gid}", headers=caregiver.h, json={"can_manage_medications": True})
    assert r.json()["can_manage_medications"] is False


def test_patient_can_revoke_guardian(client, login):
    caregiver, patient = login("caregiver@test.com"), login("patient@test.com")
    gid = client.get("/guardianships/my-patients", headers=caregiver.h).json()[0]["guardianship_id"]
    assert client.delete(f"/guardianships/{gid}", headers=patient.h).status_code == 204
    assert client.get(f"/patient-medications/patient/{patient.id}", headers=caregiver.h).status_code == 403


def test_minor_guardianship_needs_admin(client, login):
    # قاصر يسجل ويُنشئ ملفه
    assert _register(client, "kid@test.com", "kid_user", "700000003", dob="2016-05-05").status_code == 201
    kid = login("kid@test.com")
    assert client.post("/patient-profiles", headers=kid.h, json={}).status_code == 201

    stranger, admin = login("stranger@test.com"), login("admin@test.com")
    g = client.post("/guardianships", headers=stranger.h, json={
        "dependent_patient_id": kid.id, "relationship_type": "Father",
        "can_view_history": True, "can_manage_medications": True}).json()
    assert g["status"] == "Pending"  # حتى للقاصر: لا Active تلقائي

    # القاصر نفسه لا يوافق، والغريب لا يوافق
    assert client.put(f"/guardianships/{g['guardianship_id']}/approve", headers=kid.h).status_code == 404
    assert client.put(f"/guardianships/{g['guardianship_id']}/approve", headers=stranger.h).status_code == 404
    # الأدمن يرى الطلب ويوافق
    pend = client.get("/guardianships/pending-requests", headers=admin.h).json()
    assert any(p["guardianship_id"] == g["guardianship_id"] for p in pend)
    assert client.put(f"/guardianships/{g['guardianship_id']}/approve", headers=admin.h).json()["status"] == "Active"


def test_guardianship_requires_patient_profile(client, login):
    # مستخدم بدون patient_profile -> 404 وليس 500
    caregiver = login("caregiver@test.com")
    stranger = login("stranger@test.com")
    r = client.post("/guardianships", headers=stranger.h, json={
        "dependent_patient_id": caregiver.id, "relationship_type": "Friend"})
    assert r.status_code == 404


# ---------- الأطباء والممرضون ----------
def test_unsupervised_doctor_has_no_access(client, login):
    # طبيب جديد بدون إشراف على stranger
    stranger, doctor = login("stranger@test.com"), login("doctor@test.com")
    assert client.post("/patient-profiles", headers=stranger.h, json={}).status_code == 201
    assert client.get(f"/medical-records/patient/{stranger.id}", headers=doctor.h).status_code == 403
    assert client.get(f"/patient-medications/patient/{stranger.id}", headers=doctor.h).status_code == 403
    assert client.get(f"/schedules/patient/{stranger.id}", headers=doctor.h).status_code == 403
    assert client.post("/medical-records", headers=doctor.h, json={
        "patient_id": stranger.id, "condition": "X", "patient_status": "Stable"}).status_code == 403


def test_supervision_requires_patient_approval(client, login):
    stranger, doctor = login("stranger@test.com"), login("doctor@test.com")
    client.post("/patient-profiles", headers=stranger.h, json={})
    r = client.post("/medical-supervisors", headers=doctor.h, json={"patient_id": stranger.id})
    assert r.status_code == 201 and r.json()["status"] == "Pending"
    sid = r.json()["supervisor_id"]
    assert client.get(f"/medical-records/patient/{stranger.id}", headers=doctor.h).status_code == 403
    assert client.put(f"/medical-supervisors/{sid}/approve", headers=doctor.h).status_code == 404  # الطبيب لا يوافق بنفسه
    assert client.put(f"/medical-supervisors/{sid}/approve", headers=stranger.h).status_code == 200
    assert client.get(f"/medical-records/patient/{stranger.id}", headers=doctor.h).status_code == 200


def test_doctor_record_flow_and_delete(client, login):
    doctor, patient = login("doctor@test.com"), login("patient@test.com")
    r = client.post("/medical-records", headers=doctor.h, json={
        "patient_id": patient.id, "doctor_user_id": 9999,   # يُتجاهل
        "condition": "Hypertension", "patient_status": "Stable"})
    assert r.status_code == 201
    rec = r.json()
    assert rec["doctor_user_id"] == doctor.id and rec["created_by_user_id"] == doctor.id

    # ملاحظة ثم حذف السجل (يحذف الملاحظات تلقائياً) -> 204
    assert client.post("/medical-record-notes", headers=doctor.h, json={
        "record_id": rec["record_id"], "note_type": "FollowUp", "note_text": "ok"}).status_code == 201
    assert client.delete(f"/medical-records/{rec['record_id']}", headers=doctor.h).status_code == 204


def test_patient_cannot_create_or_delete_records_or_notes(client, login):
    doctor, patient = login("doctor@test.com"), login("patient@test.com")
    assert client.post("/medical-records", headers=patient.h, json={
        "patient_id": patient.id, "condition": "X", "patient_status": "Y"}).status_code == 403
    rec = client.post("/medical-records", headers=doctor.h, json={
        "patient_id": patient.id, "condition": "X", "patient_status": "Y"}).json()
    note = client.post("/medical-record-notes", headers=doctor.h, json={
        "record_id": rec["record_id"], "note_type": "FollowUp", "note_text": "n"}).json()
    assert client.delete(f"/medical-record-notes/{note['note_id']}", headers=patient.h).status_code == 403
    assert client.delete(f"/medical-records/{rec['record_id']}", headers=patient.h).status_code == 403


def test_nurse_assigned_access_but_cannot_create_record(client, login):
    nurse, patient = login("nurse@test.com"), login("patient@test.com")
    assert client.get(f"/patient-medications/patient/{patient.id}", headers=nurse.h).status_code == 200
    assert client.post("/medical-records", headers=nurse.h, json={
        "patient_id": patient.id, "condition": "X", "patient_status": "Y"}).status_code == 403
    # ممرض غير معيّن على مريض آخر
    stranger = login("stranger@test.com")
    client.post("/patient-profiles", headers=stranger.h, json={})
    assert client.get(f"/patient-medications/patient/{stranger.id}", headers=nurse.h).status_code == 403


def test_patient_can_assign_nurse(client, login):
    stranger, nurse = login("stranger@test.com"), login("nurse@test.com")
    client.post("/patient-profiles", headers=stranger.h, json={})
    assert client.get(f"/patient-medications/patient/{stranger.id}", headers=nurse.h).status_code == 403
    r = client.put("/patient-profiles/me/nurse", headers=stranger.h, json={"nurse_user_id": nurse.id})
    assert r.status_code == 200 and r.json()["assigned_nurse_id"] == nurse.id
    assert client.get(f"/patient-medications/patient/{stranger.id}", headers=nurse.h).status_code == 200


# ---------- مسارات أخرى ----------
def test_notifications_cannot_target_arbitrary_user(client, login):
    stranger, patient = login("stranger@test.com"), login("patient@test.com")
    payload = {"title": "t", "message": "m", "scheduled_for": "2026-12-01T08:00:00", "user_id": patient.id}
    assert client.post("/notifications", headers=stranger.h, json=payload).status_code == 403
    assert client.post("/notifications", headers=stranger.h, json={**payload, "user_id": stranger.id}).status_code == 201


def test_catalog_create_restricted(client, login):
    patient, doctor = login("patient@test.com"), login("doctor@test.com")
    body = {"generic_name": "Ibuprofen", "dosage_form": "Tablet", "quantity_unit": "Tablet"}
    assert client.post("/medication-catalog", headers=patient.h, json=body).status_code == 403
    assert client.post("/medication-catalog", headers=doctor.h, json=body).status_code == 201


def test_stock_balance_computed_server_side(client, login):
    patient = login("patient@test.com")
    med = client.post("/medications", headers=patient.h, json={"name": "A", "dosage_form": "Tablet", "total_quantity": 10}).json()
    r = client.post("/stock-transactions", headers=patient.h, json={
        "medication_id": med["medication_id"], "transaction_type": "Add",
        "quantity_change": 5, "balance_after": 99999})  # balance_after يُتجاهل
    assert r.status_code == 201 and float(r.json()["balance_after"]) == 15
    r = client.post("/stock-transactions", headers=patient.h, json={
        "medication_id": med["medication_id"], "transaction_type": "Use", "quantity_change": -100})
    assert r.status_code == 400
    # حذف دواء له سجل مخزون -> 409 وليس 500
    assert client.delete(f"/medications/{med['medication_id']}", headers=patient.h).status_code == 409


def _first_pm(client, patient):
    return client.get("/patient-medications", headers=patient.h).json()[0]["patient_medication_id"]


def test_dose_flow(client, login):
    patient = login("patient@test.com")
    pm = _first_pm(client, patient)
    sched = client.post("/schedules", headers=patient.h, json={
        "patient_medication_id": pm, "frequency_type": "Daily", "dose_quantity": 1,
        "dose_time_local": "08:00:00", "start_date": "2026-11-10"})
    assert sched.status_code == 201
    sid = sched.json()["schedule_id"]

    log = client.post("/doses", headers=patient.h, json={
        "schedule_id": sid, "scheduled_datetime": "2026-11-10T08:00:00", "status": "Taken"}).json()
    assert log["status"] == "Pending"  # الحالة من العميل تُتجاهل
    assert client.post(f"/doses/{log['log_id']}/take", headers=patient.h).status_code == 200
    assert client.post(f"/doses/{log['log_id']}/take", headers=patient.h).status_code == 400
    assert client.post(f"/doses/{log['log_id']}/skip", headers=patient.h).status_code == 400

    # الجدول له سجل جرعات -> 409
    assert client.delete(f"/schedules/{sid}", headers=patient.h).status_code == 409


def test_other_users_cannot_touch_doses(client, login):
    patient, stranger = login("patient@test.com"), login("stranger@test.com")
    pm = _first_pm(client, patient)
    sid = client.post("/schedules", headers=patient.h, json={
        "patient_medication_id": pm, "frequency_type": "Daily", "dose_quantity": 1,
        "dose_time_local": "08:00:00", "start_date": "2026-11-10"}).json()["schedule_id"]
    log = client.post("/doses", headers=patient.h, json={
        "schedule_id": sid, "scheduled_datetime": "2026-11-10T08:00:00"}).json()
    assert client.post(f"/doses/{log['log_id']}/take", headers=stranger.h).status_code == 403
    assert client.get(f"/schedules/{sid}", headers=stranger.h).status_code == 403


def test_consent_toggle_does_not_crash(client, login):
    patient = login("patient@test.com")
    body = {"consent_type": "Privacy", "policy_version": "1.0", "granted": True}
    assert client.post("/consents", headers=patient.h, json=body).status_code == 201
    r = client.post("/consents", headers=patient.h, json={**body, "granted": False})
    assert r.status_code == 201 and r.json()["granted"] is False
    assert len(client.get("/consents/me", headers=patient.h).json()) == 1


def test_appointments(client, login):
    patient, stranger = login("patient@test.com"), login("stranger@test.com")
    doctor = login("doctor@test.com")
    body = {"patient_id": patient.id, "doctor_user_id": doctor.id, "appointment_date": "2026-12-01T10:00:00"}
    assert client.post("/appointments", headers=patient.h, json=body).status_code == 201   # المريض يحجز لنفسه
    assert client.post("/appointments", headers=stranger.h, json=body).status_code == 403  # الغريب لا


def test_supervision_unknown_patient_is_404(client, login):
    doctor = login("doctor@test.com")
    r = client.post("/medical-supervisors", headers=doctor.h, json={"patient_id": 99999})
    assert r.status_code == 404
