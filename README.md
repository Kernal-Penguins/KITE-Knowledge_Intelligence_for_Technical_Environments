# KITE (Knowledge Intelligence for Technical Environments)

KITE is an autonomous Industrial GraphRAG system. It automatically ingests maintenance logs, Standard Operating Procedures (SOPs), and Piping & Instrumentation Diagrams (P&IDs) into a highly structured Neo4j Knowledge Graph and Qdrant Vector database, exposing an intelligent AI Copilot and autonomous compliance and RCA agents.

## Prerequisites
- Docker & Docker Compose (for databases)
- Python 3.11+
- Node.js 18+ (for frontend)
- `uv` (Fast python package manager)

## 1. Setup Infrastructure
Spin up the required databases (Neo4j, Qdrant, PostgreSQL) using Docker Compose:
```bash
docker-compose up -d
```
*Wait ~10 seconds for the databases to fully initialize.*

## 2. Setup Backend
```bash
cd backend
# Create virtual environment and install dependencies
uv venv
# On Windows: .\.venv\Scripts\activate
# On Mac/Linux: source .venv/bin/activate
uv pip install -r requirements.txt
```

### Environment Variables
Ensure you have your `GEMINI_API_KEY` set. You can create a `.env` file in the `backend` directory:
```env
GEMINI_API_KEY=your_key_here
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=kite_password
POSTGRES_URI=postgresql+asyncpg://postgres:kite_password@localhost:5432/kite
QDRANT_URL=http://localhost:6333
```

### Run Backend
```bash
cd backend
uvicorn app.main:app --reload
```
*The API will be available at http://localhost:8000.*

## 3. Setup Frontend
```bash
cd frontend
npm install
npm run dev
```
*The React UI will be available at http://localhost:5173.*

## Project Architecture
- **Backend**: FastAPI, LangChain, SentenceTransformers, BAAI Reranker, Google Gemini.
- **Frontend**: Vite, React, TailwindCSS, TanStack Query, Lucide Icons.
- **Databases**: Neo4j (Graph), Qdrant (Vector), PostgreSQL (Logs/State).

## Features
- **GraphRAG Copilot:** Ask natural language questions and receive cited answers grounded in both semantic text chunks and deterministic graph edges.
- **Root Cause Analysis (RCA) Agent:** Input an equipment ID to auto-generate an RCA report traversing its failure and incident history.
- **Lessons Learned Agent:** Auto-cluster historical failures using vector embeddings to create `SIMILAR_FAILURE_MODE` links in the graph.
- **Compliance Agent:** Deterministic 5-rule Cypher audit engine to flag safety violations (e.g. LOTO procedures performed without certification).

## Evaluation
To run the automated evaluation suite against the GraphRAG pipeline:
```bash
cd backend
python scripts/run_evaluation.py
```
