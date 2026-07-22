import { useState } from "react";
import { Sparkles, Loader2, AlertTriangle, GitBranch, Info } from "lucide-react";
import { useRunLessonsClustering } from "../hooks/useKiteApi";

export default function LessonsPage() {
  const [threshold, setThreshold] = useState(0.85);
  const cluster = useRunLessonsClustering();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-medium text-white">Lessons-Learned Clustering</h1>
        <p className="text-sm text-white/45">
          Groups similar failure events in the knowledge graph by semantic similarity,
          surfacing patterns across equipment and time.
        </p>
      </div>

      {/* How-to tip */}
      <div className="flex items-start gap-2 rounded-lg bg-white/[0.03] px-4 py-3 text-[12px] text-white/55 ring-1 ring-white/5">
        <Info className="mt-0.5 h-3.5 w-3.5 shrink-0 text-[#4FD1C5]" />
        <span>
          Run this after ingesting documents. The algorithm embeds every Failure node description,
          computes cosine similarity, and writes new graph edges for pairs above the threshold.
          Check the Graph Explorer afterwards to see the clusters.
        </span>
      </div>

      <div className="rounded-lg bg-white/[0.03] px-4 py-4 ring-1 ring-white/5">
        <div className="mb-2 flex items-center justify-between text-[12px] text-white/60">
          <span>Cosine similarity threshold</span>
          <span className="font-mono text-white/80">{threshold.toFixed(2)}</span>
        </div>
        <input
          type="range"
          min={0}
          max={1}
          step={0.01}
          value={threshold}
          onChange={(e) => setThreshold(Number(e.target.value))}
          className="w-full accent-[#E08A3C]"
        />
        <p className="mt-1 text-[10px] text-white/30">
          Higher → only near-identical failure descriptions get linked. Lower → broader, looser clusters.
        </p>
        <button
          onClick={() => cluster.mutate(threshold)}
          disabled={cluster.isPending}
          className="mt-4 flex items-center gap-1.5 rounded-full bg-[#E08A3C] px-4 py-2 text-[12px] font-medium text-[#0B0F14] hover:bg-[#EDA45E] disabled:opacity-50"
        >
          {cluster.isPending ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
          Run Clustering
        </button>
      </div>

      {cluster.isError && (
        <div className="flex items-center gap-2 rounded-lg bg-[#E08A3C]/10 px-4 py-3 text-sm text-[#E08A3C] ring-1 ring-[#E08A3C]/20">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          {cluster.error instanceof Error ? cluster.error.message : "Clustering failed."}
        </div>
      )}

      {cluster.data?.status === "skipped" && (
        <div className="rounded-lg bg-white/[0.04] px-4 py-3 text-sm text-white/60 ring-1 ring-white/10">
          Skipped — {cluster.data.reason}
        </div>
      )}

      {cluster.data && cluster.data.status !== "skipped" && (
        <div className="grid grid-cols-3 divide-x divide-white/5 rounded-xl bg-white/[0.03] ring-1 ring-white/5">
          <div className="px-4 py-4">
            <div className="text-2xl font-medium text-white">{cluster.data.processed_failures}</div>
            <div className="mt-1 text-[9px] tracking-wider text-white/35">FAILURES PROCESSED</div>
          </div>
          <div className="px-4 py-4">
            <div className="text-2xl font-medium text-white">{cluster.data.similarity_threshold?.toFixed(2)}</div>
            <div className="mt-1 text-[9px] tracking-wider text-white/35">THRESHOLD USED</div>
          </div>
          <div className="px-4 py-4">
            <div className="flex items-center gap-1.5 text-2xl font-medium text-[#4FD1C5]">
              <GitBranch className="h-4 w-4" /> {cluster.data.new_relationships_created}
            </div>
            <div className="mt-1 text-[9px] tracking-wider text-white/35">NEW EDGES CREATED</div>
          </div>
        </div>
      )}
    </div>
  );
}
