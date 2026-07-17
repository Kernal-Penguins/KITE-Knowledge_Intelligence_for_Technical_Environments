import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { ShieldCheck, XCircle, CheckCircle, AlertTriangle } from 'lucide-react';

const Compliance = () => {
  const { data, isLoading, isError } = useQuery({
    queryKey: ['compliance'],
    queryFn: async () => {
      const res = await fetch(`/api/agents/compliance`);
      if (!res.ok) throw new Error("Failed to fetch Compliance audit");
      return res.json();
    }
  });

  return (
    <div className="p-8 h-full overflow-y-auto">
      <div className="max-w-5xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <ShieldCheck className="text-emerald-500" />
            Compliance Dashboard
          </h1>
          <p className="text-gray-400 mt-2">Real-time audit of all active graph relationships against regulatory rules.</p>
        </div>

        {isLoading && (
          <div className="animate-pulse flex gap-4">
            <div className="flex-1 h-32 bg-gray-900 rounded-xl border border-gray-800"></div>
            <div className="flex-1 h-32 bg-gray-900 rounded-xl border border-gray-800"></div>
          </div>
        )}

        {data && (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gray-900 p-6 rounded-xl border border-gray-800 flex items-center gap-4">
                <div className={`p-4 rounded-full ${data.status === 'passed' ? 'bg-emerald-500/20 text-emerald-500' : 'bg-red-500/20 text-red-500'}`}>
                  {data.status === 'passed' ? <CheckCircle size={32}/> : <AlertTriangle size={32}/>}
                </div>
                <div>
                  <p className="text-gray-400 font-medium">Audit Status</p>
                  <p className={`text-2xl font-bold capitalize ${data.status === 'passed' ? 'text-emerald-500' : 'text-red-500'}`}>
                    {data.status}
                  </p>
                </div>
              </div>
              
              <div className="bg-gray-900 p-6 rounded-xl border border-gray-800 flex items-center gap-4">
                <div className="p-4 rounded-full bg-blue-500/20 text-blue-500">
                  <XCircle size={32}/>
                </div>
                <div>
                  <p className="text-gray-400 font-medium">Total Gaps Found</p>
                  <p className="text-2xl font-bold text-white">{data.total_gaps}</p>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              <h2 className="text-xl font-bold text-white">Rule Violations</h2>
              {Object.entries(data.details).map(([rule, violations]: [string, any]) => (
                <div key={rule} className="bg-gray-900 rounded-xl border border-gray-800 overflow-hidden">
                  <div className="bg-gray-800 px-6 py-4 border-b border-gray-700 flex justify-between items-center">
                    <h3 className="font-semibold text-gray-200 capitalize">{rule.replace(/_/g, ' ')}</h3>
                    <span className="bg-gray-700 text-gray-300 px-3 py-1 text-xs rounded-full">
                      {violations.length} Violations
                    </span>
                  </div>
                  {violations.length > 0 ? (
                    <div className="divide-y divide-gray-800">
                      {violations.map((v: any, i: number) => (
                        <div key={i} className="p-4 px-6 text-sm flex gap-4">
                          <span className="text-red-400 flex-shrink-0"><XCircle size={16}/></span>
                          <span className="text-gray-300 font-mono text-xs bg-gray-800 px-2 py-1 rounded">{Object.values(v)[0] as string}</span>
                          <span className="text-gray-400">{v.gap}</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <div className="p-6 text-center text-emerald-500 text-sm flex items-center justify-center gap-2">
                      <CheckCircle size={16}/> Passed with 0 violations
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default Compliance;
