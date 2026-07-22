import { useMemo, useState } from "react";
import { AlertTriangle } from "lucide-react";
import ReactFlow, { Background, Controls, MiniMap, type Edge, type Node } from "reactflow";
import "reactflow/dist/style.css";
import { equipment, documents, relationships, type EquipmentStatus } from "../data/mockData";

const statusFill: Record<EquipmentStatus, string> = {
  Operational: "rgba(40,200,64,0.14)",
  Warning: "rgba(254,188,46,0.16)",
  Failed: "rgba(224,138,60,0.18)",
};

const statusBorder: Record<EquipmentStatus, string> = {
  Operational: "#28c840",
  Warning: "#febc2e",
  Failed: "#E08A3C",
};

const equipmentPositions: Record<string, { x: number; y: number }> = {
  "eq-p101": { x: 260, y: 60 },
  "eq-v205": { x: 520, y: 60 },
  "eq-tk04": { x: 780, y: 60 },
  "eq-hx310": { x: 80, y: 240 },
  "eq-mot118": { x: 400, y: 260 },
};

const documentPositions: Record<string, { x: number; y: number }> = {
  "doc-1": { x: 100, y: 440 },
  "doc-2": { x: 520, y: 440 },
  "doc-3": { x: 780, y: 440 },
  "doc-4": { x: 0, y: 580 },
  "doc-5": { x: 400, y: 580 },
};

export default function GraphExplorerPage() {
  const [showDocuments, setShowDocuments] = useState(true);

  const nodes: Node[] = useMemo(() => {
    const eqNodes: Node[] = equipment.map((e) => ({
      id: e.id,
      position: equipmentPositions[e.id],
      data: { label: `${e.tag}\n${e.type}` },
      style: {
        background: statusFill[e.status],
        border: `1px solid ${statusBorder[e.status]}`,
        borderRadius: 10,
        color: "#E7ECF2",
        fontSize: 11,
        fontFamily: "IBM Plex Mono, monospace",
        padding: 8,
        width: 150,
        whiteSpace: "pre-line",
        textAlign: "center" as const,
      },
    }));

    if (!showDocuments) return eqNodes;

    const docNodes: Node[] = documents.map((d) => ({
      id: d.id,
      position: documentPositions[d.id],
      data: { label: d.filename },
      style: {
        background: "rgba(79,209,197,0.08)",
        border: "1px dashed #4FD1C5",
        borderRadius: 8,
        color: "#B7C0CB",
        fontSize: 10,
        fontFamily: "IBM Plex Mono, monospace",
        padding: 8,
        width: 170,
        textAlign: "center" as const,
      },
    }));

    return [...eqNodes, ...docNodes];
  }, [showDocuments]);

  const edges: Edge[] = useMemo(() => {
    return relationships
      .filter((r) => showDocuments || (!r.from.startsWith("doc") && !r.to.startsWith("doc")))
      .map((r, i) => ({
        id: `e-${i}`,
        source: r.from,
        target: r.to,
        label: r.type,
        labelStyle: { fill: "#8A95A3", fontSize: 9 },
        style: { stroke: "#3A4552" },
        animated: r.type === "CONNECTED_TO",
      }));
  }, [showDocuments]);

  return (
    <div className="flex h-[calc(100vh-7.5rem)] flex-col gap-4">
      <div className="flex items-start gap-2 rounded-lg bg-[#4FD1C5]/10 px-4 py-3 text-[12px] text-[#4FD1C5] ring-1 ring-[#4FD1C5]/20">
        <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
        <span>
          Preview using sample data -- your backend's <code>/metrics</code> confirms Neo4j has real nodes/edges, but
          there's no endpoint yet that returns the actual graph. Add a route (e.g. <code>GET /api/v1/graph</code>)
          that queries Neo4j and returns nodes + relationships, and this view can be wired to it directly.
        </span>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-medium text-white">Graph Explorer</h1>
          <p className="text-sm text-white/45">Traverse how assets, documents, and status connect.</p>
        </div>
        <label className="flex items-center gap-2 text-[12px] text-white/60">
          <input
            type="checkbox"
            checked={showDocuments}
            onChange={(e) => setShowDocuments(e.target.checked)}
            className="accent-[#E08A3C]"
          />
          Show documents
        </label>
      </div>

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
    </div>
  );
}
