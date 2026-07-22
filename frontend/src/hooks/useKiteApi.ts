import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ROUTES } from "../lib/api";
import type {
  ComplianceAuditResponse,
  ComplianceReviewResponse,
  HealthResponse,
  IngestResponse,
  LessonsClusterResponse,
  MetricsResponse,
  QueryResponse,
  RcaResponse,
} from "../lib/types";

// ── Observability ────────────────────────────────────────────────────────

export function useHealth() {
  return useQuery({
    queryKey: ["health"],
    queryFn: async () => (await api.get<HealthResponse>(ROUTES.health)).data,
    refetchInterval: 30_000,
  });
}

export function useMetrics() {
  return useQuery({
    queryKey: ["metrics"],
    queryFn: async () => (await api.get<MetricsResponse>(ROUTES.metrics)).data,
    refetchInterval: 15_000,
  });
}

// ── Ingestion ────────────────────────────────────────────────────────────

export function useIngestDocument() {
  return useMutation({
    mutationFn: async (file: File) => {
      const form = new FormData();
      form.append("file", file);
      const res = await api.post<IngestResponse>(ROUTES.ingest, form, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      return res.data;
    },
  });
}

// ── Copilot / GraphRAG query ────────────────────────────────────────────

export function useCopilotQuery() {
  return useMutation({
    mutationFn: async (query: string) => {
      const res = await api.post<QueryResponse>(ROUTES.query, { query });
      return res.data;
    },
  });
}

// ── Agents: RCA ──────────────────────────────────────────────────────────

export function useRunRca() {
  return useMutation({
    mutationFn: async (equipmentId: string) => {
      const res = await api.get<RcaResponse>(ROUTES.rca(equipmentId));
      return res.data;
    },
  });
}

// ── Agents: Lessons-Learned clustering ──────────────────────────────────

export function useRunLessonsClustering() {
  return useMutation({
    mutationFn: async (threshold: number) => {
      const res = await api.post<LessonsClusterResponse>(`${ROUTES.lessonsCluster}?threshold=${threshold}`);
      return res.data;
    },
  });
}

// ── Agents: Compliance audit ─────────────────────────────────────────────

export function useComplianceAudit() {
  return useQuery({
    queryKey: ["compliance"],
    queryFn: async () => (await api.get<ComplianceAuditResponse>(ROUTES.compliance)).data,
  });
}

export function useReviewComplianceFlag() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ flagHash, status }: { flagHash: string; status: "dismissed" | "confirmed" | "pending" }) => {
      const res = await api.post<ComplianceReviewResponse>(ROUTES.complianceReview(flagHash), { status });
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["compliance"] });
    },
  });
}
