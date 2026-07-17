"""
shared/api_models.py
────────────────────
All FastAPI request and response models.
These are the contracts between the API layer and the frontend.

LOCKED: Every API endpoint must use these exact shapes.
Do not define inline request/response models in route files.
"""
from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from app.shared.ontology import ComplianceRuleId, DocType, Severity

# ──────────────────────────────────────────────────────────────
#  Common
# ──────────────────────────────────────────────────────────────

class HealthService(BaseModel):
    status: str     # "connected" | "degraded" | "unreachable"
    latency_ms: float | None = None


class HealthResponse(BaseModel):
    status: str     # "ok" | "degraded"
    services: dict[str, HealthService]
    timestamp: datetime


class VersionResponse(BaseModel):
    version: str
    build: str
    environment: str


class MetricsResponse(BaseModel):
    documents_ingested: int
    graph_nodes: int
    graph_edges: int
    qdrant_vectors: int
    queries_served: int
    avg_response_ms: float
    agent_invocations: dict[str, int]


# ──────────────────────────────────────────────────────────────
#  Ingest
# ──────────────────────────────────────────────────────────────

class IngestResponse(BaseModel):
    job_id: str
    doc_id: str
    filename: str
    doc_type: DocType
    status: str       # "queued" | "parsing" | "extracting" | "resolving" | "complete" | "failed"
    message: str | None = None


class IngestStatusResponse(BaseModel):
    job_id: str
    doc_id: str
    status: str
    pipeline_stage: str | None = None
    entities_extracted: int | None = None
    nodes_created: int | None = None
    chunks_embedded: int | None = None
    error: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


# ──────────────────────────────────────────────────────────────
#  Query  (Copilot)
# ──────────────────────────────────────────────────────────────

class QueryRequest(BaseModel):
    query: str = Field(min_length=1, max_length=2000)
    max_results: int = Field(default=5, ge=1, le=20)
    chat_id: str | None = None     # for session continuity


class Citation(BaseModel):
    """A single source citation (document level)."""
    doc_id: str
    filename: str
    doc_type: DocType
    page: int | None = None
    excerpt: str | None = None     # short relevant snippet


class GraphNode(BaseModel):
    """A node in the graph path used for answer generation."""
    node_id: str
    label: str
    properties: dict


class GraphEdge(BaseModel):
    """An edge in the graph path used for answer generation."""
    from_id: str
    to_id: str
    rel_type: str


class GraphPath(BaseModel):
    """A traversal path through the knowledge graph."""
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    description: str | None = None   # human-readable summary of the path


class QueryResponse(BaseModel):
    query: str
    answer: str
    confidence: float = Field(ge=0.0, le=1.0)
    citations: list[Citation] = Field(default_factory=list)
    graph_paths: list[GraphPath] = Field(default_factory=list)
    response_ms: float
    message_id: str


# ──────────────────────────────────────────────────────────────
#  RCA Agent
# ──────────────────────────────────────────────────────────────

class FailureRecord(BaseModel):
    failure_id: str
    description: str
    date: str | None = None
    severity: Severity | None = None
    resolved_by: list[str] | None = None   # WO or procedure IDs


class RootCause(BaseModel):
    description: str
    frequency: int
    last_occurrence: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)


class EvidenceLink(BaseModel):
    entity_id: str
    entity_type: str
    description: str
    source_doc: str | None = None


class RCAResponse(BaseModel):
    equipment_id: str
    equipment_type: str | None = None
    failure_count: int
    failure_history: list[FailureRecord]
    root_causes: list[RootCause]
    evidence_chain: list[EvidenceLink]
    recommended_action: str
    graph_path: GraphPath | None = None
    generated_at: datetime


# ──────────────────────────────────────────────────────────────
#  Compliance Agent
# ──────────────────────────────────────────────────────────────

class ComplianceGap(BaseModel):
    rule_id: ComplianceRuleId
    rule_description: str
    status: str                          # "FLAGGED" | "PASS"
    equipment_id: str | None = None
    record_id: str | None = None
    gap_description: str | None = None
    graph_evidence: GraphPath | None = None


class ComplianceResponse(BaseModel):
    total_checks: int
    flagged_count: int
    passed_count: int
    gaps: list[ComplianceGap]
    generated_at: datetime


# ──────────────────────────────────────────────────────────────
#  Lessons-Learned Agent
# ──────────────────────────────────────────────────────────────

class LessonsPattern(BaseModel):
    pattern_id: str
    description: str
    failure_ids: list[str]
    equipment_ids: list[str]
    equipment_count: int
    similarity_score: float = Field(ge=0.0, le=1.0)
    last_seen: str | None = None
    recommended_action: str | None = None


class LessonsResponse(BaseModel):
    pattern_count: int
    patterns: list[LessonsPattern]
    last_batch_run: datetime | None = None


# ──────────────────────────────────────────────────────────────
#  Graph Explorer  (for frontend GraphViewer)
# ──────────────────────────────────────────────────────────────

class GraphExplorerNode(BaseModel):
    id: str
    label: str
    properties: dict
    node_type: str


class GraphExplorerEdge(BaseModel):
    source: str
    target: str
    rel_type: str


class GraphExplorerResponse(BaseModel):
    nodes: list[GraphExplorerNode]
    edges: list[GraphExplorerEdge]
    total_nodes: int
    total_edges: int


# ──────────────────────────────────────────────────────────────
#  Feedback
# ──────────────────────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    message_id: str
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class FeedbackResponse(BaseModel):
    feedback_id: str
    message: str
