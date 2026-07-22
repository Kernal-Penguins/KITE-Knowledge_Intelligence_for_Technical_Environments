import { useState } from "react";
import { Search, Loader2, AlertTriangle, FileWarning, Lightbulb } from "lucide-react";
import { useRunRca } from "../hooks/useKiteApi";
import MarkdownLite from "../components/MarkdownLite";

const EXAMPLE_TAGS = ["P-101", "V-205", "HX-310", "MOT-118", "TK-04"];

export default function RcaPage() {
  const [equipmentId, setEquipmentId] = useState("");
  const rca = useRunRca();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-medium text-white">Root Cause Analysis</h1>
        <p className="text-sm text-white/45">
          Enter an equipment tag to traverse its graph context (failures, work orders, inspections)
          and generate an AI-written RCA report.
        </p>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (equipmentId.trim()) rca.mutate(equipmentId.trim());
        }}
        className="flex items-center gap-3 rounded-full bg-white/[0.05] py-1.5 pl-5 pr-1.5 ring-1 ring-white/10"
      >
        <input
          value={equipmentId}
          onChange={(e) => setEquipmentId(e.target.value)}
          placeholder="Equipment tag — e.g. P-101"
          className="flex-1 bg-transparent py-2 font-mono text-sm text-white outline-none placeholder-white/35"
        />
        <button
          type="submit"
          disabled={rca.isPending || !equipmentId.trim()}
          className="flex items-center gap-1.5 rounded-full bg-[#E08A3C] px-4 py-2 text-[12px] font-medium text-[#0B0F14] hover:bg-[#EDA45E] disabled:opacity-50"
        >
          {rca.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Search className="h-3.5 w-3.5" />}
          Run RCA
        </button>
      </form>

      {/* Example tags hint */}
      {!rca.data && !rca.isPending && !rca.isError && (
        <div className="space-y-2">
          <div className="flex items-center gap-1.5 text-[11px] text-white/35">
            <Lightbulb className="h-3 w-3" />
            Enter any equipment tag from your knowledge graph. Example tags:
          </div>
          <div className="flex flex-wrap gap-2">
            {EXAMPLE_TAGS.map((tag) => (
              <button
                key={tag}
                onClick={() => setEquipmentId(tag)}
                className="rounded bg-white/[0.04] px-2.5 py-1 font-mono text-[11px] text-white/55 ring-1 ring-white/10 hover:bg-white/[0.08] hover:text-white/80 transition-colors"
              >
                {tag}
              </button>
            ))}
          </div>
        </div>
      )}

      {rca.isError && (
        <div className="flex items-center gap-2 rounded-lg bg-[#E08A3C]/10 px-4 py-3 text-sm text-[#E08A3C] ring-1 ring-[#E08A3C]/20">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          {rca.error instanceof Error ? rca.error.message : "RCA failed — check logs."}
        </div>
      )}

      {rca.data?.error && (
        <div className="flex items-center gap-2 rounded-lg bg-white/[0.04] px-4 py-3 text-sm text-white/60 ring-1 ring-white/10">
          <FileWarning className="h-4 w-4 shrink-0" />
          {rca.data.error}
        </div>
      )}

      {rca.data?.report && (
        <div className="rounded-lg bg-white/[0.03] px-5 py-4 ring-1 ring-white/5">
          <div className="mb-4 flex items-center gap-2">
            <span className="rounded-full bg-white/[0.06] px-2.5 py-1 font-mono text-[11px] text-white/70">
              {rca.data.equipment_id}
            </span>
            <span className="rounded-full bg-[#4FD1C5]/10 px-2.5 py-1 text-[11px] text-[#4FD1C5]">
              {rca.data.evidence_count} graph records analysed
            </span>
          </div>
          <MarkdownLite text={rca.data.report} />
        </div>
      )}
    </div>
  );
}
