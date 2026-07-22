import { useState } from "react";
import { Check, X, GitMerge } from "lucide-react";
import { reviewQueue } from "../data/mockData";

type Resolution = "pending" | "merged" | "rejected";

export default function ReviewQueuePage() {
  const [resolutions, setResolutions] = useState<Record<string, Resolution>>({});

  const resolve = (id: string, r: Resolution) => setResolutions((prev) => ({ ...prev, [id]: r }));

  const pendingCount = reviewQueue.filter((c) => (resolutions[c.id] ?? "pending") === "pending").length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-medium text-white">Review Queue</h1>
        <p className="text-sm text-white/45">
          {pendingCount} candidate{pendingCount === 1 ? "" : "s"} awaiting resolution -- matched by rapidfuzz across
          ingested sources.
        </p>
      </div>

      <div className="space-y-3">
        {reviewQueue.map((c) => {
          const resolution = resolutions[c.id] ?? "pending";
          return (
            <div
              key={c.id}
              className="rounded-lg bg-white/[0.03] px-4 py-3.5 ring-1 ring-white/5"
              style={{ opacity: resolution === "pending" ? 1 : 0.45 }}
            >
              <div className="flex items-center justify-between gap-4">
                <div className="flex min-w-0 items-center gap-3">
                  <span className="rounded bg-white/[0.06] px-2 py-1 font-mono text-[12px] text-white/85">
                    {c.entityA}
                  </span>
                  <GitMerge className="h-3.5 w-3.5 shrink-0 text-white/30" />
                  <span className="rounded bg-white/[0.06] px-2 py-1 font-mono text-[12px] text-white/85">
                    {c.entityB}
                  </span>
                  <span className="shrink-0 rounded-full bg-white/[0.04] px-2 py-0.5 text-[10px] text-white/40">
                    {c.entityType}
                  </span>
                </div>

                <div className="flex shrink-0 items-center gap-2">
                  {resolution === "pending" ? (
                    <>
                      <button
                        onClick={() => resolve(c.id, "merged")}
                        className="flex items-center gap-1 rounded-full bg-[#28c840]/15 px-3 py-1.5 text-[11px] font-medium text-[#28c840] hover:bg-[#28c840]/25"
                      >
                        <Check className="h-3 w-3" /> Merge
                      </button>
                      <button
                        onClick={() => resolve(c.id, "rejected")}
                        className="flex items-center gap-1 rounded-full bg-white/[0.06] px-3 py-1.5 text-[11px] font-medium text-white/60 hover:bg-white/[0.1]"
                      >
                        <X className="h-3 w-3" /> Not a match
                      </button>
                    </>
                  ) : (
                    <span className="text-[11px] text-white/40">
                      {resolution === "merged" ? "Merged" : "Kept separate"}
                    </span>
                  )}
                </div>
              </div>

              <div className="mt-3 flex items-center gap-3">
                <div className="h-1.5 flex-1 overflow-hidden rounded-full bg-white/[0.06]">
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${c.confidence * 100}%`,
                      background: c.confidence > 0.85 ? "#28c840" : c.confidence > 0.7 ? "#febc2e" : "#E08A3C",
                    }}
                  />
                </div>
                <span className="w-10 shrink-0 text-right font-mono text-[11px] text-white/50">
                  {Math.round(c.confidence * 100)}%
                </span>
              </div>
              <div className="mt-1.5 text-[10px] text-white/35">Source: {c.source}</div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
