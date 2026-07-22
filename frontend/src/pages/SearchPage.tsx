import { useState } from "react";
import { Search as SearchIcon, Loader2, AlertTriangle, BookOpen } from "lucide-react";
import { useCopilotQuery } from "../hooks/useKiteApi";
import ResultViewer from "../components/ResultViewer";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [submitted, setSubmitted] = useState<string | null>(null);
  const search = useCopilotQuery();

  const handleSubmit = () => {
    const q = query.trim();
    if (!q || search.isPending) return;
    setSubmitted(q);
    search.mutate(q);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-medium text-white">Search</h1>
        <p className="text-sm text-white/45">
          Upload documents and ask technical questions. Results are grounded in your knowledge graph.
        </p>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSubmit();
        }}
        className="flex items-center gap-3 rounded-full bg-white/[0.05] py-1.5 pl-5 pr-1.5 ring-1 ring-white/10"
      >
        <SearchIcon className="h-4 w-4 shrink-0 text-white/40" aria-hidden="true" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="e.g. pump seal leak, inspection overdue on V-205"
          aria-label="Search query"
          className="flex-1 bg-transparent py-2 text-sm text-white outline-none placeholder-white/35"
        />
        <button
          type="submit"
          disabled={search.isPending || !query.trim()}
          className="shrink-0 rounded-full bg-[#E08A3C] px-4 py-2 text-[12px] font-medium text-[#0B0F14] hover:bg-[#EDA45E] disabled:opacity-50"
        >
          {search.isPending ? "Searching…" : "Search"}
        </button>
      </form>

      {search.isPending && (
        <div className="flex items-center gap-2 text-sm text-white/40" role="status">
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" />
          Searching your documents…
        </div>
      )}

      {search.isError && (
        <div className="flex items-center gap-2 rounded-lg bg-[#E08A3C]/10 px-4 py-3 text-sm text-[#E08A3C] ring-1 ring-[#E08A3C]/20">
          <AlertTriangle className="h-4 w-4 shrink-0" aria-hidden="true" />
          Search unavailable right now. Please try again shortly.
        </div>
      )}

      {!submitted && !search.isPending && (
        <div className="rounded-lg bg-white/[0.03] px-4 py-6 text-center ring-1 ring-white/5">
          <p className="text-sm text-white/45">
            Enter a question about equipment, failures, procedures, or inspections.
          </p>
          <p className="mt-1 text-[12px] text-white/30">
            Upload documents from the Ingest page first to populate searchable content.
          </p>
        </div>
      )}

      {search.data && submitted && (
        <div className="rounded-lg bg-white/[0.03] px-4 py-3.5 ring-1 ring-white/5">
          <div className="text-[12px] text-white/45">Query</div>
          <div className="mb-3 text-[13px] text-white/85">{submitted}</div>
          <div className="text-[12px] text-white/45">Answer</div>
          <div className="mb-3 text-[13.5px] leading-relaxed text-white/90">{search.data.answer}</div>
          <div className="mb-2 flex items-center gap-2 text-[11px] text-white/40">
            <span className="rounded-full bg-white/[0.06] px-2 py-0.5">
              confidence {Math.round(search.data.confidence * 100)}%
            </span>
          </div>
          {search.data.citations && Object.keys(search.data.citations).length > 0 && (
            <div>
              <div className="mb-1 flex items-center gap-1.5 text-[10px] tracking-wider text-white/30">
                <BookOpen className="h-3 w-3" aria-hidden="true" /> SOURCES
              </div>
              <ResultViewer data={search.data.citations} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}
