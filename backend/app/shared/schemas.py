"""
shared/schemas.py
─────────────────
Pydantic models for all 8 Knowledge Graph node types, extracted entity
results, and intermediate document schema.

These are the canonical data shapes used across all layers:
  - Extraction service outputs these models
  - Neo4j repository reads/writes these models
  - API responses reference these models (via api_models.py)

LOCKED: Do not add fields without updating ontology.py and neo4j_repo.py.
"""
import datetime

from pydantic import BaseModel, Field

from app.shared.ontology import Criticality, DocType, NodeLabel, RelType, Severity

# ──────────────────────────────────────────────────────────────
#  Intermediate Document Schema  (output of parser_service.py)
# ──────────────────────────────────────────────────────────────

class DocumentTable(BaseModel):
    """A structured table extracted from a document."""
    headers: list[str]
    rows: list[list[str]]
    caption: str | None = None


class ParsedDocument(BaseModel):
    """
    Intermediate representation of an ingested document.
    Output of parser_service.py, input to extraction_service.py.
    """
    doc_id: str
    doc_type: DocType
    source_filename: str
    raw_text: str
    tables: list[DocumentTable] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)
    parse_confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    parse_errors: list[str] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────
#  Graph Node Models
# ──────────────────────────────────────────────────────────────

class Equipment(BaseModel):
    """Equipment node. Primary identifier: tag_id."""
    tag_id: str
    type: str
    location: str | None = None
    criticality: Criticality | None = None
    aliases: list[str] = Field(default_factory=list)
    source_doc_ids: list[str] = Field(default_factory=list)


class Failure(BaseModel):
    """Failure event node. Primary identifier: failure_id."""
    failure_id: str
    description: str
    date: datetime.date | None = None
    severity: Severity | None = None
    equipment_tag: str                 # FK → Equipment.tag_id
    source_doc_ids: list[str] = Field(default_factory=list)


class Procedure(BaseModel):
    """Operating or maintenance procedure node. Primary identifier: procedure_id."""
    procedure_id: str
    title: str
    version: str | None = None
    governing_reg: str | None = None   # FK → Regulation.reg_id
    source_doc_ids: list[str] = Field(default_factory=list)


class Person(BaseModel):
    """Personnel node. Primary identifier: person_id."""
    person_id: str
    name: str
    role: str | None = None
    certification: str | None = None
    source_doc_ids: list[str] = Field(default_factory=list)


class Regulation(BaseModel):
    """Regulatory reference node. Primary identifier: reg_id."""
    reg_id: str
    source: str | None = None    # e.g. "OISD-105"
    clause: str | None = None    # e.g. "Clause 4.2"
    source_doc_ids: list[str] = Field(default_factory=list)


class Inspection(BaseModel):
    """Inspection record node. Primary identifier: inspection_id."""
    inspection_id: str
    date: datetime.date | None = None
    result: str | None = None
    inspector_ref: str | None = None   # FK → Person.person_id
    equipment_tag: str                     # FK → Equipment.tag_id
    source_doc_ids: list[str] = Field(default_factory=list)


class WorkOrder(BaseModel):
    """Work order node. Primary identifier: wo_id."""
    wo_id: str
    date: datetime.date | None = None
    description: str | None = None
    status: str | None = None
    source_doc_ids: list[str] = Field(default_factory=list)


class Incident(BaseModel):
    """Incident / near-miss record node. Primary identifier: incident_id."""
    incident_id: str
    date: datetime.date | None = None
    description: str | None = None
    severity: Severity | None = None
    source_doc_ids: list[str] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────
#  Relationship Schema
# ──────────────────────────────────────────────────────────────

class Relationship(BaseModel):
    """A directed relationship between two graph nodes."""
    from_id: str          # tag_id / failure_id / wo_id / etc.
    from_label: NodeLabel
    to_id: str
    to_label: NodeLabel
    rel_type: RelType
    properties: dict = Field(default_factory=dict)
    source_doc_ids: list[str] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────
#  Extraction Result  (output of extraction_service.py)
# ──────────────────────────────────────────────────────────────

class ExtractionResult(BaseModel):
    """
    Structured entities extracted from a single document via LLM.
    Input to resolution_service.py.
    """
    doc_id: str
    equipment: list[Equipment] = Field(default_factory=list)
    failures: list[Failure] = Field(default_factory=list)
    procedures: list[Procedure] = Field(default_factory=list)
    personnel: list[Person] = Field(default_factory=list)
    regulations: list[Regulation] = Field(default_factory=list)
    inspections: list[Inspection] = Field(default_factory=list)
    work_orders: list[WorkOrder] = Field(default_factory=list)
    incidents: list[Incident] = Field(default_factory=list)
    relationships: list[Relationship] = Field(default_factory=list)
    extraction_confidence: float = Field(ge=0.0, le=1.0, default=1.0)
    extraction_errors: list[str] = Field(default_factory=list)


# ──────────────────────────────────────────────────────────────
#  Vector Chunk  (stored in Qdrant)
# ──────────────────────────────────────────────────────────────

class DocumentChunk(BaseModel):
    """A text chunk with embedding metadata for Qdrant storage."""
    chunk_id: str
    doc_id: str
    doc_type: DocType
    source_filename: str
    text: str
    chunk_index: int
    graph_node_ids: list[str] = Field(default_factory=list)   # linked Neo4j node IDs
    embedding: list[float] | None = None
