import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, FileWarning, AlertTriangle } from 'lucide-react';

const RCA = () => {
  const [eqId, setEqId] = useState('');
  const [searchId, setSearchId] = useState('');

  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['rca', searchId],
    queryFn: async () => {
      const res = await fetch(`/api/agents/rca/${searchId}`);
      if (!res.ok) throw new Error("Failed to fetch RCA");
      return res.json();
    },
    enabled: !!searchId
  });

  return (
    <div className="p-8 h-full overflow-y-auto">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <FileWarning className="text-yellow-500" />
            Root Cause Analysis Agent
          </h1>
          <p className="text-gray-400 mt-2">Generate an autonomous RCA report for any equipment tag.</p>
        </div>

        <form onSubmit={e => { e.preventDefault(); setSearchId(eqId); }} className="flex gap-4">
          <input 
            type="text" 
            value={eqId}
            onChange={e => setEqId(e.target.value)}
            placeholder="Enter Equipment ID (e.g. P-101)"
            className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-yellow-500 focus:ring-1 focus:ring-yellow-500"
          />
          <button type="submit" disabled={isLoading || !eqId} className="bg-yellow-600 hover:bg-yellow-500 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 disabled:opacity-50">
            <Search size={18} /> Analyze
          </button>
        </form>

        {isLoading && (
          <div className="animate-pulse bg-gray-900 rounded-xl p-8 border border-gray-800 space-y-4">
            <div className="h-6 bg-gray-800 rounded w-1/4"></div>
            <div className="h-4 bg-gray-800 rounded w-full"></div>
            <div className="h-4 bg-gray-800 rounded w-full"></div>
            <div className="h-4 bg-gray-800 rounded w-3/4"></div>
          </div>
        )}

        {isError && (
          <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-6 text-red-200 flex items-start gap-4">
            <AlertTriangle className="text-red-500 flex-shrink-0" />
            <div>
              <h3 className="font-semibold text-red-400">Analysis Failed</h3>
              <p className="text-sm mt-1">{error.message}</p>
            </div>
          </div>
        )}

        {data && (
          <div className="bg-gray-900 rounded-xl border border-gray-800 shadow-xl overflow-hidden">
            <div className="bg-gray-800 px-6 py-4 border-b border-gray-700 flex justify-between items-center">
              <h2 className="font-bold text-lg text-white">RCA Report: {data.equipment_id}</h2>
              <span className="bg-blue-500/20 text-blue-400 text-xs px-3 py-1 rounded-full font-medium">
                {data.evidence_count} Graph Nodes Analyzed
              </span>
            </div>
            <div className="p-8 prose prose-invert max-w-none">
              <div dangerouslySetInnerHTML={{ __html: data.report.replace(/\n/g, '<br/>') }} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RCA;
