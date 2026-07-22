import { useRef, useState } from "react";
import { UploadCloud, FileText, Loader2, AlertTriangle, CheckCircle2 } from "lucide-react";
import { useIngestDocument } from "../hooks/useKiteApi";
import type { IngestResponse } from "../lib/types";

interface TrackedJob extends IngestResponse {
  uploadedAt: string;
}

export default function IngestPage() {
  const [jobs, setJobs] = useState<TrackedJob[]>([]);
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const ingest = useIngestDocument();

  const handleFiles = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    Array.from(files).forEach((file) => {
      ingest.mutate(file, {
        onSuccess: (data) => {
          setJobs((prev) => [{ ...data, uploadedAt: new Date().toLocaleTimeString() }, ...prev]);
        },
      });
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-medium text-white">Ingest</h1>
        <p className="text-sm text-white/45">
          Uploads POST to <code className="text-white/70">/api/v1/ingest</code> and are queued for background
          processing.
        </p>
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => inputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border border-dashed px-6 py-10 text-center transition-colors ${
          dragOver ? "border-[#E08A3C] bg-[#E08A3C]/5" : "border-white/15 bg-white/[0.02]"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          className="hidden"
          onChange={(e) => handleFiles(e.target.files)}
        />
        {ingest.isPending ? (
          <Loader2 className="h-7 w-7 animate-spin text-white/40" />
        ) : (
          <UploadCloud className="h-7 w-7 text-white/40" />
        )}
        <p className="text-sm text-white/70">Drop files here, or click to browse</p>
        <p className="text-[11px] text-white/35">Sent directly to your FastAPI backend</p>
      </div>

      {ingest.isError && (
        <div className="flex items-center gap-2 rounded-lg bg-[#E08A3C]/10 px-4 py-3 text-sm text-[#E08A3C] ring-1 ring-[#E08A3C]/20">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          Upload failed: {ingest.error instanceof Error ? ingest.error.message : "unknown error"}
        </div>
      )}

      <div className="rounded-lg bg-white/[0.03] ring-1 ring-white/5">
        <div className="border-b border-white/5 px-4 py-2.5 text-[11px] text-white/40">
          This session's uploads -- your backend doesn't yet expose a GET endpoint to list past uploads, so this
          resets on page refresh.
        </div>
        {jobs.length === 0 ? (
          <div className="px-4 py-6 text-center text-[12px] text-white/30">No uploads yet this session.</div>
        ) : (
          <>
            <div className="grid grid-cols-5 gap-2 border-b border-white/5 px-4 py-2 text-[9px] tracking-wider text-white/30">
              <span>FILE</span>
              <span>DOC TYPE</span>
              <span>JOB ID</span>
              <span>UPLOADED</span>
              <span>STATUS</span>
            </div>
            {jobs.map((job) => (
              <div
                key={job.job_id}
                className="grid grid-cols-5 gap-2 border-b border-white/5 px-4 py-2.5 text-[12px] text-white/70 last:border-b-0"
              >
                <span className="flex items-center gap-2 truncate font-mono text-white/60">
                  <FileText className="h-3.5 w-3.5 shrink-0 text-white/30" />
                  {job.filename}
                </span>
                <span>{job.doc_type}</span>
                <span className="font-mono text-white/45">{job.job_id}</span>
                <span>{job.uploadedAt}</span>
                <span className="flex items-center gap-1 text-[#febc2e]">
                  <CheckCircle2 className="h-3 w-3" /> {job.status}
                </span>
              </div>
            ))}
          </>
        )}
      </div>
    </div>
  );
}
