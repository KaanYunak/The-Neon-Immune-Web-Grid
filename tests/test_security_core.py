import pytest
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import app


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

def test_login_get_has_csrf(client):
    r = client.get("/login")
    assert r.status_code == 200
    assert "csrf_token" in r.get_data(as_text=True)

def test_firewall_blocks_suspicious_query(client):
    r = client.get("/?q=<script>alert(1)</script>")
    # firewall before_request -> 400 expected
    assert r.status_code in (400, 403)

def test_security_headers_exist(client):
    r = client.get("/")
    assert r.headers.get("X-Frame-Options") == "DENY"
    assert r.headers.get("X-Content-Type-Options") == "nosniff"
