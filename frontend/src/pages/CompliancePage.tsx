import { Loader2, AlertTriangle, Check, X, HelpCircle, ShieldCheck, ShieldAlert } from "lucide-react";
import { useComplianceAudit, useReviewComplianceFlag } from "../hooks/useKiteApi";

const ruleLabels: Record<string, string> = {
  rule_1_critical_inspections: "Critical Equipment Missing Recent Inspection",
  rule_2_loto_certification: "LOTO Procedure Without Certified Personnel",
  rule_3_failure_resolution: "Unresolved Failures",
  rule_4_regulated_procedures: "Regulated Equipment Missing Procedure",
  rule_5_incident_closure: "Incidents Without Corrective Action",
};

function entityLabel(row: Record<string, string>): string {
  const idKey = Object.keys(row).find((k) => k.endsWith("_id"));
  return idKey ? `${idKey.replace(/_id$/, "").replace(/_/g, " ")}: ${row[idKey]}` : "";
}

export default function CompliancePage() {
  const { data, isLoading, isError, error } = useComplianceAudit();
  const review = useReviewComplianceFlag();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-medium text-white">Compliance</h1>
        <p className="text-sm text-white/45">
          Runs deterministic audit rules against your knowledge graph to surface compliance gaps.
        </p>
      </div>

      {isLoading && (
        <div className="flex items-center gap-2 text-sm text-white/40">
          <Loader2 className="h-4 w-4 animate-spin" /> Running audit...
        </div>
      )}

      {isError && (
        <div className="flex items-center gap-2 rounded-lg bg-[#E08A3C]/10 px-4 py-3 text-sm text-[#E08A3C] ring-1 ring-[#E08A3C]/20">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          Audit failed. Please try again shortly.
        </div>
      )}

      {data && (
        <>
          <div className="flex items-center gap-3">
            <span
              className={`flex items-center gap-1.5 rounded-full px-3 py-1.5 text-[12px] font-medium ${
                data.status === "passed" ? "bg-[#28c840]/15 text-[#28c840]" : "bg-[#E08A3C]/15 text-[#E08A3C]"
              }`}
            >
              {data.status === "passed" ? <ShieldCheck className="h-3.5 w-3.5" /> : <ShieldAlert className="h-3.5 w-3.5" />}
              {data.status === "passed" ? "Passed" : "Failed"}
            </span>
            <span className="text-[12px] text-white/45">{data.total_gaps} open gap{data.total_gaps === 1 ? "" : "s"}</span>
          </div>

          {Object.entries(data.details).map(([ruleKey, gaps]) => (
            <div key={ruleKey} className="rounded-lg bg-white/[0.03] ring-1 ring-white/5">
              <div className="flex items-center justify-between border-b border-white/5 px-4 py-2.5">
                <span className="text-[13px] font-medium text-white/85">
                  {ruleLabels[ruleKey] ?? ruleKey}
                </span>
                <span className="text-[11px] text-white/35">{gaps.length}</span>
              </div>

              {gaps.length === 0 ? (
                <div className="px-4 py-3 text-[12px] text-white/30">No gaps found.</div>
              ) : (
                gaps.map((row) => (
                  <div
                    key={row.flag_hash}
                    className="flex items-center justify-between gap-3 border-b border-white/5 px-4 py-3 last:border-b-0"
                  >
                    <div className="min-w-0">
                      <div className="truncate text-[12px] text-white/75">{row.gap}</div>
                      <div className="truncate font-mono text-[10.5px] text-white/35">{entityLabel(row)}</div>
                    </div>
                    <div className="flex shrink-0 items-center gap-1.5">
                      <button
                        onClick={() => review.mutate({ flagHash: row.flag_hash, status: "confirmed" })}
                        disabled={review.isPending}
                        title="Confirm gap"
                        className="flex h-7 w-7 items-center justify-center rounded-full bg-[#E08A3C]/15 text-[#E08A3C] hover:bg-[#E08A3C]/25 disabled:opacity-40"
                      >
                        <Check className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => review.mutate({ flagHash: row.flag_hash, status: "dismissed" })}
                        disabled={review.isPending}
                        title="Dismiss"
                        className="flex h-7 w-7 items-center justify-center rounded-full bg-white/[0.06] text-white/60 hover:bg-white/[0.1] disabled:opacity-40"
                      >
                        <X className="h-3.5 w-3.5" />
                      </button>
                      <button
                        onClick={() => review.mutate({ flagHash: row.flag_hash, status: "pending" })}
                        disabled={review.isPending}
                        title="Keep pending"
                        className="flex h-7 w-7 items-center justify-center rounded-full bg-white/[0.06] text-white/60 hover:bg-white/[0.1] disabled:opacity-40"
                      >
                        <HelpCircle className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          ))}
        </>
      )}
    </div>
  );
}
