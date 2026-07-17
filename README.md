# KITE — Knowledge Integration & Tracing Engine

> **ET AI Hackathon 2.0** · AI for Industrial Knowledge Intelligence

KITE is a **GraphRAG platform** for industrial knowledge intelligence. It ingests heterogeneous industrial documents (maintenance logs, SOPs, inspection reports, work orders, incident records), extracts entities into a unified knowledge graph, and exposes that knowledge through a mobile-first conversational copilot and three specialised AI agents.

---

## Architecture

```
APPLICATION  →  Copilot UI · RCA · Compliance · Lessons
AGENT LAYER  →  RCA Agent · Compliance Agent · Lessons-Learned Agent
RETRIEVAL    →  Graph Traversal + Vector Search + Cross-Encoder Reranking
KNOWLEDGE    →  Neo4j (graph)  ·  Qdrant (vectors)
EXTRACTION   →  Gemini 2.5 Flash (entity extraction + resolution)
INGESTION    →  Docling (PDF · DOCX · CSV)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI · Python 3.14 · uvicorn |
| Knowledge Graph | Neo4j 5 Community |
| Vector Store | Qdrant |
| Embedding | BAAI/bge-large-en-v1.5 |
| Reranker | BAAI/bge-reranker-large |
| LLM | Gemini 2.5 Flash (extraction) · Gemini 2.5 Pro (generation) |
| Document Parsing | Docling (IBM, MIT-licensed) |
| Frontend | React 19 · TypeScript · Vite · Tailwind CSS · shadcn/ui |
| State Management | TanStack Query · React Router |
| Graph Visualisation | React Flow |
| Database | PostgreSQL 16 |
| Logging | structlog |

---

## Quick Start (Local)

### Prerequisites
- Docker Desktop (running)
- Node.js 24 LTS
- Python 3.14
- uv (`winget install astral-sh.uv`)

### 1. Clone and configure
```bash
git clone https://github.com/Kernal-Penguins/KITE-Knowledge_Intelligence_for_Technical_Environments.git
cd KITE
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Add documents
```
backend/data/documents/
├── maintenance_logs/   ← Add PDF/DOCX maintenance logs
├── sops/               ← Add PDF/DOCX SOPs
├── inspection_reports/ ← Add PDF/DOCX inspection reports
├── work_orders/        ← Add PDF/DOCX/CSV work orders
└── incidents/          ← Add PDF/DOCX incident records
```

### 3. Start all services
```bash
docker compose up -d
```

### 4. Install backend dependencies
```bash
cd backend
uv venv .venv --python 3.14
uv pip install -e .
```

### 5. Run backend (dev)
```bash
uvicorn app.main:app --reload --port 8000
```

### 6. Install and run frontend
```bash
cd frontend
npm install
npm run dev
```

### 7. Open the app
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474
- **Qdrant Dashboard**: http://localhost:6333/dashboard

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Service connectivity status |
| GET | `/version` | App version and build info |
| GET | `/metrics` | Live system counters |
| POST | `/api/v1/ingest` | Upload and ingest a document |
| GET | `/api/v1/ingest/{job_id}` | Ingestion pipeline status |
| POST | `/api/v1/query` | Copilot query (hybrid GraphRAG) |
| GET | `/api/v1/agents/rca/{equipment_id}` | RCA report for an equipment tag |
| GET | `/api/v1/agents/compliance` | Compliance gap scan |
| GET | `/api/v1/agents/lessons` | Lessons-learned pattern feed |
| GET | `/api/v1/graph/nodes` | Graph node explorer |
| GET | `/api/v1/graph/paths` | Graph path explorer |

---

## Knowledge Graph Ontology

**Node Types:** Equipment · Failure · Procedure · Person · Regulation · Inspection · WorkOrder · Incident

**Relationship Types:** HAS_FAILURE · RESOLVED_BY · PERFORMED_BY · GOVERNED_BY · INSPECTED_ON · REFERENCES · SIMILAR_FAILURE_MODE

---

## Git Workflow

```
main          ← production releases
  └── develop ← integration (all PRs merge here)
        └── feature/day{N}-{description}
```

---

## Deployment

| Service | Platform |
|---|---|
| Frontend | Vercel |
| Backend | Render |
| Neo4j | Neo4j Aura Free |
| Qdrant | Qdrant Cloud |

---

## Evaluation

Run the benchmark suite:
```bash
cd backend
python scripts/run_evaluation.py
```

Results are stored in PostgreSQL `evaluation_results` table.

---

## Scoping

| Capability | Status |
|---|---|
| Document ingestion (PDF/DOCX/CSV) | ✅ Full |
| Knowledge graph + entity resolution | ✅ Full |
| Hybrid retrieval copilot | ✅ Full |
| RCA agent | ✅ Full |
| Compliance agent | ✅ Scoped (5 rules) |
| Lessons-learned agent | ✅ Batch job |
| P&ID computer vision | 🔲 Stretch goal |
| Role-based access / audit logging | 📋 Roadmap |
