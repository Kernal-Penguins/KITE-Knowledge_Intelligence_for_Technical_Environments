"""
tests/unit/test_schemas.py
──────────────────────────
Unit tests for shared/schemas.py — validates Pydantic models
load correctly and enforce constraints without any DB/LLM connection.
"""
import datetime

import pytest
from pydantic import ValidationError

from app.shared.schemas import (
    DocumentChunk,
    DocumentTable,
    Equipment,
    ExtractionResult,
    Failure,
    Incident,
    Inspection,
    ParsedDocument,
    Person,
    Procedure,
    Regulation,
    Relationship,
    WorkOrder,
)
from app.shared.ontology import (
    Criticality,
    DocType,
    NodeLabel,
    RelType,
    Severity,
)


# ── Equipment ─────────────────────────────────────────────────────────────────

class TestEquipment:
    def test_minimal_valid(self):
        eq = Equipment(tag_id="P-101", type="Centrifugal Pump")
        assert eq.tag_id == "P-101"
        assert eq.aliases == []
        assert eq.criticality is None

    def test_full_valid(self):
        eq = Equipment(
            tag_id="V-205",
            type="Vessel",
            location="Unit 3",
            criticality=Criticality.HIGH,
            aliases=["Vessel 205", "V205"],
            source_doc_ids=["doc-abc"],
        )
        assert eq.criticality == Criticality.HIGH
        assert len(eq.aliases) == 2

    def test_missing_required_fields(self):
        with pytest.raises(ValidationError):
            Equipment(tag_id="P-101")  # type is required

    def test_invalid_criticality_rejected(self):
        with pytest.raises(ValidationError):
            Equipment(tag_id="P-101", type="Pump", criticality="SuperCritical")


# ── Failure ───────────────────────────────────────────────────────────────────

class TestFailure:
    def test_minimal_valid(self):
        f = Failure(
            failure_id="F-001",
            description="Bearing seizure",
            equipment_tag="P-101",
        )
        assert f.date is None
        assert f.severity is None

    def test_date_field_accepts_datetime_date(self):
        f = Failure(
            failure_id="F-002",
            description="Seal leak",
            equipment_tag="P-101",
            date=datetime.date(2026, 3, 11),
        )
        assert f.date.year == 2026

    def test_invalid_severity_rejected(self):
        with pytest.raises(ValidationError):
            Failure(
                failure_id="F-003",
                description="test",
                equipment_tag="P-101",
                severity="Catastrophic",
            )


# ── ParsedDocument ────────────────────────────────────────────────────────────

class TestParsedDocument:
    def test_parse_confidence_bounds(self):
        with pytest.raises(ValidationError):
            ParsedDocument(
                doc_id="d1",
                doc_type=DocType.MAINTENANCE_LOG,
                source_filename="test.pdf",
                raw_text="text",
                parse_confidence=1.5,  # > 1.0 — invalid
            )

    def test_valid_document(self):
        doc = ParsedDocument(
            doc_id="d1",
            doc_type=DocType.SOP,
            source_filename="sop.pdf",
            raw_text="LOTO procedure for P-101",
            parse_confidence=0.95,
        )
        assert doc.tables == []
        assert doc.parse_errors == []


# ── ExtractionResult ──────────────────────────────────────────────────────────

class TestExtractionResult:
    def test_empty_result(self):
        r = ExtractionResult(doc_id="d1")
        assert r.equipment == []
        assert r.failures == []
        assert r.extraction_confidence == 1.0

    def test_extraction_confidence_bounds(self):
        with pytest.raises(ValidationError):
            ExtractionResult(doc_id="d1", extraction_confidence=-0.1)

    def test_populated_result(self):
        r = ExtractionResult(
            doc_id="d1",
            equipment=[Equipment(tag_id="P-101", type="Pump")],
            failures=[
                Failure(failure_id="F-1", description="Vibration", equipment_tag="P-101")
            ],
        )
        assert len(r.equipment) == 1
        assert len(r.failures) == 1


# ── Relationship ──────────────────────────────────────────────────────────────

class TestRelationship:
    def test_valid_relationship(self):
        rel = Relationship(
            from_id="P-101",
            from_label=NodeLabel.EQUIPMENT,
            to_id="F-001",
            to_label=NodeLabel.FAILURE,
            rel_type=RelType.HAS_FAILURE,
        )
        assert rel.rel_type == RelType.HAS_FAILURE

    def test_invalid_rel_type_rejected(self):
        with pytest.raises(ValidationError):
            Relationship(
                from_id="P-101",
                from_label=NodeLabel.EQUIPMENT,
                to_id="F-001",
                to_label=NodeLabel.FAILURE,
                rel_type="MADE_UP_REL",
            )
