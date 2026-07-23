# KITE (Knowledge Intelligence for Technical Environments)

KITE is an AI-powered industrial knowledge platform that ingests maintenance logs, SOPs, work orders, and P&IDs into a Neo4j knowledge graph and Qdrant vector store, then exposes GraphRAG search, RCA, lessons-learned clustering, and compliance auditing through a React dashboard.

---

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────┐
│   React UI  │────▶│  FastAPI API │────▶│  Neo4j  │
│  (Vite/Nginx)│     │  + Agents    │     └─────────┘
└─────────────┘     │              │     ┌─────────┐
                    │              │────▶│ Qdrant  │
                    │              │     └─────────┘
                    │              │     ┌───────────┐
                    └──────────────┘────▶│ PostgreSQL│
                                         └───────────┘
```

**Agents:** Copilot (GraphRAG query), RCA, Lessons-Learned clustering, Compliance audit.

---

## Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Node.js 20+
- [uv](https://github.com/astral-sh/uv) (Python package manager)

---

## Quick Start (Docker)

1. Copy environment template and set your API key:

```bash
cp .env.example .env
# Edit .env — set GEMINI_API_KEY (required for LLM features)
```

2. Start the full stack:

```bash
docker compose up -d --build
```

3. Open the app:
   - **Frontend:** http://localhost:5173
   - **API docs:** http://localhost:8000/docs
   - **Neo4j browser:** http://localhost:7474

---

## Local Development

### Backend

```bash
cd backend
cp ../.env.example .env   # or use root .env
uv venv && uv pip install -r pyproject.toml
uv run uvicorn app.main:app --reload
```

API runs at http://localhost:8000.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI runs at http://localhost:5173. Vite proxies `/api`, `/health`, `/metrics`, and `/version` to the backend.

---

## Environment Variables

See [`.env.example`](.env.example) for the full list. Key variables:

| Variable | Description | Default |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (required for LLM) | — |
| `LLM_PROVIDER` | LLM backend: `gemini`, `openai`, `groq`, `ollama` | `gemini` |
| `NEO4J_URI` | Neo4j bolt URI | `bolt://localhost:7687` |
| `DATABASE_URL` | PostgreSQL async connection string | local docker default |
| `QDRANT_URL` | Qdrant HTTP endpoint | `http://localhost:6333` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` |
| `VITE_WORKSPACE_NAME` | Workspace label in UI | `My Workspace` |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Service connectivity status |
| GET | `/metrics` | System counters |
| POST | `/api/v1/ingest` | Upload a document |
| GET | `/api/v1/uploads` | List past uploads |
| GET | `/api/v1/review-queue` | Entity resolution review items |
| POST | `/api/v1/query` | GraphRAG search / Copilot |
| GET | `/api/v1/graph/nodes` | Graph explorer data |
| GET | `/api/v1/agents/rca/{id}` | Root cause analysis |
| POST | `/api/v1/agents/lessons/cluster` | Lessons-learned clustering |
| GET | `/api/v1/agents/compliance` | Compliance audit |

Legacy `/api/...` routes (without `/v1`) are also supported for backward compatibility.

---

## Demo Flow

1. **Ingest** — Upload sample docs from `Data_feed/synthetic_maintenance_docs/`.
2. **Overview** — Confirm graph nodes and vectors are increasing.
3. **Search / Copilot** — Ask questions like "What caused the pump failure on P-101?"
4. **Graph Explorer** — Visualize equipment, failures, and relationships.
5. **RCA** — Enter an equipment tag (e.g. `P-101`) for an AI-written report.
6. **Lessons-Learned** — Run clustering to link similar failure modes.
7. **Compliance** — Review audit results and confirm/dismiss gaps.
8. **Review Queue** — Confirm entity alias matches flagged during ingestion.

---

## Testing

```bash
cd backend
uv pip install -r pyproject.toml
pytest tests/ -v --timeout=60
```

---

## Deployment Notes

- The frontend Docker image uses nginx and proxies `/api`, `/health`, `/metrics`, and `/version` to the backend container.
- Set `CORS_ORIGINS` to include your production frontend URL.
- All database volumes (`neo4j_data`, `pg_data`, `qdrant_data`) persist across restarts.
- Services use `restart: unless-stopped` in docker-compose.

---

## Automated Benchmark Evaluation

```bash
cd backend
uv run python scripts/run_evaluation.py
```
