interface ResultViewerProps {
  data: unknown;
}

function isPlainObject(v: unknown): v is Record<string, unknown> {
  return typeof v === "object" && v !== null && !Array.isArray(v);
}

function ValueNode({ value, depth }: { value: unknown; depth: number }) {
  if (value === null || value === undefined) {
    return <span className="text-white/30">--</span>;
  }
  if (Array.isArray(value)) {
    if (value.length === 0) return <span className="text-white/30">[]</span>;
    return (
      <div className="space-y-1.5">
        {value.map((item, i) => (
          <div key={i} className="rounded-md bg-white/[0.03] px-3 py-2 ring-1 ring-white/5">
            <ValueNode value={item} depth={depth + 1} />
          </div>
        ))}
      </div>
    );
  }
  if (isPlainObject(value)) {
    return (
      <div className="space-y-1.5">
        {Object.entries(value).map(([k, v]) => (
          <div key={k} className={depth === 0 ? "grid grid-cols-[160px_1fr] gap-3 border-b border-white/5 py-2 last:border-b-0" : "grid grid-cols-[120px_1fr] gap-2"}>
            <span className="text-[10px] tracking-wider text-white/35">{k.toUpperCase()}</span>
            <div className="text-[12.5px] text-white/80">
              <ValueNode value={v} depth={depth + 1} />
            </div>
          </div>
        ))}
      </div>
    );
  }
  if (typeof value === "number") {
    return <span className="font-mono text-white/85">{value.toLocaleString()}</span>;
  }
  return <span className="whitespace-pre-wrap">{String(value)}</span>;
}

export default function ResultViewer({ data }: ResultViewerProps) {
  return (
    <div className="rounded-lg bg-white/[0.03] px-4 py-3 ring-1 ring-white/5">
      <ValueNode value={data} depth={0} />
    </div>
  );
}
