# KITE (Knowledge Intelligence for Technical Environments)

KITE is an autonomous Industrial GraphRAG system designed for enterprise asset intelligence and operational decision support. It automatically ingests maintenance logs, Standard Operating Procedures (SOPs), Work Orders, and Piping & Instrumentation Diagrams (P&IDs) into a structured Neo4j Knowledge Graph and Qdrant Vector database, exposing an intelligent AI Copilot and autonomous compliance and RCA agents.

---

## Technical Stack & Frameworks

- **Backend Framework**: FastAPI, Python 3.12/3.14, SQLAlchemy, Pydantic v2, Google GenAI SDK.
- **Frontend Framework**: Vite, React, TypeScript, TailwindCSS.
- **Databases**: Neo4j (Knowledge Graph), Qdrant (Vector Database), PostgreSQL (Relational Metadata & Audit Logs).
- **Embeddings & Reranking**: `sentence-transformers/all-MiniLM-L6-v2` and `cross-encoder/ms-marco-MiniLM-L-6-v2`.
- **Development & AI Assistance**: Built with **Antigravity** (Google DeepMind agentic AI environment) for rapid architectural design, container orchestration, and GraphRAG optimization.

---

## Core System Features

- **GraphRAG Copilot**: Natural language query engine combining semantic vector retrieval with deterministic multi-hop graph traversals to provide cited responses.
- **Root Cause Analysis (RCA) Agent**: Autonomous agent that traverses equipment failure chains to generate chronological RCA reports and root-cause hypotheses.
- **Lessons Learned Agent**: Vector embedding clustering engine that identifies similar failure modes and creates `SIMILAR_FAILURE_MODE` relationships across graph nodes.
- **Compliance Audit Agent**: Deterministic Cypher audit engine executing rule-based compliance checks (e.g., verifying LOTO procedures against certified personnel).
- **Entity Resolution Engine**: Hybrid fuzzy ratio and LLM adjudication pipeline that deduplicates equipment and failure tag aliases (e.g., `P-104` and `Pump 104`).

---

## System Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Node.js 20+
- `uv` (Fast Python package manager)

---

## Installation & Deployment

### 1. Database Infrastructure Setup
Spin up PostgreSQL, Neo4j, and Qdrant containers:
```bash
docker compose up -d
```

### 2. Backend Environment Setup
```bash
cd backend
uv venv
# Windows: .\.venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
uv pip install -r pyproject.toml
```

#### Environment Variables Configuration
Configure your `GEMINI_API_KEY` in `backend/.env` (or root `.env`):
```env
GEMINI_API_KEY=your_gemini_api_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=kite_password
POSTGRES_URI=postgresql+asyncpg://postgres:kite_password@localhost:5432/kite
QDRANT_URL=http://localhost:6333
```

#### Run Backend Server
```bash
cd backend
uv run uvicorn app.main:app --reload
```
The FastAPI backend service will run at `http://localhost:8000`.

### 3. Frontend Application Setup
```bash
cd frontend
npm install
npm run dev
```
The React frontend application will run at `http://localhost:5173`.

---

## Automated Benchmark Evaluation

To execute the automated evaluation suite against the GraphRAG pipeline and log scores to PostgreSQL:
```bash
cd backend
uv run python scripts/run_evaluation.py
```
