interface Node {
  id: string;
  x: number;
  y: number;
  r: number;
  color: "copper" | "cyan" | "dim";
}

interface Edge {
  from: string;
  to: string;
  delay: number;
}

// A loose plant-graph: rotating equipment, piping, and instrumentation
// nodes wired together the way KITE would actually trace them.
const nodes: Node[] = [
  { id: "a1", x: 180, y: 160, r: 4, color: "copper" },
  { id: "a2", x: 320, y: 110, r: 3, color: "dim" },
  { id: "a3", x: 300, y: 260, r: 3, color: "cyan" },
  { id: "a4", x: 470, y: 200, r: 5, color: "copper" },
  { id: "a5", x: 560, y: 90, r: 3, color: "dim" },
  { id: "a6", x: 640, y: 230, r: 3, color: "cyan" },
  { id: "a7", x: 760, y: 140, r: 4, color: "dim" },
  { id: "a8", x: 860, y: 260, r: 3, color: "copper" },
  { id: "a9", x: 940, y: 130, r: 3, color: "dim" },
  { id: "a10", x: 1040, y: 210, r: 4, color: "cyan" },
  { id: "a11", x: 1150, y: 120, r: 3, color: "dim" },
  { id: "a12", x: 1230, y: 250, r: 3, color: "copper" },
  { id: "b1", x: 120, y: 620, r: 3, color: "dim" },
  { id: "b2", x: 250, y: 700, r: 4, color: "cyan" },
  { id: "b3", x: 380, y: 630, r: 3, color: "dim" },
  { id: "b4", x: 480, y: 730, r: 3, color: "copper" },
  { id: "b5", x: 610, y: 660, r: 4, color: "dim" },
  { id: "b6", x: 720, y: 750, r: 3, color: "cyan" },
  { id: "b7", x: 840, y: 650, r: 3, color: "dim" },
  { id: "b8", x: 960, y: 720, r: 4, color: "copper" },
  { id: "b9", x: 1080, y: 640, r: 3, color: "dim" },
  { id: "b10", x: 1200, y: 710, r: 3, color: "cyan" },
];

const edges: Edge[] = [
  { from: "a1", to: "a2", delay: 0 },
  { from: "a1", to: "a3", delay: 80 },
  { from: "a2", to: "a4", delay: 160 },
  { from: "a3", to: "a4", delay: 240 },
  { from: "a4", to: "a5", delay: 120 },
  { from: "a4", to: "a6", delay: 320 },
  { from: "a5", to: "a7", delay: 200 },
  { from: "a6", to: "a7", delay: 400 },
  { from: "a7", to: "a8", delay: 260 },
  { from: "a7", to: "a9", delay: 480 },
  { from: "a8", to: "a10", delay: 340 },
  { from: "a9", to: "a10", delay: 560 },
  { from: "a10", to: "a11", delay: 400 },
  { from: "a10", to: "a12", delay: 620 },
  { from: "a11", to: "a12", delay: 460 },
  { from: "b1", to: "b2", delay: 60 },
  { from: "b2", to: "b3", delay: 180 },
  { from: "b3", to: "b4", delay: 260 },
  { from: "b3", to: "b5", delay: 340 },
  { from: "b4", to: "b6", delay: 220 },
  { from: "b5", to: "b6", delay: 420 },
  { from: "b5", to: "b7", delay: 300 },
  { from: "b6", to: "b8", delay: 500 },
  { from: "b7", to: "b8", delay: 380 },
  { from: "b7", to: "b9", delay: 560 },
  { from: "b8", to: "b10", delay: 440 },
  { from: "b9", to: "b10", delay: 620 },
];

const colorMap: Record<Node["color"], string> = {
  copper: "#E08A3C",
  cyan: "#4FD1C5",
  dim: "#3A4552",
};

function findNode(id: string) {
  return nodes.find((n) => n.id === id)!;
}

export default function GraphBackground() {
  return (
    <div className="absolute inset-0 z-0 overflow-hidden bg-[#0B0F14]">
      {/* soft directional glow */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "radial-gradient(120% 70% at 50% 0%, rgba(224,138,60,0.10) 0%, rgba(11,15,20,0) 55%), radial-gradient(90% 60% at 85% 90%, rgba(79,209,197,0.08) 0%, rgba(11,15,20,0) 60%)",
        }}
      />

      {/* blueprint grid */}
      <svg className="absolute inset-0 h-full w-full opacity-[0.06]" aria-hidden="true">
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#E7ECF2" strokeWidth="1" />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>

      {/* the graph itself */}
      <svg
        viewBox="0 0 1360 860"
        preserveAspectRatio="xMidYMid slice"
        className="graph-drift absolute inset-0 h-full w-full"
        aria-hidden="true"
      >
        <g strokeLinecap="round">
          {edges.map((e, i) => {
            const from = findNode(e.from);
            const to = findNode(e.to);
            return (
              <line
                key={i}
                x1={from.x}
                y1={from.y}
                x2={to.x}
                y2={to.y}
                pathLength={1}
                stroke="#4A5A68"
                strokeWidth={1}
                strokeOpacity={0.5}
                className="graph-edge"
                style={{ animationDelay: `${e.delay}ms` }}
              />
            );
          })}
        </g>
        <g>
          {nodes.map((n, i) => (
            <circle
              key={n.id}
              cx={n.x}
              cy={n.y}
              r={n.r}
              fill={colorMap[n.color]}
              className="graph-node"
              style={{ animationDelay: `${(i % 7) * 220}ms` }}
            />
          ))}
        </g>
      </svg>

      {/* vignette so foreground text stays legible */}
      <div
        className="absolute inset-0"
        style={{
          background:
            "linear-gradient(180deg, rgba(11,15,20,0.35) 0%, rgba(11,15,20,0.15) 22%, rgba(11,15,20,0.55) 68%, rgba(11,15,20,0.92) 100%)",
        }}
      />
    </div>
  );
}
