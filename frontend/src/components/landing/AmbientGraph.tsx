interface AmbientGraphProps {
  className?: string;
  dim?: boolean;
}

const nodes = [
  { x: 12, y: 20 }, { x: 28, y: 12 }, { x: 44, y: 26 }, { x: 60, y: 14 },
  { x: 76, y: 24 }, { x: 90, y: 10 }, { x: 20, y: 45 }, { x: 38, y: 52 },
  { x: 55, y: 44 }, { x: 70, y: 55 }, { x: 85, y: 46 }, { x: 15, y: 72 },
  { x: 33, y: 80 }, { x: 50, y: 70 }, { x: 66, y: 82 }, { x: 82, y: 74 },
];

const edges: [number, number][] = [
  [0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [0, 6], [1, 6], [2, 7], [3, 8],
  [4, 9], [5, 10], [6, 7], [7, 8], [8, 9], [9, 10], [6, 11], [7, 12],
  [8, 13], [9, 14], [10, 15], [11, 12], [12, 13], [13, 14], [14, 15],
];

/**
 * A slow-drifting, glowing node graph rendered as SVG. Stands in for the
 * cinematic background video from the recreation prompt -- original
 * artwork, no external media dependency.
 */
export default function AmbientGraph({ className = "", dim = false }: AmbientGraphProps) {
  return (
    <svg
      viewBox="0 0 100 100"
      preserveAspectRatio="xMidYMid slice"
      className={`graph-drift h-full w-full ${className}`}
      style={{ opacity: dim ? 0.35 : 0.6 }}
      aria-hidden="true"
    >
      <defs>
        <radialGradient id="ambient-glow" cx="50%" cy="35%" r="70%">
          <stop offset="0%" stopColor="rgba(255,255,255,0.10)" />
          <stop offset="100%" stopColor="rgba(255,255,255,0)" />
        </radialGradient>
      </defs>
      <rect width="100" height="100" fill="url(#ambient-glow)" />
      <g strokeLinecap="round">
        {edges.map(([a, b], i) => (
          <line
            key={i}
            x1={nodes[a].x}
            y1={nodes[a].y}
            x2={nodes[b].x}
            y2={nodes[b].y}
            pathLength={1}
            stroke="rgba(255,255,255,0.35)"
            strokeWidth={0.15}
            className="graph-edge"
            style={{ animationDelay: `${i * 90}ms`, animationDuration: "3s" }}
          />
        ))}
      </g>
      <g>
        {nodes.map((n, i) => (
          <circle
            key={i}
            cx={n.x}
            cy={n.y}
            r={0.7}
            fill="rgba(255,255,255,0.8)"
            className="graph-node"
            style={{ animationDelay: `${(i % 6) * 300}ms` }}
          />
        ))}
      </g>
    </svg>
  );
}
