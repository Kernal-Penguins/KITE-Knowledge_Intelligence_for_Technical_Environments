import axios from "axios";

// In dev, vite.config.ts proxies /api and other backend paths to
// http://localhost:8000. In prod, nginx.conf should do the same
// (see location /api/ block). Health/version/metrics are NOT under
// /api -- they're mounted at the app root in main.py.
export const api = axios.create({
  baseURL: "/",
  timeout: 30_000,
});

// ── Route map (source of truth: main.py + route files you shared) ──────────
// GET  /health
// GET  /version
// GET  /metrics
// POST /api/v1/ingest                                  (multipart file upload)
// POST /api/v1/query                                   { query } -> { answer, confidence, citations }
// GET  /api/v1/agents/rca/{equipment_id}
// POST /api/v1/agents/lessons/cluster?threshold=0.85
// GET  /api/v1/agents/compliance
// GET  /api/v1/graph/nodes
// GET  /api/v1/uploads
// GET  /api/v1/review-queue
// POST /api/v1/agents/compliance/flags/{flag_hash}/review   { status }

export const ROUTES = {
  health: "/health",
  version: "/version",
  metrics: "/metrics",
  ingest: "/api/v1/ingest",
  uploads: "/api/v1/uploads",
  reviewQueue: "/api/v1/review-queue",
  query: "/api/v1/query",
  graphNodes: "/api/v1/graph/nodes",
  rca: (equipmentId: string) => `/api/v1/agents/rca/${encodeURIComponent(equipmentId)}`,
  lessonsCluster: "/api/v1/agents/lessons/cluster",
  compliance: "/api/v1/agents/compliance",
  complianceReview: (flagHash: string) =>
    `/api/v1/agents/compliance/flags/${encodeURIComponent(flagHash)}/review`,
};
