import {
  PanelLeft,
  ChevronLeft,
  ChevronRight,
  Monitor,
  RotateCw,
  Share,
  Plus,
  Copy,
  Compass,
  Layers,
  ListTodo,
  Sparkles,
  Cog,
} from "lucide-react";

const stats = [
  { label: "ENTITIES MAPPED", value: "8,412", sub: "Assets & components" },
  { label: "ENTITY TYPES", value: "34", sub: "Distinct classes" },
  { label: "RELATIONSHIPS", value: "24,905", sub: "Connections traced" },
  { label: "PENDING REVIEW", value: "156", sub: "Needs validation" },
];

const clusters = [
  { name: "Rotating Equipment", count: "2,140 entities" },
  { name: "Piping & Instrumentation", count: "3,760 entities" },
  { name: "Electrical Systems", count: "1,508 entities" },
];

const imports = [
  { source: "P&ID_Unit-204.pdf", entities: 312, relationships: 588, status: "Complete", color: "#28c840" },
  { source: "sap_asset_export.csv", entities: 1204, relationships: 2210, status: "Complete", color: "#28c840" },
  { source: "electrical_schematics/", entities: 96, relationships: 140, status: "Processing", color: "#febc2e" },
  { source: "maintenance_logs_q2.json", entities: 58, relationships: 74, status: "Needs Review", color: "#E08A3C" },
  { source: "vendor_manuals_batch3.pdf", entities: 210, relationships: 305, status: "Processing", color: "#febc2e" },
];

const recentSynced = [
  "SAP PM Module",
  "Historian — Unit 3",
  "Document Vault",
];

export default function DashboardMockup() {
  return (
    <div className="rounded-t-2xl overflow-hidden bg-[#1a1a1c] text-left shadow-[0_-20px_80px_rgba(0,0,0,0.35)] ring-1 ring-white/10">
      {/* title bar */}
      <div className="flex items-center gap-3 border-b border-white/5 bg-[#242427] px-4 py-2.5">
        <div className="flex items-center gap-1.5">
          <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: "#ff5f57" }} />
          <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: "#febc2e" }} />
          <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: "#28c840" }} />
        </div>
        <div className="flex items-center gap-2.5 pl-1">
          <PanelLeft className="h-3.5 w-3.5 text-white/40" />
          <ChevronLeft className="h-3.5 w-3.5 text-white/40" />
          <ChevronRight className="h-3.5 w-3.5 text-white/25" />
        </div>
        <div className="mx-auto flex items-center gap-2 rounded-md bg-[#1a1a1c] px-6 py-1">
          <Monitor className="h-3 w-3 text-white/40" />
          <span className="text-[10px] text-white/60">app.kite.io</span>
        </div>
        <div className="flex items-center gap-3">
          <RotateCw className="h-3.5 w-3.5 text-white/40" />
          <Share className="h-3.5 w-3.5 text-white/40" />
          <Plus className="h-3.5 w-3.5 text-white/40" />
          <Copy className="h-3.5 w-3.5 text-white/40" />
        </div>
      </div>

      <div className="flex">
        {/* sidebar */}
        <div className="w-[22%] border-r border-white/5 bg-[#1e1e21] px-3 py-3.5">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-1.5 text-white/70">
              <svg viewBox="0 0 256 256" className="h-4 w-4" fill="currentColor">
                <path d="M 144 256 L 27.598 256 L 144 139.598 Z M 256 207.5 L 200 256 L 200 56 L 0 56 L 48 0 L 256 0 Z M 0 204.402 L 0 112 L 92.402 112 Z" />
              </svg>
            </div>
            <Layers className="h-3.5 w-3.5 text-white/30" />
          </div>

          <div className="mb-4 flex items-center gap-2">
            <div className="flex h-4 w-4 items-center justify-center rounded bg-[#c1502e] text-[9px] font-semibold text-white">
              N
            </div>
            <span className="text-[10px] text-white/80">Northgate Refinery</span>
          </div>

          <div className="space-y-2.5">
            <div className="flex items-center gap-2 text-[10px] text-white/60">
              <Compass className="h-3 w-3" /> Explore
            </div>
            <div className="flex items-center gap-2 text-[10px] text-white/60">
              <Layers className="h-3 w-3" /> Entity Types
            </div>
            <div className="flex items-center gap-2 text-[10px] text-white/60">
              <ListTodo className="h-3 w-3" /> Review Queue
            </div>
          </div>

          <div className="mt-5 border-t border-white/5 pt-3">
            <div className="mb-2 text-[8px] tracking-wider text-white/30">RECENTLY SYNCED</div>
            <div className="space-y-2">
              {recentSynced.map((item) => (
                <div key={item} className="flex items-center gap-1.5 text-[9.5px] text-white/50">
                  <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: "#28c840b3" }} />
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* main content */}
        <div className="flex-1 px-5 py-4">
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#c1502e]">
                <Cog className="h-4 w-4 text-white/90" />
              </div>
              <div>
                <div className="text-sm font-medium text-white">Northgate Refinery</div>
                <div className="text-[10px] text-white/45">Knowledge graph &middot; updated 2 min ago</div>
              </div>
            </div>
            <button className="flex items-center gap-1.5 rounded-full bg-white/[0.06] px-3 py-1.5 text-[10px] text-white/80 ring-1 ring-white/10">
              <Sparkles className="h-3 w-3" /> Extract Entities
            </button>
          </div>

          {/* stats */}
          <div className="mb-4 grid grid-cols-4 divide-x divide-white/5 rounded-xl bg-white/[0.03] ring-1 ring-white/5">
            {stats.map((s) => (
              <div key={s.label} className="px-3 py-3">
                <div className="text-xl font-medium text-white">{s.value}</div>
                <div className="mt-1 text-[8px] tracking-wider text-white/35">{s.label}</div>
                <div className="text-[9px] text-white/30">{s.sub}</div>
              </div>
            ))}
          </div>

          {/* clusters */}
          <div className="mb-4 grid grid-cols-3 gap-3">
            {clusters.map((c) => (
              <div key={c.name} className="rounded-lg bg-white/[0.03] px-3 py-2.5 ring-1 ring-white/5">
                <div className="text-[11px] font-medium text-white/85">{c.name}</div>
                <div className="mt-1 text-[9.5px] text-white/40">{c.count}</div>
              </div>
            ))}
          </div>

          {/* recent imports */}
          <div className="rounded-lg bg-white/[0.03] ring-1 ring-white/5">
            <div className="grid grid-cols-4 gap-2 border-b border-white/5 px-3 py-2 text-[8px] tracking-wider text-white/30">
              <span>SOURCE</span>
              <span>ENTITIES</span>
              <span>RELATIONSHIPS</span>
              <span>STATUS</span>
            </div>
            {imports.map((row) => (
              <div
                key={row.source}
                className="grid grid-cols-4 gap-2 border-b border-white/5 px-3 py-2 text-[10px] text-white/70 last:border-b-0"
              >
                <span className="truncate font-mono text-white/60">{row.source}</span>
                <span>{row.entities}</span>
                <span>{row.relationships}</span>
                <span style={{ color: row.color, opacity: 0.9 }}>{row.status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
