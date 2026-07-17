# KITE — Implementation Plan v3 (FINAL — APPROVED)
## Knowledge Integration & Tracing Engine
### ET AI Hackathon 2.0

> [!IMPORTANT]
> **Architectural Law:** Never introduce patterns, dependencies, folders, or libraries beyond those defined here. Every generated module must follow `shared/` API contracts, schemas, and ontology. If a dependency on another module exists, assume its interface — never reimplement it.

---

## Part 1 — Confirmed Decisions (No Further Questions on These)

| Decision | Confirmed Value |
|---|---|
| LLM | Provider abstraction — Gemini 2.5 Flash (routine) / Gemini 2.5 Pro (reasoning) as primary |
| Gemini API key | Placeholder in `.env` — user replaces before running |
| Vector store | **Qdrant** (local Docker for dev; Qdrant Cloud for prod) |
| Embedding model | **BAAI/bge-large-en-v1.5** |
| Reranker | **bge-reranker-large** |
| Frontend | React + TypeScript + Vite + Tailwind + **shadcn/ui** |
| shadcn/ui theme | **Toggle** — dark/light mode switcher, defaults to dark |
| State / data fetching | **TanStack Query** |
| Routing | **React Router** |
| Graph visualisation | **React Flow** |
| DOCX corpus | Real docs — placeholder folder structure; user adds actual files |
| Deployment — frontend | **Vercel** |
| Deployment — backend | **Render** |
| Deployment — Neo4j | **Local Docker (dev)** → **Neo4j Aura Free (prod)** |
| Deployment — Qdrant | **Local Docker (dev)** → **Qdrant Cloud (prod)** |
| Logging | **structlog** (structured, levelled logs throughout) |
| Observability | `/health`, `/metrics`, `/version` |
| Docker Compose | FastAPI + Neo4j + Qdrant + **PostgreSQL** + Frontend |
| Backend layers | API → Pipeline → Services → Repositories → Databases |
| DB migrations | **SQLAlchemy `create_all()`** — no Alembic for hackathon speed |
| Evaluation module | Standalone `evaluation/` with benchmark.py, metrics.py, ground_truth.json, benchmark_questions.json |
| PostgreSQL purpose | Users, Uploads, Chats, Eval Metrics, Agent Logs, Feedback, Sessions |
| Git workflow | `main` ← `develop` ← `feature/*` |
| Shared contract layer | `shared/` module: schemas.py, constants.py, ontology.py, api_models.py |
| P&ID stretch goal | Scaffold + placeholder on Day 8 — implement only if ahead of schedule |

---

## Part 2 — Full Project Structure

```
KITE/
│
├── .github/
│   └── workflows/
│       ├── ci.yml                        # Lint + test on PR to develop
│       └── deploy.yml                    # Deploy on merge to main
│
├── backend/
│   ├── app/
│   │   ├── main.py                       # FastAPI app factory, lifespan, router registration
│   │   ├── config.py                     # pydantic-settings: all env vars, typed
│   │   │
│   │   ├── shared/                       # ⭐ Single source of truth — imported everywhere
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py                # All Pydantic models for graph entities (8 node types)
│   │   │   ├── constants.py              # Enums, thresholds, timeouts, rule IDs
│   │   │   ├── ontology.py               # Node labels, relationship types, property keys
│   │   │   └── api_models.py             # Request/response shapes for every API endpoint
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py                   # FastAPI dependencies (DB sessions, LLM provider, etc.)
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── health.py             # GET /health, GET /version, GET /metrics
│   │   │       ├── ingest.py             # POST /ingest  — upload trigger
│   │   │       ├── query.py              # POST /query   — copilot retrieval
│   │   │       ├── graph.py              # GET /graph/nodes, /graph/paths
│   │   │       └── agents/
│   │   │           ├── __init__.py
│   │   │           ├── rca.py            # GET /agents/rca/{equipment_id}
│   │   │           ├── compliance.py     # GET /agents/compliance
│   │   │           └── lessons.py        # GET /agents/lessons
│   │   │
│   │   ├── pipeline/                     # ⭐ Orchestration only — no business logic here
│   │   │   ├── __init__.py
│   │   │   ├── ingestion_pipeline.py     # parse → extract → resolve → graph write → embed
│   │   │   ├── query_pipeline.py         # entity extract from query → hybrid retrieve → rerank → generate
│   │   │   └── agent_pipeline.py         # agent-specific graph traversal + generation flows
│   │   │
│   │   ├── services/                     # ⭐ Business logic — calls repositories, LLM, embedder
│   │   │   ├── __init__.py
│   │   │   ├── ingestion/
│   │   │   │   ├── parser_service.py     # Docling wrapper → intermediate doc schema
│   │   │   │   ├── extraction_service.py # LLM entity extraction (Appendix A prompt)
│   │   │   │   └── resolution_service.py # rapidfuzz Step1 + LLM Step2 + merge Step3
│   │   │   ├── retrieval/
│   │   │   │   ├── hybrid_service.py     # Graph traversal + vector search merge
│   │   │   │   ├── reranker_service.py   # bge-reranker-large cross-encoder
│   │   │   │   └── citation_service.py   # Dual citation assembly (doc page + graph path)
│   │   │   ├── generation/
│   │   │   │   └── generation_service.py # LLM answer generation with context + citations
│   │   │   └── agents/
│   │   │       ├── rca_service.py
│   │   │       ├── compliance_service.py
│   │   │       └── lessons_service.py
│   │   │
│   │   ├── repositories/                 # ⭐ Data access only — no business logic
│   │   │   ├── __init__.py
│   │   │   ├── neo4j_repo.py             # All Cypher queries (MERGE, MATCH, traversals)
│   │   │   ├── qdrant_repo.py            # All Qdrant collection ops (upsert, search)
│   │   │   └── postgres_repo.py          # All SQLAlchemy queries for PG tables
│   │   │
│   │   ├── providers/                    # ⭐ LLM provider abstraction
│   │   │   ├── __init__.py
│   │   │   ├── base.py                   # LLMProvider ABC: generate(), extract_entities(), adjudicate()
│   │   │   ├── gemini_provider.py        # GeminiProvider — Flash for routine, Pro for reasoning
│   │   │   ├── openai_provider.py        # OpenAIProvider
│   │   │   ├── groq_provider.py          # GroqProvider
│   │   │   └── ollama_provider.py        # OllamaProvider
│   │   │
│   │   ├── infrastructure/               # ⭐ Clients, connections, embedder — no logic
│   │   │   ├── __init__.py
│   │   │   ├── neo4j_client.py           # Async Neo4j driver, connection pool
│   │   │   ├── qdrant_client.py          # Qdrant async client
│   │   │   ├── postgres_client.py        # SQLAlchemy async engine + session factory
│   │   │   ├── embedder.py               # BAAI/bge-large-en-v1.5 wrapper
│   │   │   └── logger.py                 # structlog configuration + processors
│   │   │
│   │   └── db/
│   │       ├── __init__.py
│   │       ├── models.py                 # SQLAlchemy ORM models (all PG tables)
│   │       └── migrations/               # Alembic migrations
│   │           └── versions/
│   │
│   ├── evaluation/                       # ⭐ Standalone evaluation module
│   │   ├── __init__.py
│   │   ├── benchmark.py                  # Run benchmark questions against live system
│   │   ├── metrics.py                    # Compute all §12 metrics + store to PG
│   │   ├── ground_truth.json             # Known-correct entity/relationship facts
│   │   └── benchmark_questions.json      # 15–20 domain-expert benchmark questions
│   │
│   ├── data/
│   │   └── documents/                    # ⭐ PLACEHOLDER — add real industrial docs here
│   │       ├── README.md                 # Instructions: expected filename format, doc types
│   │       ├── maintenance_logs/         # Add .pdf or .docx files here
│   │       ├── sops/                     # Add .pdf or .docx files here
│   │       ├── inspection_reports/       # Add .pdf or .docx files here
│   │       ├── work_orders/              # Add .pdf, .docx, or .csv files here
│   │       ├── incidents/                # Add .pdf or .docx files here
│   │       └── pid_samples/              # Add P&ID image files here (stretch goal)
│   │
│   ├── scripts/
│   │   ├── seed_graph.py                 # Bulk-load graph from parsed corpus
│   │   └── run_evaluation.py             # CLI runner for evaluation/ module
│   │
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_parser_service.py
│   │   │   ├── test_extraction_service.py
│   │   │   ├── test_resolution_service.py
│   │   │   └── test_providers.py
│   │   ├── integration/
│   │   │   ├── test_ingestion_pipeline.py
│   │   │   ├── test_query_pipeline.py
│   │   │   └── test_agents.py
│   │   └── conftest.py
│   │
│   ├── pyproject.toml
│   ├── .env.example
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                       # shadcn/ui generated components live here
│   │   │   ├── chat/
│   │   │   │   ├── ChatThread.tsx        # Message list
│   │   │   │   ├── ChatInput.tsx         # Query input bar
│   │   │   │   ├── MessageBubble.tsx     # Single message with citation badges
│   │   │   │   ├── CitationBadge.tsx     # Doc citation (page, filename)
│   │   │   │   ├── GraphPathBadge.tsx    # Graph path inline snippet
│   │   │   │   └── ConfidenceBar.tsx     # Confidence score display
│   │   │   ├── upload/
│   │   │   │   ├── DropZone.tsx          # Drag-and-drop file upload
│   │   │   │   └── PipelineStatus.tsx    # Real-time ingestion status
│   │   │   ├── rca/
│   │   │   │   ├── RCAReport.tsx         # Full RCA structured report
│   │   │   │   ├── FailureTimeline.tsx   # Chronological failure history
│   │   │   │   └── RootCauseCard.tsx     # Single root cause with evidence
│   │   │   ├── compliance/
│   │   │   │   ├── ComplianceDashboard.tsx
│   │   │   │   ├── GapCard.tsx           # Single flagged gap
│   │   │   │   └── RuleStatusBadge.tsx
│   │   │   ├── lessons/
│   │   │   │   ├── LessonsFeed.tsx
│   │   │   │   └── PatternCard.tsx
│   │   │   └── graph/
│   │   │       └── GraphViewer.tsx       # React Flow graph path visualiser
│   │   │
│   │   ├── pages/
│   │   │   ├── CopilotPage.tsx
│   │   │   ├── RCAPage.tsx
│   │   │   ├── CompliancePage.tsx
│   │   │   ├── LessonsPage.tsx
│   │   │   └── AdminPage.tsx             # Upload + pipeline status + graph stats
│   │   │
│   │   ├── hooks/                        # TanStack Query hooks (one per API resource)
│   │   │   ├── useQuery.ts               # POST /query
│   │   │   ├── useRCA.ts                 # GET /agents/rca/{id}
│   │   │   ├── useCompliance.ts          # GET /agents/compliance
│   │   │   ├── useLessons.ts             # GET /agents/lessons
│   │   │   └── useUpload.ts              # POST /ingest (with progress)
│   │   │
│   │   ├── api/
│   │   │   └── client.ts                 # Axios instance, base URL, typed wrappers
│   │   │
│   │   ├── lib/
│   │   │   └── utils.ts                  # shadcn/ui utility (cn helper)
│   │   │
│   │   ├── router.tsx                    # React Router route definitions
│   │   ├── App.tsx
│   │   └── main.tsx
│   │
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── components.json                   # shadcn/ui config
│   └── Dockerfile
│
├── docker-compose.yml                    # All 5 services: FastAPI, Neo4j, Qdrant, Postgres, Frontend
├── docker-compose.prod.yml               # Prod overrides (env vars, no volumes)
├── .gitignore
├── .env.example
└── README.md
```

---

## Part 3 — Layer Responsibilities (API → Pipeline → Services → Repositories → Databases)

```
REQUEST
   │
   ▼
┌─────────────────────────────────┐
│  API LAYER  (api/routes/)       │  Validates input. Calls pipeline. Returns response.
│  Uses: shared/api_models.py     │  No business logic. No direct DB calls.
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  PIPELINE LAYER  (pipeline/)    │  Orchestrates the step sequence.
│  e.g. parse→extract→resolve     │  Calls services in order. Handles errors/retries.
│       →graph write→embed        │  No DB calls. No LLM calls directly.
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  SERVICE LAYER  (services/)     │  Business logic. Calls repositories + providers.
│  e.g. resolution_service.py     │  Uses shared/schemas.py and shared/ontology.py.
│       hybrid_service.py         │  Never crosses into another service directly.
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  REPOSITORY LAYER (repos/)      │  Raw data access only. No logic.
│  neo4j_repo / qdrant_repo       │  Returns typed objects from shared/schemas.py.
│  postgres_repo                  │  Never calls services or providers.
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  DATABASE LAYER                 │
│  Neo4j │ Qdrant │ PostgreSQL    │
└─────────────────────────────────┘
```

---

## Part 4 — LLM Provider Abstraction

### `providers/base.py` — Abstract Interface

```python
# Interface only — never instantiated directly
class LLMProvider(ABC):
    @abstractmethod
    async def extract_entities(self, text: str) -> dict: ...

    @abstractmethod
    async def adjudicate_entities(self, candidate_a: str, candidate_b: str, context: str) -> str: ...

    @abstractmethod
    async def generate_answer(self, query: str, context: list[str], citations: list) -> str: ...

    @abstractmethod
    async def generate_rca_report(self, equipment_id: str, failure_chain: list) -> str: ...
```

### Task → Model Routing (Gemini primary)

| Task | Model | Reason |
|---|---|---|
| Entity extraction per document | **Gemini 2.5 Flash** | High volume, structured JSON output, cost-sensitive |
| Entity resolution adjudication | **Gemini 2.5 Flash** | Binary decision, context window small |
| Compliance rule evaluation | **Gemini 2.5 Flash** | Rule checking, structured output |
| Hybrid retrieval answer generation | **Gemini 2.5 Pro** | Reasoning quality, citation assembly |
| RCA report generation | **Gemini 2.5 Pro** | Multi-hop reasoning, structured narrative |
| Lessons-Learned pattern clustering | **Gemini 2.5 Flash** | Batch job, cost-sensitive |

### `providers/gemini_provider.py`

```python
class GeminiProvider(LLMProvider):
    FLASH = "gemini-2.5-flash"
    PRO   = "gemini-2.5-pro"

    async def extract_entities(self, text: str) -> dict:
        # Uses FLASH + Appendix A prompt + JSON mode
        ...

    async def generate_answer(self, ...) -> str:
        # Uses PRO
        ...

    async def generate_rca_report(self, ...) -> str:
        # Uses PRO
        ...
```

---

## Part 5 — `shared/` Module (Single Source of Truth)

### `shared/ontology.py`
```python
# Node labels
class NodeLabel(str, Enum):
    EQUIPMENT   = "Equipment"
    FAILURE     = "Failure"
    PROCEDURE   = "Procedure"
    PERSON      = "Person"
    REGULATION  = "Regulation"
    INSPECTION  = "Inspection"
    WORK_ORDER  = "WorkOrder"
    INCIDENT    = "Incident"

# Relationship types
class RelType(str, Enum):
    HAS_FAILURE          = "HAS_FAILURE"
    RESOLVED_BY          = "RESOLVED_BY"
    PERFORMED_BY         = "PERFORMED_BY"
    GOVERNED_BY          = "GOVERNED_BY"
    INSPECTED_ON         = "INSPECTED_ON"
    REFERENCES           = "REFERENCES"
    SIMILAR_FAILURE_MODE = "SIMILAR_FAILURE_MODE"
```

### `shared/schemas.py`
```python
# All 8 node types as Pydantic models
class Equipment(BaseModel):
    tag_id: str; type: str; location: str
    criticality: str; aliases: list[str] = []

class Failure(BaseModel):
    failure_id: str; description: str; date: date
    severity: str; equipment_tag: str

# ... Procedure, Person, Regulation, Inspection, WorkOrder, Incident

# Extraction output
class ExtractionResult(BaseModel):
    equipment: list[Equipment]
    failures: list[Failure]
    procedures: list[Procedure]
    personnel: list[Person]
    regulations: list[Regulation]
    inspections: list[Inspection]
    work_orders: list[WorkOrder]
    incidents: list[Incident]
    relationships: list[Relationship]
```

### `shared/constants.py`
```python
INSPECTION_MAX_AGE_DAYS         = 90      # Compliance rule 1
INCIDENT_CLOSE_DEADLINE_DAYS    = 30      # Compliance rule 5
ENTITY_RESOLUTION_THRESHOLD     = 0.85   # rapidfuzz similarity threshold
MAX_GRAPH_TRAVERSAL_DEPTH       = 3
CHUNK_SIZE_TOKENS               = 500
CHUNK_OVERLAP_TOKENS            = 50
EMBEDDING_MODEL                 = "BAAI/bge-large-en-v1.5"
RERANKER_MODEL                  = "BAAI/bge-reranker-large"
```

### `shared/api_models.py`
```python
# All API request/response shapes

class IngestRequest(BaseModel):
    doc_type: DocType

class IngestResponse(BaseModel):
    job_id: str; status: str; doc_id: str

class QueryRequest(BaseModel):
    query: str; max_results: int = 5

class QueryResponse(BaseModel):
    answer: str
    confidence: float
    citations: list[Citation]        # {doc_id, page, filename}
    graph_paths: list[GraphPath]     # {nodes, edges used}

class RCAResponse(BaseModel):
    equipment_id: str
    failure_history: list[FailureRecord]
    root_causes: list[RootCause]
    evidence_chain: list[EvidenceLink]
    recommended_action: str

class ComplianceResponse(BaseModel):
    gaps: list[ComplianceGap]        # {rule_id, equipment_id, description, evidence, status}

class LessonsResponse(BaseModel):
    patterns: list[LessonsPattern]   # {failure_ids, description, equipment_count, last_seen}
```

---

## Part 6 — PostgreSQL Schema

### Tables

| Table | Purpose | Key Columns |
|---|---|---|
| `users` | User accounts (roadmap — seeded for demo) | id, email, role, created_at |
| `sessions` | Active user sessions | id, user_id, token, expires_at |
| `uploads` | Document upload tracking | id, filename, doc_type, status, pipeline_stage, created_at |
| `chats` | Chat session history | id, user_id, created_at |
| `chat_messages` | Individual messages | id, chat_id, role (user/assistant), content, confidence, citations_json |
| `agent_logs` | All agent invocations | id, agent_type, input, output_json, duration_ms, created_at |
| `evaluation_runs` | Benchmark run records | id, run_at, question_count, model_used |
| `evaluation_results` | Per-question results | id, run_id, question_id, answer, correct, metrics_json |
| `feedback` | User thumbs up/down on answers | id, message_id, user_id, rating, comment, created_at |

> **PostgreSQL is the system of record for everything transactional. Neo4j is for graph traversal. Qdrant is for vector similarity. They are never used interchangeably.**

---

## Part 7 — Docker Compose (All 5 Services)

```yaml
services:

  backend:
    build: ./backend
    ports: ["8000:8000"]
    env_file: .env
    depends_on: [neo4j, qdrant, postgres]
    volumes:
      - ./backend/data/documents:/app/data/documents

  frontend:
    build: ./frontend
    ports: ["5173:5173"]
    depends_on: [backend]

  neo4j:
    image: neo4j:5-community
    ports: ["7474:7474", "7687:7687"]
    environment:
      NEO4J_AUTH: neo4j/kite_password
    volumes:
      - neo4j_data:/data

  qdrant:
    image: qdrant/qdrant:latest
    ports: ["6333:6333", "6334:6334"]
    volumes:
      - qdrant_data:/qdrant/storage

  postgres:
    image: postgres:16-alpine
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: kite
      POSTGRES_USER: kite
      POSTGRES_PASSWORD: kite_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  neo4j_data:
  qdrant_data:
  postgres_data:
```

---

## Part 8 — Observability Endpoints

### `GET /health`
```json
{
  "status": "ok",
  "services": {
    "neo4j": "connected",
    "qdrant": "connected",
    "postgres": "connected"
  },
  "timestamp": "2026-07-17T06:00:00Z"
}
```

### `GET /version`
```json
{
  "version": "0.1.0",
  "build": "git-sha",
  "environment": "development"
}
```

### `GET /metrics`
```json
{
  "documents_ingested": 47,
  "graph_nodes": 312,
  "graph_edges": 891,
  "qdrant_vectors": 2341,
  "queries_served": 142,
  "avg_response_ms": 1840,
  "agent_invocations": { "rca": 23, "compliance": 11, "lessons": 4 }
}
```

---

## Part 9 — Logging (structlog)

```python
# infrastructure/logger.py
import structlog

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.PrintLoggerFactory(),
)

log = structlog.get_logger()
```

Every service/pipeline logs:
```python
log.info("entity_extraction.started", doc_id=doc_id, doc_type=doc_type)
log.info("entity_extraction.complete", doc_id=doc_id, entity_count=len(result.equipment))
log.error("ingestion.failed", doc_id=doc_id, stage="parse", error=str(e))
```

---

## Part 10 — Evaluation Module

```
evaluation/
├── benchmark.py            # Calls live API, records answers
├── metrics.py              # Computes all §12 metrics
├── ground_truth.json       # Known entity/relationship facts per doc
└── benchmark_questions.json
```

### `benchmark_questions.json` (structure)
```json
[
  {
    "id": "BQ-001",
    "question": "What is the most recent failure recorded for equipment P-104?",
    "expected_entities": ["P-104"],
    "requires_graph_traversal": true,
    "doc_types_required": ["maintenance_log", "work_order"]
  },
  ...
]
```

### Metrics Computed (all §12 metrics)
```python
class EvaluationMetrics(BaseModel):
    entity_extraction_accuracy: float   # Manual spot-check %
    query_answer_quality: float         # Human score 1-5 avg
    graph_linkage_completeness: float   # % expected paths found
    time_to_answer_ms: float            # vs keyword search baseline
    compliance_gap_accuracy: float      # seeded gap detection %
    source_citation_rate: float         # % answers with valid doc cite
    graph_path_accuracy: float          # % cited paths valid
    evidence_completeness: float        # % answers with full evidence
    unsupported_claim_rate: float       # % claims with no source
    provenance_coverage: float          # % facts traceable to source
    confidence_calibration: float       # correlation(stated, actual)
```

---

## Part 11 — Document Placeholders

```
backend/data/documents/
├── README.md                    ← Describes expected file format
├── maintenance_logs/
│   └── .gitkeep                 ← ADD real .pdf/.docx maintenance logs here
├── sops/
│   └── .gitkeep                 ← ADD real .pdf/.docx SOPs here
├── inspection_reports/
│   └── .gitkeep                 ← ADD real .pdf/.docx inspection reports here
├── work_orders/
│   └── .gitkeep                 ← ADD real .pdf/.docx/.csv work orders here
├── incidents/
│   └── .gitkeep                 ← ADD real .pdf/.docx incident records here
└── pid_samples/
    └── .gitkeep                 ← ADD real P&ID image files here (stretch goal)
```

> [!NOTE]
> The ingestion pipeline auto-detects `doc_type` from the subdirectory name. File naming convention: `{equipment_tag}_{doc_type}_{YYYYMMDD}.{ext}`. Docs may reference equipment across folders — the entity resolution pass handles cross-document merging.

---

## Part 12 — Git Workflow

```
main          ← production-ready only; protected branch; deploy on merge
  └── develop ← integration branch; all feature PRs target here
        ├── feature/day1-scaffold
        ├── feature/day2-ingestion-pipeline
        ├── feature/day3-entity-extraction
        ├── feature/day4-entity-resolution
        ├── feature/day5-vector-hybrid-retrieval
        ├── feature/day6-rca-lessons-agents
        ├── feature/day7-compliance-agent
        ├── feature/day8-pid-stretch
        ├── feature/day9-frontend-ui
        └── feature/day10-eval-polish
```

**Rules:**
- Never commit directly to `main` or `develop`
- PRs to `develop` require passing CI (lint + unit tests)
- Merge `develop` → `main` only at end-of-day milestones
- All feature branches follow `feature/{day}-{short-description}` naming

---

## Part 13 — Deployment Architecture

```
                        ┌────────────────┐
                        │   Vercel       │
                        │   Frontend     │
                        │   (React)      │
                        └───────┬────────┘
                                │ HTTPS API calls
                        ┌───────▼────────┐
                        │   Render       │
                        │   Backend      │
                        │   (FastAPI)    │
                        └──┬──┬────┬─────┘
                           │  │    │
            ┌──────────────┘  │    └──────────────────┐
            │                 │                       │
   ┌────────▼──────┐  ┌───────▼──────┐  ┌────────────▼────────┐
   │ Neo4j Aura    │  │ Qdrant Cloud │  │ Render PostgreSQL   │
   │ (Free tier)   │  │              │  │  or managed PG      │
   └───────────────┘  └──────────────┘  └─────────────────────┘
```

**Prod env vars (never committed — set in Render dashboard):**
```
GEMINI_API_KEY=...
NEO4J_URI=neo4j+s://xxxx.databases.neo4j.io
NEO4J_PASSWORD=...
QDRANT_URL=https://xxxx.qdrant.io
QDRANT_API_KEY=...
DATABASE_URL=postgresql+asyncpg://...
```

---

## Part 14 — Revised 10-Day Build Plan

### Day 1 — Scaffold + Git + Docker + Shared Contracts
**Tasks:**
- `git init`, `develop` branch, Day 1 feature branch
- Create full project directory skeleton (all folders, `__init__.py`, `.gitkeep`)
- Write `shared/ontology.py`, `shared/constants.py` (complete — never changes after this)
- Write `shared/schemas.py` (all 8 Pydantic node models — lock these)
- Write `shared/api_models.py` (all request/response shapes — lock these)
- Write `docker-compose.yml` (all 5 services)
- Write `backend/app/main.py` (app factory + lifespan + `/health` + `/version`)
- Write `infrastructure/logger.py` (structlog setup)
- `docker compose up -d` — verify all services healthy
- Scaffold frontend: Vite + React + TS + Tailwind + shadcn/ui init + React Router + TanStack Query

**Exit criterion:** `GET /health` returns all services connected; frontend dev server runs; `shared/` module is importable; Docker Compose all green.

---

### Day 2 — Ingestion Pipeline
**Tasks:**
- `infrastructure/embedder.py` — BAAI/bge-large-en-v1.5 wrapper
- `repositories/qdrant_repo.py` — collection creation, upsert, search
- `repositories/postgres_repo.py` — uploads table CRUD
- `services/ingestion/parser_service.py` — Docling PDF/DOCX/CSV → intermediate schema
- `pipeline/ingestion_pipeline.py` — parse → (extract next) — wire parse step only
- `api/routes/ingest.py` — `POST /ingest`
- `GET /metrics` stub (return live counts from PG + Neo4j + Qdrant)
- Retry queue + graceful degradation with structlog error logging

**Exit criterion:** `POST /ingest` with a PDF returns `{job_id, status: "parsing_complete"}` and logs structured events; `/metrics` returns real counts.

---

### Day 3 — Entity Extraction
**Tasks:**
- `providers/base.py` — LLMProvider ABC
- `providers/gemini_provider.py` — Flash for extraction, Pro for generation
- `providers/openai_provider.py`, `groq_provider.py`, `ollama_provider.py` (stubs conforming to ABC)
- `services/ingestion/extraction_service.py` — Appendix A prompt → JSON → `ExtractionResult`
- Wire extraction into `pipeline/ingestion_pipeline.py`
- Write extracted entities to PG `uploads` table with pipeline stage tracking

**Exit criterion:** A real doc (or placeholder text) flows through parse → extract and returns a valid `ExtractionResult` JSON conforming to `shared/schemas.py`.

---

### Day 4 — Entity Resolution + Graph Write
**Tasks:**
- `services/ingestion/resolution_service.py` — rapidfuzz Step 1 + Gemini Flash Step 2 + merge Step 3
- `repositories/neo4j_repo.py` — `MERGE` on all 8 node types + all 7 relationship types
- Wire resolution → graph write into `pipeline/ingestion_pipeline.py`
- Sanity Cypher: verify 3+ multi-hop chains exist; verify aliases stored on merged nodes

**Exit criterion:** Graph shows ≥3 multi-hop chains traceable to source docs; duplicate entity variants provably merged.

---

### Day 5 — Vector Layer + Hybrid Retrieval
**Tasks:**
- Chunker (500 tokens, 50 overlap) with `graph_node_ids` payload in Qdrant
- `repositories/qdrant_repo.py` — upsert chunks, vector search
- `services/retrieval/hybrid_service.py` — graph traversal + vector search → merge + deduplicate
- `services/retrieval/reranker_service.py` — bge-reranker-large cross-encoder
- `services/retrieval/citation_service.py` — dual citation (doc page + graph path)
- `services/generation/generation_service.py` — Gemini Pro answer with citations
- `pipeline/query_pipeline.py` — full chain
- `api/routes/query.py` — `POST /query`
- PG: log query + answer to `chat_messages`

**Exit criterion:** `POST /query` returns `{answer, confidence, citations[doc+graph], graph_paths}` with both a cited source doc and a cited graph path.

---

### Day 6 — RCA + Lessons-Learned Agents
**Tasks:**
- `services/agents/rca_service.py` — graph traversal → Gemini Pro report
- `services/agents/lessons_service.py` — batch clustering → `SIMILAR_FAILURE_MODE` edges → cached
- `pipeline/agent_pipeline.py` — agent orchestration
- `api/routes/agents/rca.py`, `lessons.py`
- PG: log all agent invocations to `agent_logs`

**Exit criterion:** `GET /agents/rca/{equipment_id}` returns a valid `RCAResponse` with evidence chain for ≥2 equipment IDs.

---

### Day 7 — Compliance Agent
**Tasks:**
- `services/agents/compliance_service.py` — 5 Cypher-based rule checks
- `api/routes/agents/compliance.py`
- Rules:
  1. Critical equipment `INSPECTED_ON` within 90 days
  2. `WorkOrder` with LOTO procedure `PERFORMED_BY` certified Person
  3. `Failure` flagged → `RESOLVED_BY` a corrective `WorkOrder`
  4. Equipment `GOVERNED_BY` regulation → at least one linked `Procedure`
  5. `Incident` closed within 30 days
- PG: log compliance runs to `agent_logs`

**Exit criterion:** Compliance agent correctly flags seeded gap + passes seeded compliant case.

---

### Day 8 — P&ID Stretch Goal (Hard Time-Box: morning only)
- Run YOLOv8 pretrained on P&ID samples in `data/documents/pid_samples/`
- Detected tags → `Equipment` nodes in Neo4j
- Hard cutoff if not clean by noon → redirect to polish

---

### Day 9 — Frontend UI + Evaluation
**Frontend:**
- All pages (Copilot, RCA, Compliance, Lessons, Admin)
- All components (ChatThread, DropZone, RCAReport, ComplianceDashboard, LessonsFeed, GraphViewer)
- All TanStack Query hooks
- Mobile-responsive (375px min)
- React Flow `GraphViewer` for inline graph path display

**Evaluation:**
- `evaluation/benchmark.py` — run all 15–20 benchmark questions against live `/query`
- `evaluation/metrics.py` — compute all 11 metrics, store to PG `evaluation_results`
- Run `scripts/run_evaluation.py`, record numbers

**Exit criterion:** All pages render on 375px; evaluation numbers exist in PG.

---

### Day 10 — Polish, Documentation, Demo
- Architecture diagram (matching exactly what was built)
- README with local dev + Docker Compose run instructions
- Record demo video: upload → graph update → RCA query end-to-end
- Rehearse live query flow 3–4 times
- Honest scoping table in deck
- Final `develop` → `main` merge

---

## Part 15 — All Decisions Locked ✅

> [!NOTE]
> All open questions have been answered. No further approvals needed. Ready to build.

| Question | Answer |
|---|---|
| Gemini API key | Placeholder in `.env` — will be replaced before running |
| Neo4j for dev | Local Docker container in `docker-compose.yml` |
| Neo4j for prod | Neo4j Aura Free (connection string swapped via env var) |
| P&ID stretch goal | Scaffold folder + stub service on Day 8 — implement only if ahead of schedule |
| shadcn/ui theme | Toggle (dark default, light available) |
| DB migrations | SQLAlchemy `create_all()` on startup — no Alembic |

---

## Part 16 — `.env.example` (Complete)

```env
# ── LLM ──────────────────────────────────────────────
GEMINI_API_KEY=your-gemini-api-key-here
LLM_PROVIDER=gemini                         # gemini | openai | groq | ollama
OPENAI_API_KEY=
GROQ_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434

# ── Neo4j ────────────────────────────────────────────
# Dev: local Docker
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=kite_password
# Prod (Aura Free): swap to neo4j+s://xxxx.databases.neo4j.io

# ── Qdrant ───────────────────────────────────────────
# Dev: local Docker
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=
# Prod (Qdrant Cloud): set URL + API key

# ── PostgreSQL ───────────────────────────────────────
DATABASE_URL=postgresql+asyncpg://kite:kite_password@localhost:5432/kite

# ── App ──────────────────────────────────────────────
APP_ENV=development                         # development | production
APP_VERSION=0.1.0
CORS_ORIGINS=http://localhost:5173

# ── Embedding / Reranker ─────────────────────────────
EMBEDDING_MODEL=BAAI/bge-large-en-v1.5
RERANKER_MODEL=BAAI/bge-reranker-large
```

---

## Part 17 — `pyproject.toml` (Backend Dependencies)

```toml
[project]
name = "kite-backend"
version = "0.1.0"
requires-python = ">=3.14"

dependencies = [
    # API
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "python-multipart>=0.0.18",
    "aiofiles>=24.0",

    # Config + validation
    "pydantic>=2.10",
    "pydantic-settings>=2.7",
    "python-dotenv>=1.0",

    # Database drivers
    "neo4j>=5.27",
    "qdrant-client>=1.14",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.30",

    # LLM providers
    "google-genai>=1.0",           # Gemini 2.5 Flash + Pro
    "openai>=1.58",
    "groq>=0.13",

    # Ingestion
    "docling>=2.0",

    # Embeddings + reranking
    "sentence-transformers>=3.3",
    "FlagEmbedding>=1.3",          # bge-reranker-large

    # Entity resolution
    "rapidfuzz>=3.11",

    # Batch scheduling
    "apscheduler>=3.10",

    # Logging
    "structlog>=24.4",

    # HTTP client
    "httpx>=0.28",
]

[dependency-groups]
dev = [
    "pytest>=8.3",
    "pytest-asyncio>=0.25",
    "httpx>=0.28",
    "ruff>=0.9",
]
```

---

## Part 18 — `package.json` (Frontend Dependencies)

```json
{
  "name": "kite-frontend",
  "version": "0.1.0",
  "type": "module",
  "dependencies": {
    "react": "^19",
    "react-dom": "^19",
    "react-router-dom": "^7",
    "@tanstack/react-query": "^5",
    "reactflow": "^11",
    "axios": "^1.7",
    "lucide-react": "^0.475",
    "class-variance-authority": "^0.7",
    "clsx": "^2.1",
    "tailwind-merge": "^2.6"
  },
  "devDependencies": {
    "@types/react": "^19",
    "@types/react-dom": "^19",
    "@vitejs/plugin-react": "^4",
    "typescript": "^5.7",
    "vite": "^6",
    "tailwindcss": "^4",
    "@tailwindcss/vite": "^4"
  }
}
```

---

## Part 19 — Ontology Governance

To ensure the knowledge graph's schema evolves systematically without drift, the following governance rules apply:
- **Versioning**: The ontology (`shared/ontology.py` and `shared/schemas.py`) acts as the single source of truth. Any change to node types, relationship types, or properties must be treated as a breaking API change and versioned accordingly (e.g. `v2`).
- **Review Process**: Before a new node or edge type is added, the change must be reviewed by both a Domain Expert (to confirm industrial validity) and a Data Engineer (to confirm Neo4j performance implications).
- **Migration Strategy**: Introducing a new edge type requires a retroactive batch job (`scripts/ontology_migration.py`) to infer the new edges across existing data, ensuring historical documents are not orphaned under the old schema.

