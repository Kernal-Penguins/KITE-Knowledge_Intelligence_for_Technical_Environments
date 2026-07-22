import { useMemo, useState } from "react";
import { Loader2, AlertTriangle, Share2 } from "lucide-react";
import ReactFlow, { Background, Controls, MiniMap, type Edge, type Node } from "reactflow";
import "reactflow/dist/style.css";
import { useGraphData } from "../hooks/useKiteApi";

const NODE_COLORS: Record<string, { bg: string; border: string }> = {
  Equipment: { bg: "rgba(40,200,64,0.14)", border: "#28c840" },
  Failure: { bg: "rgba(224,138,60,0.18)", border: "#E08A3C" },
  Procedure: { bg: "rgba(79,209,197,0.08)", border: "#4FD1C5" },
  Person: { bg: "rgba(254,188,46,0.16)", border: "#febc2e" },
  Inspection: { bg: "rgba(147,130,255,0.12)", border: "#9382FF" },
  Regulation: { bg: "rgba(180,180,180,0.1)", border: "#8A95A3" },
};

function layoutNodes(rawNodes: { id: string; label: string; node_type: string }[]): Node[] {
  const cols = Math.max(1, Math.ceil(Math.sqrt(rawNodes.length)));
  return rawNodes.map((n, i) => {
    const colors = NODE_COLORS[n.node_type] ?? { bg: "rgba(255,255,255,0.06)", border: "#3A4552" };
    return {
      id: n.id,
      position: { x: (i % cols) * 200, y: Math.floor(i / cols) * 130 },
      data: { label: `${n.label}\n${n.node_type}` },
      style: {
        background: colors.bg,
        border: `1px solid ${colors.border}`,
        borderRadius: 10,
        color: "#E7ECF2",
        fontSize: 11,
        fontFamily: "IBM Plex Mono, monospace",
        padding: 8,
        width: 150,
        whiteSpace: "pre-line" as const,
        textAlign: "center" as const,
      },
    };
  });
}

export default function GraphExplorerPage() {
  const [showDocuments, setShowDocuments] = useState(true);
  const { data, isLoading, isError } = useGraphData(100);

  const filteredNodes = useMemo(() => {
    if (!data?.nodes) return [];
    if (showDocuments) return data.nodes;
    return data.nodes.filter((n) => n.node_type !== "Document");
  }, [data, showDocuments]);

  const nodeIds = useMemo(() => new Set(filteredNodes.map((n) => n.id)), [filteredNodes]);

  const nodes: Node[] = useMemo(
    () => layoutNodes(filteredNodes.map((n) => ({ id: n.id, label: n.label, node_type: n.node_type }))),
    [filteredNodes],
  );

  const edges: Edge[] = useMemo(() => {
    if (!data?.edges) return [];
    return data.edges
      .filter((e) => nodeIds.has(e.source) && nodeIds.has(e.target))
      .map((e, i) => ({
        id: `e-${i}`,
        source: e.source,
        target: e.target,
        label: e.rel_type,
        labelStyle: { fill: "#8A95A3", fontSize: 9 },
        style: { stroke: "#3A4552" },
        animated: e.rel_type === "CONNECTED_TO" || e.rel_type === "AFFECTS",
      }));
  }, [data, nodeIds]);

  const isEmpty = !isLoading && !isError && filteredNodes.length === 0;

  return (
    <div className="flex h-[calc(100vh-7.5rem)] flex-col gap-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-medium text-white">Graph Explorer</h1>
          <p className="text-sm text-white/45">
            Upload engineering documents to generate a knowledge graph, then explore connections here.
          </p>
        </div>
        <label className="flex items-center gap-2 text-[12px] text-white/60">
          <input
            type="checkbox"
            checked={showDocuments}
            onChange={(e) => setShowDocuments(e.target.checked)}
            className="accent-[#E08A3C]"
            aria-label="Show document nodes"
          />
          Show documents
        </label>
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 text-sm text-white/40" role="status">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          Loading graph…
        </div>
      )}

      {isError && (
        <div className="flex items-center gap-2 rounded-lg bg-[#E08A3C]/10 px-4 py-3 text-sm text-[#E08A3C] ring-1 ring-[#E08A3C]/20">
          <AlertTriangle className="h-4 w-4 shrink-0" aria-hidden="true" />
          Graph unavailable right now. Upload documents to build your graph, then try again.
        </div>
      )}

      {isEmpty && (
        <div className="flex flex-col items-center justify-center gap-2 rounded-xl bg-white/[0.02] px-6 py-16 ring-1 ring-white/5">
          <Share2 className="h-8 w-8 text-white/20" aria-hidden="true" />
          <p className="text-sm text-white/50">No graph data yet.</p>
          <p className="max-w-md text-center text-[12px] text-white/30">
            Upload maintenance logs, SOPs, or inspection reports from the Ingest page. The pipeline will
            extract entities and relationships automatically.
          </p>
        </div>
      )}

      {!isEmpty && !isLoading && (
        <div className="min-h-0 flex-1 overflow-hidden rounded-xl bg-white/[0.02] ring-1 ring-white/5">
          <ReactFlow nodes={nodes} edges={edges} fitView proOptions={{ hideAttribution: true }}>
            <Background color="#232a33" gap={24} />
            <Controls className="!fill-white [&_button]:!border-white/10 [&_button]:!bg-[#12181F] [&_button]:!text-white" />
            <MiniMap
              pannable
              zoomable
              maskColor="rgba(11,15,20,0.7)"
              nodeColor={() => "#3A4552"}
              style={{ background: "#0E1319" }}
            />
          </ReactFlow>
        </div>
      )}

      {data && data.total_nodes > 0 && (
        <div className="text-[11px] text-white/30">
          Showing {filteredNodes.length} of {data.total_nodes} nodes · {data.total_edges} relationships
        </div>
      )}
    </div>
  );
}
