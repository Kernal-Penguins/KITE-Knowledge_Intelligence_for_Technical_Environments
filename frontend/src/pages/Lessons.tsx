import { useMutation } from '@tanstack/react-query';
import { BookOpen, RefreshCw, Network } from 'lucide-react';

const Lessons = () => {
  const mutation = useMutation({
    mutationFn: async () => {
      const res = await fetch('/api/agents/lessons/cluster', { method: 'POST' });
      if (!res.ok) throw new Error("Failed to run clustering");
      return res.json();
    }
  });

  return (
    <div className="p-8 h-full overflow-y-auto">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <BookOpen className="text-purple-500" />
            Lessons Learned Agent
          </h1>
          <p className="text-gray-400 mt-2">Asynchronous batch clustering of historical failures to discover SIMILAR_FAILURE_MODE patterns.</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center">
          <Network className="w-16 h-16 text-gray-700 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">Run Clustering Job</h2>
          <p className="text-gray-400 mb-6 max-w-lg mx-auto">
            This will trigger a deep embedding analysis across all failures in the Knowledge Graph and forge new edges where similarity exceeds 85%.
          </p>
          
          <button 
            onClick={() => mutation.mutate()}
            disabled={mutation.isPending}
            className="bg-purple-600 hover:bg-purple-500 text-white px-8 py-3 rounded-lg font-medium flex items-center gap-2 mx-auto disabled:opacity-50 transition-colors"
          >
            {mutation.isPending ? <RefreshCw className="animate-spin" /> : <Network />}
            {mutation.isPending ? 'Clustering...' : 'Execute Clustering'}
          </button>
        </div>

        {mutation.isError && (
          <div className="bg-red-900/20 border border-red-500/50 rounded-xl p-6 text-red-200">
            Error: {mutation.error.message}
          </div>
        )}

        {mutation.isSuccess && (
          <div className="bg-emerald-900/20 border border-emerald-500/50 rounded-xl p-6 text-emerald-200">
            <h3 className="font-semibold text-emerald-400 mb-2">Clustering Complete!</h3>
            <ul className="space-y-1 text-sm">
              <li>Processed Failures: {mutation.data.processed_failures}</li>
              <li>Similarity Threshold: {mutation.data.similarity_threshold}</li>
              <li><strong className="text-emerald-300">New Graph Edges Created: {mutation.data.new_relationships_created}</strong></li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default Lessons;
