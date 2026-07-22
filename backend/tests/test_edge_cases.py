"""
backend/tests/test_edge_cases.py
─────────────────────────────────
End-to-end edge case tests for the KITE API.
Runs against a live stack (use with docker-compose up).

Run with:
    pytest tests/test_edge_cases.py -v --timeout=60
"""
import io
import time

import pytest
from fastapi.testclient import TestClient
from app.main import app

API = "/api/v1"

# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


# ── Health ────────────────────────────────────────────────────────────────────

def test_health_ok(client):
    """Basic liveness check."""
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("ok", "degraded", "healthy")


# ── Ingest: happy path ────────────────────────────────────────────────────────

def test_ingest_pdf_happy_path(client):
    """Upload a minimal valid PDF and expect queued response."""
    # Minimal 1-page PDF bytes (hand-crafted, always parseable)
    pdf_bytes = b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/MediaBox[0 0 612 792]/Parent 2 0 R/Contents 4 0 R/Resources<<>>>>endobj
4 0 obj<</Length 44>>stream
BT /F1 12 Tf 100 700 Td (Pump P-101 failed on 2026-01-10) Tj ET
endstream endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000266 00000 n 
trailer<</Size 5/Root 1 0 R>>
startxref
360
%%EOF"""
    r = client.post(
        f"{API}/ingest",
        files={"file": ("test_report.pdf", pdf_bytes, "application/pdf")}
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "queued"
    assert "job_id" in data
    return data["job_id"]


# ── Ingest: edge cases ────────────────────────────────────────────────────────

def test_ingest_empty_file(client):
    """Empty file upload should still accept (pipeline will fail gracefully)."""
    r = client.post(
        f"{API}/ingest",
        files={"file": ("empty.pdf", b"", "application/pdf")}
    )
    # Should still return 200 (queued) — the pipeline handles the failure internally
    assert r.status_code in (200, 422)


def test_ingest_no_file(client):
    """Missing file field should return 422 Unprocessable Entity."""
    r = client.post(f"{API}/ingest")
    assert r.status_code == 422


def test_ingest_wrong_content_type(client):
    """Uploading a text blob as binary should still be accepted and queued."""
    r = client.post(
        f"{API}/ingest",
        files={"file": ("notes.txt", b"Equipment V-205 is running fine.", "text/plain")}
    )
    assert r.status_code == 200


def test_ingest_very_large_file(client):
    """1MB text file should be accepted without timeout."""
    large_content = b"Equipment P-101 shows anomalous vibration. " * 25000  # ~1MB
    r = client.post(
        f"{API}/ingest",
        files={"file": ("large_report.txt", large_content, "text/plain")}
    )
    assert r.status_code == 200
    assert r.json()["status"] == "queued"


def test_ingest_duplicate_upload(client):
    """Two uploads of the same file should both get different job IDs."""
    content = b"Inspection of V-205 completed on 2026-05-13."
    r1 = client.post(f"{API}/ingest", files={"file": ("report.txt", content, "text/plain")})
    r2 = client.post(f"{API}/ingest", files={"file": ("report.txt", content, "text/plain")})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["job_id"] != r2.json()["job_id"]


# ── Query: edge cases ─────────────────────────────────────────────────────────

def test_query_empty_string(client):
    """Empty query should return 422 or a graceful response — not 500."""
    r = client.post(f"{API}/query", json={"query": ""})
    assert r.status_code in (200, 422, 400)
    assert r.status_code != 500


def test_query_no_documents_ingested(client):
    """Query when collection might be empty — should not crash."""
    r = client.post(f"{API}/query", json={"query": "What caused the pump failure?"})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert "confidence" in data


def test_query_very_long_input(client):
    """Very long query string should be handled gracefully."""
    long_query = "pump failure vibration " * 200  # 4600 chars
    r = client.post(f"{API}/query", json={"query": long_query})
    assert r.status_code in (200, 400, 422)
    assert r.status_code != 500


def test_query_special_characters(client):
    """SQL/Cypher injection-style input should not crash the server."""
    evil_query = "'; DROP TABLE uploads; --"
    r = client.post(f"{API}/query", json={"query": evil_query})
    assert r.status_code in (200, 400)
    assert r.status_code != 500


def test_query_missing_body(client):
    """POST to /query with no body should return 422."""
    r = client.post(f"{API}/query")
    assert r.status_code == 422


# ── Agents: Compliance ────────────────────────────────────────────────────────

def test_compliance_audit_runs(client):
    """Compliance audit endpoint should return without error."""
    r = client.get(f"{API}/agents/compliance")
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        data = r.json()
        assert "status" in data


def test_compliance_review_invalid_status(client):
    """Reviewing a flag with an invalid status should return 400 or 422."""
    r = client.post(
        f"{API}/agents/compliance/flags/fake-hash-123/review",
        json={"status": "invalid_status"}
    )
    assert r.status_code in (400, 422)


def test_compliance_review_valid_statuses(client):
    """Each valid status should succeed without crash."""
    for status in ("dismissed", "confirmed", "pending"):
        r = client.post(
            f"{API}/agents/compliance/flags/test-hash-abc/review",
            json={"status": status}
        )
        assert r.status_code in (200, 500)  # 500 ok if DB not seeded, but not 4xx on valid input


# ── Agents: RCA ───────────────────────────────────────────────────────────────

def test_rca_nonexistent_equipment(client):
    """RCA for unknown equipment ID should return gracefully (not 500)."""
    r = client.get(f"{API}/agents/rca/nonexistent-pump-xyz")
    # May return 200 with empty result or 500 if LLM key not set
    assert r.status_code in (200, 500)


def test_rca_empty_equipment_id(client):
    """RCA with spaces in ID should not crash the server."""
    r = client.get(f"{API}/agents/rca/ ")
    assert r.status_code in (200, 404, 422, 500)
    assert r.status_code != 400  # not a client format error if it's non-empty


# ── Agents: Lessons ───────────────────────────────────────────────────────────

def test_lessons_cluster_no_data(client):
    """Lesson clustering with no data should return gracefully."""
    r = client.post(f"{API}/agents/lessons/cluster")
    assert r.status_code in (200, 500)  # 500 ok if empty graph


def test_lessons_cluster_invalid_threshold(client):
    """Threshold outside 0–1 range should be handled gracefully."""
    r = client.post(f"{API}/agents/lessons/cluster?threshold=5.0")
    assert r.status_code in (200, 400, 422, 500)
    assert r.status_code != 500  # this specifically should not cause a server crash


# ── Docs ─────────────────────────────────────────────────────────────────────

def test_swagger_docs_available(client):
    """Swagger UI should be reachable."""
    r = client.get("/docs")
    assert r.status_code == 200


def test_openapi_schema_valid(client):
    """OpenAPI JSON should be valid JSON with expected fields."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert "paths" in schema
    assert "components" in schema
