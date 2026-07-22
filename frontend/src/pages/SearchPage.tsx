import { useMemo, useState } from "react";
import { Search as SearchIcon, Network } from "lucide-react";
import { documents, equipment, relationships } from "../data/mockData";

function connectedTags(equipmentId: string) {
  const ids = relationships
    .filter((r) => r.from === equipmentId || r.to === equipmentId)
    .map((r) => (r.from === equipmentId ? r.to : r.from))
    .filter((id) => id.startsWith("eq-"));
  return equipment.filter((e) => ids.includes(e.id)).map((e) => e.tag);
}

export default function SearchPage() {
  const [query, setQuery] = useState("pump seal leak");
  const [submitted, setSubmitted] = useState("pump seal leak");

  const results = useMemo(() => {
    const q = submitted.trim().toLowerCase();
    if (!q) return [];
    return documents
      .map((doc) => {
        const haystack = `${doc.filename} ${doc.docType} ${doc.preview}`.toLowerCase();
        const score = q
          .split(/\s+/)
          .reduce((acc, term) => acc + (haystack.includes(term) ? 1 : 0), 0) / q.split(/\s+/).length;
        return { doc, score };
      })
      .filter((r) => r.score > 0)
      .sort((a, b) => b.score - a.score);
  }, [submitted]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-medium text-white">Search</h1>
        <p className="text-sm text-white/45">
          Semantic search over ingested documents, grounded with live graph context.
        </p>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          setSubmitted(query);
        }}
        className="flex items-center gap-3 rounded-full bg-white/[0.05] py-1.5 pl-5 pr-1.5 ring-1 ring-white/10"
      >
        <SearchIcon className="h-4 w-4 shrink-0 text-white/40" />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask anything about your plant's assets or history..."
          className="flex-1 bg-transparent py-2 text-sm text-white outline-none placeholder-white/35"
        />
        <button
          type="submit"
          className="shrink-0 rounded-full bg-[#E08A3C] px-4 py-2 text-[12px] font-medium text-[#0B0F14] hover:bg-[#EDA45E]"
        >
          Search
        </button>
      </form>

      <div className="space-y-3">
        {results.length === 0 && (
          <p className="text-sm text-white/35">No matches -- try mentioning an equipment tag or a document type.</p>
        )}
        {results.map(({ doc, score }) => (
          <div key={doc.id} className="rounded-lg bg-white/[0.03] px-4 py-3.5 ring-1 ring-white/5">
            <div className="flex items-center justify-between">
              <span className="font-mono text-[12.5px] text-white/85">{doc.filename}</span>
              <span className="text-[10px] text-white/35">match {Math.round(score * 100)}%</span>
            </div>
            <pre className="mt-2 whitespace-pre-wrap font-mono text-[11.5px] leading-relaxed text-white/60">
              {doc.preview}
            </pre>
            <div className="mt-3 flex flex-wrap items-center gap-1.5">
              <Network className="h-3 w-3 text-[#4FD1C5]" />
              {doc.linkedEquipment.map((eqId) => {
                const eq = equipment.find((e) => e.id === eqId);
                if (!eq) return null;
                const related = connectedTags(eqId);
                return (
                  <span key={eqId} className="flex items-center gap-1 rounded-full bg-white/[0.05] px-2.5 py-1 text-[10px] text-white/60">
                    {eq.tag} &middot; {eq.status}
                    {related.length > 0 && <span className="text-white/35">&rarr; {related.join(", ")}</span>}
                  </span>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
