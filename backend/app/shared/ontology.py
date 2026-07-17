"""
shared/ontology.py
──────────────────
Single source of truth for the KITE knowledge graph ontology.
All node labels, relationship types, and property keys are defined here.

LOCKED: Do not add or modify without updating shared/schemas.py and
shared/api_models.py accordingly.
"""
from enum import Enum


# ──────────────────────────────────────────────────────────────
#  Node Labels
# ──────────────────────────────────────────────────────────────

class NodeLabel(str, Enum):
    """Canonical Neo4j node labels. Used in all Cypher queries and repositories."""
    EQUIPMENT   = "Equipment"
    FAILURE     = "Failure"
    PROCEDURE   = "Procedure"
    PERSON      = "Person"
    REGULATION  = "Regulation"
    INSPECTION  = "Inspection"
    WORK_ORDER  = "WorkOrder"
    INCIDENT    = "Incident"


# ──────────────────────────────────────────────────────────────
#  Relationship Types
# ──────────────────────────────────────────────────────────────

class RelType(str, Enum):
    """
    Canonical Neo4j relationship types.

    HAS_FAILURE          Equipment  ──► Failure
    RESOLVED_BY          Failure    ──► WorkOrder | Procedure
    PERFORMED_BY         WorkOrder  ──► Person
                         Inspection ──► Person
    GOVERNED_BY          Procedure  ──► Regulation
                         Equipment  ──► Regulation
    INSPECTED_ON         Equipment  ──► Inspection
    REFERENCES           Procedure  ──► Procedure | Regulation
    SIMILAR_FAILURE_MODE Failure    ──► Failure   (written by Lessons-Learned agent)
    """
    HAS_FAILURE          = "HAS_FAILURE"
    RESOLVED_BY          = "RESOLVED_BY"
    PERFORMED_BY         = "PERFORMED_BY"
    GOVERNED_BY          = "GOVERNED_BY"
    INSPECTED_ON         = "INSPECTED_ON"
    REFERENCES           = "REFERENCES"
    SIMILAR_FAILURE_MODE = "SIMILAR_FAILURE_MODE"


# ──────────────────────────────────────────────────────────────
#  Property Keys  (canonical property names on nodes/edges)
# ──────────────────────────────────────────────────────────────

class Prop(str, Enum):
    """Canonical Neo4j property keys. Use these constants in all Cypher strings."""
    # Equipment
    TAG_ID       = "tag_id"
    TYPE         = "type"
    LOCATION     = "location"
    CRITICALITY  = "criticality"
    ALIASES      = "aliases"

    # Failure
    FAILURE_ID   = "failure_id"
    DESCRIPTION  = "description"
    DATE         = "date"
    SEVERITY     = "severity"
    EQUIPMENT_TAG = "equipment_tag"

    # Procedure
    PROCEDURE_ID   = "procedure_id"
    TITLE          = "title"
    VERSION        = "version"
    GOVERNING_REG  = "governing_reg"

    # Person
    PERSON_ID      = "person_id"
    NAME           = "name"
    ROLE           = "role"
    CERTIFICATION  = "certification"

    # Regulation
    REG_ID         = "reg_id"
    SOURCE         = "source"
    CLAUSE         = "clause"

    # Inspection
    INSPECTION_ID  = "inspection_id"
    RESULT         = "result"
    INSPECTOR_REF  = "inspector_ref"

    # WorkOrder
    WO_ID          = "wo_id"
    STATUS         = "status"

    # Incident
    INCIDENT_ID    = "incident_id"

    # Common
    SOURCE_DOC_IDS = "source_doc_ids"   # list[str] — which docs contributed this node
    CREATED_AT     = "created_at"
    UPDATED_AT     = "updated_at"


# ──────────────────────────────────────────────────────────────
#  Severity Levels
# ──────────────────────────────────────────────────────────────

class Severity(str, Enum):
    LOW      = "Low"
    MEDIUM   = "Medium"
    HIGH     = "High"
    CRITICAL = "Critical"


# ──────────────────────────────────────────────────────────────
#  Criticality Levels  (Equipment only)
# ──────────────────────────────────────────────────────────────

class Criticality(str, Enum):
    LOW      = "Low"
    MEDIUM   = "Medium"
    HIGH     = "High"
    CRITICAL = "Critical"


# ──────────────────────────────────────────────────────────────
#  Document Types  (for ingestion pipeline)
# ──────────────────────────────────────────────────────────────

class DocType(str, Enum):
    MAINTENANCE_LOG    = "maintenance_log"
    SOP                = "sop"
    INSPECTION_REPORT  = "inspection_report"
    WORK_ORDER         = "work_order"
    INCIDENT           = "incident"
    PID                = "pid"            # P&ID stretch goal
    OTHER              = "other"


# ──────────────────────────────────────────────────────────────
#  Compliance Rule IDs
# ──────────────────────────────────────────────────────────────

class ComplianceRuleId(str, Enum):
    """IDs for the 5 scoped compliance rules."""
    INSPECTION_RECENCY      = "CR-001"   # Critical equipment inspected within 90 days
    LOTO_CERTIFICATION      = "CR-002"   # LOTO WOs must have certified performer
    CORRECTIVE_ACTION       = "CR-003"   # Flagged failures must link to corrective WO
    PROCEDURE_COVERAGE      = "CR-004"   # Regulated equipment must have linked procedure
    INCIDENT_CLOSURE        = "CR-005"   # Incidents closed within 30 days


# ──────────────────────────────────────────────────────────────
#  Agent Types
# ──────────────────────────────────────────────────────────────

class AgentType(str, Enum):
    RCA         = "rca"
    COMPLIANCE  = "compliance"
    LESSONS     = "lessons"
