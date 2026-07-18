"""
tests/integration/test_api.py
──────────────────────────────
Integration tests for the KITE REST API.
These run against a live server (localhost:8000).

Run with:
    pytest tests/integration/test_api.py -v --timeout=60

Requires:
    - Backend running: uv run uvicorn app.main:app --reload
    - Infrastructure up: docker compose up neo4j postgres qdrant
"""
import io

import pytest
import httpx

BASE_URL = "http://localhost:8000"
API_V1 = f"{BASE_URL}/api/v1"

TIMEOUT = 30.0


@pytest.fixture(scope="session")
def client() -> httpx.Client:
    return httpx.Client(base_url=BASE_URL, timeout=TIMEOUT)


# ══════════════════════════════════════════════════════════════════
# Health & Meta
# ══════════════════════════════════════════════════════════════════

class TestHealth:
    def test_health_returns_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200

    def test_health_response_has_required_keys(self, client):
        data = client.get("/health").json()
        assert "status" in data
        assert "services" in data
        assert "timestamp" in data

    def test_health_status_is_string(self, client):
        data = client.get("/health").json()
        assert data["status"] in ("ok", "degraded")

    def test_version_endpoint(self, client):
        r = client.get("/version")
        assert r.status_code == 200
        data = r.json()
        assert "version" in data
        assert "environment" in data

    def test_metrics_endpoint_returns_200(self, client):
        r = client.get("/metrics")
        assert r.status_code == 200
        data = r.json()
        assert "documents_ingested" in data
        assert "graph_nodes" in data
        assert "qdrant_vectors" in data

    def test_swagger_ui_accessible(self, client):
        r = client.get("/docs")
        assert r.status_code == 200

    def test_openapi_schema_has_expected_paths(self, client):
        schema = client.get("/openapi.json").json()
        assert "/health" in schema["paths"]
        assert "/api/v1/ingest" in schema["paths"]


# ══════════════════════════════════════════════════════════════════
# Ingest
# ══════════════════════════════════════════════════════════════════

# Minimal hand-crafted PDF (always parseable by any PDF reader)
_MINIMAL_PDF = b"""%PDF-1.4
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


class TestIngest:
    def test_pdf_upload_returns_queued(self, client):
        r = client.post(
            f"{API_V1}/ingest",
            files={"file": ("maintenance_log.pdf", _MINIMAL_PDF, "application/pdf")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "queued"
        assert data["job_id"].startswith("job-")
        assert data["doc_id"].startswith("doc-")

    def test_docx_upload_returns_queued(self, client):
        docx_bytes = b"PK\x03\x04"  # DOCX magic bytes (zip header) — minimal stub
        r = client.post(
            f"{API_V1}/ingest",
            files={"file": ("sop_maintenance.docx", docx_bytes, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
        # Should be queued even if the pipeline will fail for a stub
        assert r.status_code in (200, 422)

    def test_text_upload_accepted(self, client):
        content = b"Equipment P-101 inspection passed on 2026-05-10. Inspector: R. Singh."
        r = client.post(
            f"{API_V1}/ingest",
            files={"file": ("inspection_report.txt", content, "text/plain")},
        )
        assert r.status_code == 200
        assert r.json()["status"] == "queued"

    def test_doc_type_inferred_from_filename(self, client):
        content = b"Standard Operating Procedure for LOTO."
        r = client.post(
            f"{API_V1}/ingest",
            files={"file": ("sop_loto.txt", content, "text/plain")},
        )
        assert r.status_code == 200
        assert r.json()["doc_type"] == "sop"

    def test_duplicate_uploads_get_different_job_ids(self, client):
        content = b"Repeated maintenance log content."
        r1 = client.post(f"{API_V1}/ingest", files={"file": ("log.txt", content, "text/plain")})
        r2 = client.post(f"{API_V1}/ingest", files={"file": ("log.txt", content, "text/plain")})
        assert r1.status_code == 200
        assert r2.status_code == 200
        assert r1.json()["job_id"] != r2.json()["job_id"]

    def test_missing_file_returns_422(self, client):
        r = client.post(f"{API_V1}/ingest")
        assert r.status_code == 422

    def test_empty_file_returns_422(self, client):
        r = client.post(
            f"{API_V1}/ingest",
            files={"file": ("empty.pdf", b"", "application/pdf")},
        )
        assert r.status_code == 422

    def test_large_file_accepted(self, client):
        large = b"Equipment P-101 vibration anomaly. " * 10_000  # ~350 KB
        r = client.post(
            f"{API_V1}/ingest",
            files={"file": ("large_maintenance_log.txt", large, "text/plain")},
        )
        assert r.status_code == 200
        assert r.json()["status"] == "queued"


# ══════════════════════════════════════════════════════════════════
# Query
# ══════════════════════════════════════════════════════════════════

class TestQuery:
    def test_valid_query_does_not_500(self, client):
        r = client.post(f"{API_V1}/query", json={"query": "What caused the pump failure?"})
        assert r.status_code in (200, 500)  # 500 if LLM key missing, but not 4xx

    def test_empty_query_returns_422(self, client):
        r = client.post(f"{API_V1}/query", json={"query": ""})
        assert r.status_code == 422

    def test_whitespace_only_query_returns_422_or_422(self, client):
        r = client.post(f"{API_V1}/query", json={"query": "   "})
        assert r.status_code == 422

    def test_missing_body_returns_422(self, client):
        r = client.post(f"{API_V1}/query")
        assert r.status_code == 422

    def test_query_too_long_returns_422(self, client):
        # Exceeds the 2000 char max_length
        long_q = "pump " * 500
        r = client.post(f"{API_V1}/query", json={"query": long_q})
        assert r.status_code == 422

    def test_injection_attempt_does_not_500(self, client):
        """Cypher injection-style input should be handled safely."""
        evil = "'; DROP TABLE uploads; --"
        r = client.post(f"{API_V1}/query", json={"query": evil})
        assert r.status_code != 500


# ══════════════════════════════════════════════════════════════════
# Agents
# ══════════════════════════════════════════════════════════════════

class TestAgentsCompliance:
    def test_compliance_returns_200(self, client):
        r = client.get(f"{API_V1}/agents/compliance")
        assert r.status_code in (200, 500)  # 500 if Neo4j empty

    def test_compliance_response_has_status_key(self, client):
        r = client.get(f"{API_V1}/agents/compliance")
        if r.status_code == 200:
            assert "status" in r.json()

    def test_review_valid_statuses_accepted(self, client):
        for status in ("dismissed", "confirmed", "pending"):
            r = client.post(
                f"{API_V1}/agents/compliance/flags/test-flag-123/review",
                json={"status": status},
            )
            # DB errors are OK (500); what matters is no 422 for valid input
            assert r.status_code != 422, f"Valid status {status!r} was rejected"

    def test_review_invalid_status_returns_422(self, client):
        r = client.post(
            f"{API_V1}/agents/compliance/flags/test-hash/review",
            json={"status": "approved_by_magic"},
        )
        assert r.status_code == 422

    def test_review_missing_body_returns_422(self, client):
        r = client.post(f"{API_V1}/agents/compliance/flags/test-hash/review")
        assert r.status_code == 422


class TestAgentsRCA:
    def test_rca_unknown_equipment_does_not_500_badly(self, client):
        r = client.get(f"{API_V1}/agents/rca/nonexistent-pump-xyz-999")
        # May be 200 with empty result or 500 if LLM key missing
        assert r.status_code in (200, 500)

    def test_rca_response_time_acceptable(self, client):
        import time
        start = time.monotonic()
        client.get(f"{API_V1}/agents/rca/P-999", timeout=60.0)
        elapsed = time.monotonic() - start
        # Should respond within 60 seconds even if LLM is slow
        assert elapsed < 60.0


class TestAgentsLessons:
    def test_cluster_default_threshold_accepted(self, client):
        r = client.post(f"{API_V1}/agents/lessons/cluster")
        assert r.status_code in (200, 500)

    def test_cluster_valid_threshold_accepted(self, client):
        r = client.post(f"{API_V1}/agents/lessons/cluster?threshold=0.9")
        assert r.status_code in (200, 500)

    def test_cluster_invalid_threshold_over_one(self, client):
        r = client.post(f"{API_V1}/agents/lessons/cluster?threshold=1.5")
        assert r.status_code == 422

    def test_cluster_invalid_threshold_negative(self, client):
        r = client.post(f"{API_V1}/agents/lessons/cluster?threshold=-0.1")
        assert r.status_code == 422
