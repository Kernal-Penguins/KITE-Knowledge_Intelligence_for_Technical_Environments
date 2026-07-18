"""
app/shared/ingest_utils.py
──────────────────────────
Lightweight helpers for the ingestion route that can be imported
in unit tests without triggering heavy ML library loading.
"""
from app.shared.ontology import DocType

# 50 MB hard cap — prevents runaway memory use during upload buffering
MAX_UPLOAD_BYTES = 50 * 1024 * 1024


def infer_doc_type(filename: str) -> DocType:
    """Infer DocType from filename keywords / extension."""
    name = filename.lower()
    if "sop" in name or "procedure" in name:
        return DocType.SOP
    if "inspection" in name:
        return DocType.INSPECTION_REPORT
    if "work_order" in name or "workorder" in name or "wo-" in name:
        return DocType.WORK_ORDER
    if "incident" in name or "near_miss" in name or "nearmiss" in name:
        return DocType.INCIDENT
    if name.endswith((".png", ".jpg", ".jpeg")) or "pid" in name:
        return DocType.PID
    return DocType.MAINTENANCE_LOG
