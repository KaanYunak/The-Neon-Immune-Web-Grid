import os
import json
import pytest
import sys

sys.path.insert(0, os.path.abspath("."))

from app import app  # Flask app


DIM_LOG = "dim_threat_memory.json"


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def _read_dim_log(path=DIM_LOG):
    assert os.path.exists(path), f"{path} not found. DIM may not be writing logs."
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read().strip()

    # Try JSON first
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Try JSON lines into list
        objs = []
        for ln in raw.splitlines():
            ln = ln.strip()
            if not ln:
                continue
            try:
                objs.append(json.loads(ln))
            except Exception:
                pass
        return objs


def test_normal_user_flow_ok(client):
    """
    Normal user flow should work (not blocked by firewall).
    """
    resp = client.get("/dashboard")
    assert resp.status_code in (200, 302), f"Unexpected status: {resp.status_code}"


def test_catch_all_honeypot_probe_is_logged(client):
    """
    Probing a suspicious path should be captured/logged by DIM via catch-all route.
    """
    resp = client.get("/backup.sql")
    # catch-all might return 200 (honeypot page) or 404; both acceptable as long as logged
    assert resp.status_code in (200, 404, 403)

    data = _read_dim_log()
    text = json.dumps(data).lower()

    assert "/backup.sql" in text, "Expected probe endpoint to appear in DIM logs."
    # module names can vary in case
    assert "honeypot" in text or "dummy" in text, "Expected honeypot/catch-all tagging in DIM logs."
    assert "severity" in text, "Expected severity field in DIM logs."


def test_dashboard_threats_api_returns_data(client):
    """
    DIM + Dashboard integration validation:
    /api/dashboard/threats should respond and include threat data after a probe.
    """
    # Ensure at least one threat exists
    client.get("/backup.sql")

    resp = client.get("/api/dashboard/threats")
    assert resp.status_code == 200

    # Response should be JSON
    payload = resp.get_json(silent=True)
    assert payload is not None, "Expected JSON response from /api/dashboard/threats"

    # Accept either list or dict-based payloads
    payload_text = json.dumps(payload).lower()
    assert "threat" in payload_text or "severity" in payload_text or "endpoint" in payload_text, \
        "Threat API response doesn't look like threat data."
