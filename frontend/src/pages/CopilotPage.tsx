import { useState } from "react";
import { Send, Loader2, AlertTriangle, BookOpen } from "lucide-react";
import { useCopilotQuery } from "../hooks/useKiteApi";
import ResultViewer from "../components/ResultViewer";

interface Exchange {
  query: string;
  answer: string;
  confidence: number;
  citations: Record<string, unknown>;
}

export default function CopilotPage() {
  const [input, setInput] = useState("");
  const [history, setHistory] = useState<Exchange[]>([]);
  const copilot = useCopilotQuery();

  const submit = () => {
    const q = input.trim();
    if (!q) return;
    copilot.mutate(q, {
      onSuccess: (data) => {
        setHistory((prev) => [{ query: q, ...data }, ...prev]);
        setInput("");
      },
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-medium text-white">Copilot</h1>
        <p className="text-sm text-white/45">
          Grounded GraphRAG Q&amp;A -- posts to <code className="text-white/70">/api/v1/query</code>.
        </p>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          submit();
        }}
        className="flex items-center gap-3 rounded-full bg-white/[0.05] py-1.5 pl-5 pr-1.5 ring-1 ring-white/10"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about an asset, failure, or inspection..."
          className="flex-1 bg-transparent py-2 text-sm text-white outline-none placeholder-white/35"
        />
        <button
          type="submit"
          disabled={copilot.isPending}
          className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#E08A3C] text-[#0B0F14] hover:bg-[#EDA45E] disabled:opacity-50"
        >
          {copilot.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </button>
      </form>

      {copilot.isError && (
        <div className="flex items-center gap-2 rounded-lg bg-[#E08A3C]/10 px-4 py-3 text-sm text-[#E08A3C] ring-1 ring-[#E08A3C]/20">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          Query failed: {copilot.error instanceof Error ? copilot.error.message : "unknown error"}
        </div>
      )}

      <div className="space-y-4">
        {history.length === 0 && !copilot.isPending && (
          <p className="text-sm text-white/30">Ask a question to see a grounded answer with citations.</p>
        )}
        {history.map((ex, i) => (
          <div key={i} className="rounded-lg bg-white/[0.03] px-4 py-3.5 ring-1 ring-white/5">
            <div className="text-[12px] text-white/45">You asked</div>
            <div className="mb-3 text-[13px] text-white/85">{ex.query}</div>
            <div className="text-[12px] text-white/45">Answer</div>
            <div className="mb-3 text-[13.5px] leading-relaxed text-white/90">{ex.answer}</div>
            <div className="mb-2 flex items-center gap-2 text-[11px] text-white/40">
              <span className="rounded-full bg-white/[0.06] px-2 py-0.5">
                confidence {Math.round(ex.confidence * 100)}%
              </span>
            </div>
            {ex.citations && Object.keys(ex.citations).length > 0 && (
              <div>
                <div className="mb-1 flex items-center gap-1.5 text-[10px] tracking-wider text-white/30">
                  <BookOpen className="h-3 w-3" /> CITATIONS
                </div>
                <ResultViewer data={ex.citations} />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
