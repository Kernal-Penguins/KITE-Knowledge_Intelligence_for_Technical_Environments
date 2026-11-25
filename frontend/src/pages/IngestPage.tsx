import { useRef, useState } from "react";
import { UploadCloud, FileText, Loader2, AlertTriangle, CheckCircle2, Clock, XCircle, RefreshCw } from "lucide-react";
import { useIngestDocument, useUploadsList } from "../hooks/useKiteApi";
import type { IngestResponse, UploadRecord } from "../lib/types";

interface TrackedJob extends IngestResponse {
  uploadedAt: string;
}

const STATUS_ICON: Record<string, React.ReactNode> = {
  queued:    <Clock className="h-3 w-3" />,
  complete:  <CheckCircle2 className="h-3 w-3" />,
  failed:    <XCircle className="h-3 w-3" />,
};

const STATUS_COLOR: Record<string, string> = {
  queued:    "text-[#febc2e]",
  parsing:   "text-[#febc2e]",
  extracting:"text-[#febc2e]",
  resolving: "text-[#febc2e]",
  writing_graph: "text-[#febc2e]",
  vectorizing: "text-[#febc2e]",
  complete:  "text-[#28c840]",
  failed:    "text-[#E08A3C]",
};

function JobRow({
  filename,
  docType,
  jobId,
  when,
  status,
  errorMessage,
}: {
  filename: string;
  docType: string;
  jobId: string;
  when: string;
  status: string;
  errorMessage?: string | null;
}) {
  return (
    <div className="border-b border-white/5 last:border-b-0">
      <div className="grid grid-cols-5 gap-2 px-4 py-2.5 text-[12px] text-white/70">
        <span className="flex items-center gap-2 truncate font-mono text-white/60">
          <FileText className="h-3.5 w-3.5 shrink-0 text-white/30" />
          {filename}
        </span>
        <span>{docType}</span>
        <span className="font-mono text-white/45">{jobId.slice(0, 12)}</span>
        <span className="text-white/40">{when}</span>
        <span className={`flex items-center gap-1 ${STATUS_COLOR[status] ?? "text-white/50"}`}>
          {status === "complete" || status === "failed" || status === "queued"
            ? STATUS_ICON[status]
            : <Loader2 className="h-3 w-3 animate-spin" />}
          {status}
        </span>
      </div>
      {errorMessage && status === "failed" && (
        <p className="px-4 pb-2.5 text-[11px] leading-snug text-[#E08A3C]/90">{errorMessage}</p>
      )}
    </div>
  );
}

export default function IngestPage() {
  const [sessionJobs, setSessionJobs] = useState<TrackedJob[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const ingest = useIngestDocument();
  const { data: pastUploads, isLoading: uploadsLoading, refetch } = useUploadsList();

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    Array.from(files).forEach((file) => {
      ingest.mutate(file, {
        onSuccess: (data) => {
          setSessionJobs((prev) => [{ ...data, uploadedAt: new Date().toLocaleTimeString() }, ...prev]);
          // Refresh the persistent list after a short delay (pipeline picks it up)
          setTimeout(() => refetch(), 1500);
        },
      });
    });
  };

  // Session rows stay on screen immediately. Their status is replaced by the
  // polled upload record so "queued" moves to complete or failed on its own.
  const uploadById = new Map((pastUploads ?? []).map((u) => [u.job_id, u]));
  const sessionJobIds = new Set(sessionJobs.map((j) => j.job_id));
  const backendRows = (pastUploads ?? []).filter((u) => !sessionJobIds.has(u.job_id));

  const liveSession = sessionJobs.map((job) => {
    const live: UploadRecord | undefined = uploadById.get(job.job_id);
    return live
      ? { ...job, status: live.status, doc_type: live.doc_type, error_message: live.error_message }
      : { ...job, error_message: null as string | null };
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-medium text-white">Ingest Documents</h1>
        <p className="text-sm text-white/45">
          Upload plant documents — maintenance logs, inspection reports, SOPs, P&IDs, work orders.
          Each file is parsed, chunked, embedded, and linked into the knowledge graph.
        </p>
      </div>

      {/* Onboarding tip */}
      <div className="rounded-lg border border-dashed border-[#4FD1C5]/30 bg-[#4FD1C5]/[0.04] px-4 py-3 text-[12px] text-[#4FD1C5]/80">
        <strong className="font-medium text-[#4FD1C5]">Getting started:</strong> Drop any PDF, DOCX, CSV, or image
        file here. The pipeline will extract entities (equipment tags, failure events, procedures) and build graph
        relationships automatically. You can then query them from the Copilot or run RCA.
      </div>

      {/* Drop zone */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFiles(e.dataTransfer.files); }}
        onClick={() => inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border border-dashed px-6 py-10 text-center transition-colors ${
          dragOver ? "border-[#E08A3C] bg-[#E08A3C]/5" : "border-white/15 bg-white/[0.02]"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.doc,.csv,.txt,.png,.jpg,.jpeg,.png"
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        {ingest.isPending ? (
          <Loader2 className="h-7 w-7 animate-spin text-white/40" />
        ) : (
          <UploadCloud className="h-7 w-7 text-white/40" />
        )}
        <p className="text-sm text-white/70">Drop files here, or click to browse</p>
        <p className="text-[11px] text-white/35">PDF · DOCX · CSV · TXT · PNG · JPG</p>
      </div>

      {ingest.isError && (
        <div className="flex items-center gap-2 rounded-lg bg-[#E08A3C]/10 px-4 py-3 text-sm text-[#E08A3C] ring-1 ring-[#E08A3C]/20">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          Upload failed: {ingest.error instanceof Error ? ingest.error.message : "unknown error"}
        </div>
      )}

      {/* Upload history */}
      <div className="rounded-lg bg-white/[0.03] ring-1 ring-white/5">
        <div className="flex items-center justify-between border-b border-white/5 px-4 py-2.5">
          <span className="text-[11px] text-white/40">Upload History</span>
          <button
            onClick={() => refetch()}
            className="flex items-center gap-1 rounded px-2 py-1 text-[10px] text-white/35 hover:text-white/60"
            title="Refresh"
          >
            <RefreshCw className="h-3 w-3" /> Refresh
          </button>
        </div>

        {sessionJobs.length === 0 && backendRows.length === 0 ? (
          <div className="px-4 py-6 text-center text-[12px] text-white/30">
            {uploadsLoading ? "Loading history…" : "No uploads yet. Drop a file above to get started."}
          </div>
        ) : (
          <>
            <div className="grid grid-cols-5 gap-2 border-b border-white/5 px-4 py-2 text-[9px] tracking-wider text-white/30">
              <span>FILE</span>
              <span>DOC TYPE</span>
              <span>JOB ID</span>
              <span>UPLOADED</span>
              <span>STATUS</span>
            </div>

            {liveSession.map((job) => (
              <JobRow
                key={job.job_id}
                filename={job.filename}
                docType={job.doc_type}
                jobId={job.job_id}
                when={job.uploadedAt}
                status={job.status}
                errorMessage={job.error_message}
              />
            ))}

            {backendRows.map((job) => (
              <JobRow
                key={job.job_id}
                filename={job.filename}
                docType={job.doc_type}
                jobId={job.job_id}
                when={job.created_at ? new Date(job.created_at).toLocaleString() : "—"}
                status={job.status}
                errorMessage={job.error_message}
              />
            ))}
          </>
        )}
      </div>
    </div>
  );
}
