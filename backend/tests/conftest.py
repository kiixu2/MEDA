import os
import sys
import tempfile

# يجب ضبط البيئة قبل استيراد التطبيق
_tmp = tempfile.mkdtemp(prefix="meda_test_")
os.environ["MEDA_DATABASE_URL"] = "sqlite:///" + os.path.join(_tmp, "test.db").replace("\\", "/")
os.environ["MEDA_SECRET_KEY"] = "test-secret-key-for-pytest-only-0123456789"
os.environ["MEDA_SEED_PASSWORD"] = "Password123"
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app.utils import security
# تسريع الاختبارات: bcrypt بعدد جولات قليل (للاختبار فقط)
security.pwd_context = CryptContext(schemes=["bcrypt"], bcrypt__rounds=4)

from app.database import Base, engine  # noqa: E402
from main import app  # noqa: E402
import seed_db  # noqa: E402

PASSWORD = "Password123"


@pytest.fixture()
def client():
    """قاعدة بيانات نظيفة + بيانات seed لكل اختبار."""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    seed_db.seed()
    with TestClient(app) as c:
        yield c


class Session:
    def __init__(self, client, email):
        r = client.post("/auth/login", json={"email": email, "password": PASSWORD})
        assert r.status_code == 200, r.text
        body = r.json()
        self.id = body["user"]["user_id"]
        self.h = {"Authorization": f"Bearer {body['access_token']}"}


@pytest.fixture()
def login(client):
    def _login(email):
        return Session(client, email)
    return _login
