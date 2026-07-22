import { Loader2, AlertTriangle } from "lucide-react";
import { useMetrics, useHealth } from "../hooks/useKiteApi";

const serviceLabels: Record<string, string> = {
  neo4j: "Neo4j",
  qdrant: "Qdrant",
  postgres: "PostgreSQL",
};

export default function OverviewPage() {
  const { data: metrics, isLoading: metricsLoading, isError: metricsError } = useMetrics();
  const { data: health } = useHealth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-medium text-white">Overview</h1>
        <p className="text-sm text-white/45">Live from your KITE backend -- GET /metrics &amp; GET /health.</p>
      </div>

      {health && (
        <div className="flex flex-wrap items-center gap-2">
          <span
            className={`rounded-full px-2.5 py-1 text-[11px] font-medium ${
              health.status === "ok" ? "bg-[#28c840]/15 text-[#28c840]" : "bg-[#febc2e]/15 text-[#febc2e]"
            }`}
          >
            {health.status === "ok" ? "All systems connected" : "Degraded"}
          </span>
          {Object.entries(health.services).map(([key, svc]) => (
            <span
              key={key}
              className="flex items-center gap-1.5 rounded-full bg-white/[0.05] px-2.5 py-1 text-[11px] text-white/60"
            >
              <span
                className="h-1.5 w-1.5 rounded-full"
                style={{ backgroundColor: svc.status === "connected" ? "#28c840" : "#E08A3C" }}
              />
              {serviceLabels[key] ?? key}
            </span>
          ))}
        </div>
      )}

      {metricsLoading && (
        <div className="flex items-center gap-2 text-sm text-white/40">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading metrics...
        </div>
      )}

      {metricsError && (
        <div className="flex items-center gap-2 rounded-lg bg-[#E08A3C]/10 px-4 py-3 text-sm text-[#E08A3C] ring-1 ring-[#E08A3C]/20">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          Couldn't reach the backend at /metrics. Make sure it's running and the Vite proxy / nginx rule points at it.
        </div>
      )}

      {metrics && (
        <>
          <div className="grid grid-cols-2 divide-x divide-white/5 rounded-xl bg-white/[0.03] ring-1 ring-white/5 sm:grid-cols-4">
            <Stat label="DOCUMENTS INGESTED" value={metrics.documents_ingested} sub="Complete uploads" />
            <Stat label="GRAPH NODES" value={metrics.graph_nodes} sub="Neo4j entities" />
            <Stat label="GRAPH EDGES" value={metrics.graph_edges} sub="Relationships traced" />
            <Stat label="VECTORS" value={metrics.qdrant_vectors} sub="Qdrant embeddings" />
          </div>

          <div className="grid grid-cols-2 divide-x divide-white/5 rounded-xl bg-white/[0.03] ring-1 ring-white/5 sm:grid-cols-3">
            <Stat label="QUERIES SERVED" value={metrics.queries_served} sub={`avg ${metrics.avg_response_ms}ms`} />
            <Stat label="RCA RUNS" value={metrics.agent_invocations.rca} sub="Agent invocations" />
            <Stat label="COMPLIANCE AUDITS" value={metrics.agent_invocations.compliance} sub="Agent invocations" />
          </div>
        </>
      )}
    </div>
  );
}

function Stat({ label, value, sub }: { label: string; value: number; sub: string }) {
  return (
    <div className="px-4 py-4">
      <div className="text-2xl font-medium text-white">{value.toLocaleString()}</div>
      <div className="mt-1 text-[9px] tracking-wider text-white/35">{label}</div>
      <div className="text-[10px] text-white/30">{sub}</div>
    </div>
  );
}
