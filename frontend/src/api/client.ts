import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 60_000,
});

// ── Typed API wrappers ──────────────────────────────────────

export const api = {
  // Observability
  health: ()  => apiClient.get("/health"),
  version: () => apiClient.get("/version"),
  metrics: () => apiClient.get("/metrics"),

  // Ingestion (Day 2)
  ingest: (formData: FormData) =>
    apiClient.post("/api/v1/ingest", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }),
  ingestStatus: (jobId: string) =>
    apiClient.get(`/api/v1/ingest/${jobId}`),

  // Query / Copilot (Day 5)
  query: (payload: { query: string; max_results?: number; chat_id?: string }) =>
    apiClient.post("/api/v1/query", payload),

  // Agents (Day 6–7)
  rca: (equipmentId: string) =>
    apiClient.get(`/api/v1/agents/rca/${equipmentId}`),
  compliance: (equipmentId?: string) =>
    apiClient.get("/api/v1/agents/compliance", {
      params: equipmentId ? { equipment_id: equipmentId } : undefined,
    }),
  lessons: () =>
    apiClient.get("/api/v1/agents/lessons"),

  // Graph explorer (Day 5+)
  graphNodes: (limit = 100) =>
    apiClient.get("/api/v1/graph/nodes", { params: { limit } }),
  graphPaths: (fromId: string, toId: string) =>
    apiClient.get("/api/v1/graph/paths", { params: { from_id: fromId, to_id: toId } }),

  // Feedback
  feedback: (payload: { message_id: string; rating: number; comment?: string }) =>
    apiClient.post("/api/v1/feedback", payload),
};
