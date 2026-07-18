"""
tests/unit/test_ingest_helpers.py
──────────────────────────────────
Unit tests for helpers in the ingest route —
specifically the _infer_doc_type function and size guards.
"""
import pytest

from app.shared.ingest_utils import infer_doc_type, MAX_UPLOAD_BYTES
from app.shared.ontology import DocType


class TestInferDocType:
    def test_sop_keyword(self):
        assert infer_doc_type("sop_loto_v3.pdf") == DocType.SOP

    def test_procedure_keyword(self):
        assert infer_doc_type("pump_procedure.docx") == DocType.SOP

    def test_inspection_keyword(self):
        assert infer_doc_type("inspection_report_p101.pdf") == DocType.INSPECTION_REPORT

    def test_work_order_keyword(self):
        assert infer_doc_type("work_order_8841.csv") == DocType.WORK_ORDER

    def test_wo_dash_keyword(self):
        assert infer_doc_type("wo-8841.pdf") == DocType.WORK_ORDER

    def test_incident_keyword(self):
        assert infer_doc_type("incident_nm0092.pdf") == DocType.INCIDENT

    def test_near_miss_keyword(self):
        assert infer_doc_type("near_miss_june.pdf") == DocType.INCIDENT

    def test_pid_image_extension(self):
        assert infer_doc_type("plant_layout.png") == DocType.PID
        assert infer_doc_type("drawing.jpg") == DocType.PID
        assert infer_doc_type("diagram.jpeg") == DocType.PID

    def test_pid_keyword_in_name(self):
        assert infer_doc_type("pid_unit3.pdf") == DocType.PID

    def test_unknown_defaults_to_maintenance_log(self):
        assert infer_doc_type("random_doc.pdf") == DocType.MAINTENANCE_LOG
        assert infer_doc_type("unknown") == DocType.MAINTENANCE_LOG
        assert infer_doc_type("") == DocType.MAINTENANCE_LOG

    def test_case_insensitive(self):
        assert infer_doc_type("SOP_LOTO.PDF") == DocType.SOP
        assert infer_doc_type("INSPECTION_REPORT.DOCX") == DocType.INSPECTION_REPORT


class TestUploadConstants:
    def test_max_upload_bytes_is_sensible(self):
        """50 MB guard should be set correctly."""
        assert MAX_UPLOAD_BYTES == 50 * 1024 * 1024
