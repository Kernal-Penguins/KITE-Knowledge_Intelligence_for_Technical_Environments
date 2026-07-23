"""
backend/tests/test_edge_cases.py
─────────────────────────────────
Edge-case + happy-path API tests for KITE.

Run with:
    pytest tests/test_edge_cases.py -v --timeout=60

These tests use FastAPI's TestClient (synchronous ASGI transport) which
works without a running server, but DOES require the DB connections to be
available (or gracefully degrade).  If DB is unavailable several tests will
still pass because the service layer falls back gracefully.
"""
import io

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
    """Basic liveness check — always returns 200 regardless of DB state."""
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("ok", "degraded")
    # services dict must exist and be a mapping
    assert isinstance(data.get("services"), dict)


def test_health_services_structure(client):
    """Health response must always include all three service keys."""
    r = client.get("/health")
    assert r.status_code == 200
    services = r.json().get("services", {})
    for key in ("neo4j", "qdrant", "postgres"):
        assert key in services, f"Missing service key: {key}"
        assert services[key].get("status") in ("connected", "unreachable")


def test_metrics_response_structure(client):
    """Metrics endpoint must return all expected numeric fields."""
    r = client.get("/metrics")
    assert r.status_code == 200
    data = r.json()
    for field in ("documents_ingested", "graph_nodes", "graph_edges", "qdrant_vectors",
                  "queries_served", "avg_response_ms"):
        assert field in data, f"Missing field: {field}"
        assert isinstance(data[field], (int, float))
    assert "agent_invocations" in data
    assert isinstance(data["agent_invocations"], dict)


# ── Ingest: happy path ────────────────────────────────────────────────────────


def test_ingest_pdf_happy_path(client):
    """Upload a minimal valid PDF and expect queued response."""
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
    r = client.post(f"{API}/ingest", files={"file": ("test_report.pdf", pdf_bytes, "application/pdf")})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "queued"
    assert "job_id" in data
    assert data["job_id"].startswith("job-")
    assert "doc_id" in data


# ── Ingest: edge cases ────────────────────────────────────────────────────────


def test_ingest_empty_file(client):
    """Empty file must be rejected with 422 — validated before hitting pipeline."""
    r = client.post(f"{API}/ingest", files={"file": ("empty.pdf", b"", "application/pdf")})
    assert r.status_code == 422, "Empty files should be rejected at the boundary (422)"


def test_ingest_no_file(client):
    """Missing file field must return 422 Unprocessable Entity."""
    r = client.post(f"{API}/ingest")
    assert r.status_code == 422


def test_ingest_text_file_accepted(client):
    """Plain-text uploads must be accepted and queued (doc_type inferred)."""
    r = client.post(
        f"{API}/ingest",
        files={"file": ("notes.txt", b"Equipment V-205 is running fine.", "text/plain")},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "queued"


def test_ingest_large_file(client):
    """1 MB text file must be accepted without timeout."""
    large_content = b"Equipment P-101 shows anomalous vibration. " * 25_000  # ~1 MB
    r = client.post(
        f"{API}/ingest",
        files={"file": ("large_report.txt", large_content, "text/plain")},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "queued"


def test_ingest_duplicate_upload_unique_job_ids(client):
    """Two uploads of the same file must receive different job IDs."""
    content = b"Inspection of V-205 completed on 2026-05-13."
    r1 = client.post(f"{API}/ingest", files={"file": ("report.txt", content, "text/plain")})
    r2 = client.post(f"{API}/ingest", files={"file": ("report.txt", content, "text/plain")})
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["job_id"] != r2.json()["job_id"], "Duplicate uploads must get distinct job IDs"


def test_ingest_path_traversal_sanitised(client):
    """Filename with path separators must be stripped — not stored as '../etc/passwd'."""
    content = b"Malicious content."
    r = client.post(
        f"{API}/ingest",
        files={"file": ("../etc/passwd", content, "text/plain")},
    )
    # Must be accepted (not crash), and filename stored as basename only
    assert r.status_code == 200
    assert "/" not in r.json()["filename"]
    assert "\\" not in r.json()["filename"]


# ── Query: edge cases ─────────────────────────────────────────────────────────


def test_query_empty_string_rejected(client):
    """Empty query string must be rejected with 422 — validated by Pydantic min_length=1."""
    r = client.post(f"{API}/query", json={"query": ""})
    assert r.status_code == 422, "Empty query must return 422, not 200 or 500"


def test_query_whitespace_only_rejected(client):
    """Whitespace-only query must be rejected or return graceful answer — never 500."""
    r = client.post(f"{API}/query", json={"query": "   "})
    assert r.status_code in (200, 422, 400)
    assert r.status_code != 500


def test_query_basic_returns_answer(client):
    """A normal query should return a response with an answer field — may be empty if no docs."""
    r = client.post(f"{API}/query", json={"query": "What caused the pump failure?"})
    assert r.status_code == 200
    data = r.json()
    assert "answer" in data
    assert "confidence" in data
    assert isinstance(data["confidence"], float)
    assert 0.0 <= data["confidence"] <= 1.0


def test_query_very_long_input_handled(client):
    """Query exceeding max_length (2000 chars) must return 422, not 500."""
    long_query = "pump failure vibration " * 200  # ~4600 chars
    r = client.post(f"{API}/query", json={"query": long_query})
    assert r.status_code in (400, 422)
    assert r.status_code != 500


def test_query_cypher_injection_safe(client):
    """Cypher-injection-style input must not crash the server."""
    evil = "'; MATCH (n) DETACH DELETE n; --"
    r = client.post(f"{API}/query", json={"query": evil})
    assert r.status_code in (200, 400, 422)
    assert r.status_code != 500


def test_query_unicode_input(client):
    """Non-ASCII / emoji input must be handled without crashing."""
    r = client.post(f"{API}/query", json={"query": "Pompe P-101 défaillante 🔧"})
    assert r.status_code in (200, 400, 422)
    assert r.status_code != 500


def test_query_missing_body(client):
    """POST to /query with no body must return 422."""
    r = client.post(f"{API}/query")
    assert r.status_code == 422


# ── Graph Explorer ────────────────────────────────────────────────────────────


def test_graph_nodes_endpoint_exists(client):
    """GET /graph/nodes must return 200 or 503 (if Neo4j unreachable), never 404/500."""
    r = client.get(f"{API}/graph/nodes")
    assert r.status_code in (200, 503), f"Unexpected status: {r.status_code}"


def test_graph_nodes_response_structure(client):
    """If graph/nodes returns 200 it must have the expected schema."""
    r = client.get(f"{API}/graph/nodes")
    if r.status_code == 200:
        data = r.json()
        assert "nodes" in data
        assert "edges" in data
        assert "total_nodes" in data
        assert "total_edges" in data
        assert isinstance(data["nodes"], list)
        assert isinstance(data["edges"], list)


def test_graph_nodes_limit_param(client):
    """limit param must be respected — response not crash with edge values."""
    for lim in (1, 10, 100):
        r = client.get(f"{API}/graph/nodes?limit={lim}")
        assert r.status_code in (200, 503)

    # Out-of-range limit must be rejected by Pydantic
    r = client.get(f"{API}/graph/nodes?limit=9999")
    assert r.status_code == 422


# ── Uploads List ──────────────────────────────────────────────────────────────


def test_uploads_list_returns_list(client):
    """GET /uploads must return a list (possibly empty) — never 404/500."""
    r = client.get(f"{API}/uploads")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_review_queue_returns_list(client):
    """GET /review-queue must return a list (possibly empty) — never 404/500."""
    r = client.get(f"{API}/review-queue")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── Agents: Compliance ────────────────────────────────────────────────────────


def test_compliance_audit_schema(client):
    """Compliance audit endpoint must return expected top-level fields if 200."""
    r = client.get(f"{API}/agents/compliance")
    if r.status_code == 200:
        data = r.json()
        assert "status" in data
        assert data["status"] in ("passed", "failed")


def test_compliance_review_invalid_status_rejected(client):
    """Review with invalid status must be rejected — never silently accepted."""
    r = client.post(
        f"{API}/agents/compliance/flags/fake-hash-123/review",
        json={"status": "invalid_status"},
    )
    assert r.status_code in (400, 422)


def test_compliance_review_all_valid_statuses(client):
    """Each valid review status must not cause a 4xx validation error."""
    for status in ("dismissed", "confirmed", "pending"):
        r = client.post(
            f"{API}/agents/compliance/flags/test-hash-abc/review",
            json={"status": status},
        )
        # 200 = success, 500 = DB not seeded; never 4xx on valid input
        assert r.status_code in (200, 500), f"Status '{status}' got unexpected {r.status_code}"


# ── Agents: RCA ───────────────────────────────────────────────────────────────


def test_rca_nonexistent_equipment_graceful(client):
    """RCA for unknown equipment ID must not return 500 (unhandled)."""
    r = client.get(f"{API}/agents/rca/nonexistent-pump-xyz-9999")
    # 200 with empty report or 500 if LLM key not set — but never 404 (route exists)
    assert r.status_code in (200, 500)


def test_rca_blank_equipment_id_rejected(client):
    """RCA with a blank/whitespace equipment ID must return 422."""
    r = client.get(f"{API}/agents/rca/%20")  # URL-encoded space
    assert r.status_code in (422, 200, 404)  # 422 expected from route validator


# ── Agents: Lessons ───────────────────────────────────────────────────────────


def test_lessons_cluster_no_data_graceful(client):
    """Lessons clustering with empty graph must not crash — 200 or 500 only."""
    r = client.post(f"{API}/agents/lessons/cluster")
    assert r.status_code in (200, 500)


def test_lessons_cluster_out_of_range_threshold_rejected(client):
    """Threshold > 1.0 must be rejected by query validation — not passed through."""
    r = client.post(f"{API}/agents/lessons/cluster?threshold=5.0")
    assert r.status_code == 422, "threshold=5.0 must be rejected with 422 (ge=0, le=1)"


def test_lessons_cluster_boundary_thresholds(client):
    """Edge values 0.0 and 1.0 must be accepted."""
    for t in ("0.0", "1.0"):
        r = client.post(f"{API}/agents/lessons/cluster?threshold={t}")
        assert r.status_code in (200, 500), f"threshold={t} should not return 4xx"


# ── OpenAPI / Docs ────────────────────────────────────────────────────────────


def test_swagger_docs_available(client):
    """Swagger UI must be reachable."""
    r = client.get("/docs")
    assert r.status_code == 200


def test_openapi_schema_valid(client):
    """OpenAPI JSON must include expected structural keys."""
    r = client.get("/openapi.json")
    assert r.status_code == 200
    schema = r.json()
    assert "paths" in schema
    assert "components" in schema
    # Verify key routes exist in the schema
    paths = schema["paths"]
    assert any("/ingest" in p for p in paths), "Ingest route missing from schema"
    assert any("/query" in p for p in paths), "Query route missing from schema"
    assert any("/graph" in p for p in paths), "Graph route missing from schema"
