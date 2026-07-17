import React, { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Send, Bot, User } from 'lucide-react';

const Copilot = () => {
  const [messages, setMessages] = useState<{role: 'user' | 'assistant', text: string, citations?: any}[]>([
    { role: 'assistant', text: "Hello! I am KITE. I can answer questions about your industrial equipment using the Knowledge Graph. Ask me anything!" }
  ]);
  const [input, setInput] = useState('');

  const mutation = useMutation({
    mutationFn: async (query: string) => {
      const res = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      });
      if (!res.ok) throw new Error("Failed to fetch");
      return res.json();
    },
    onSuccess: (data) => {
      setMessages(prev => [...prev, { role: 'assistant', text: data.answer, citations: data.citations }]);
    },
    onError: (err) => {
      setMessages(prev => [...prev, { role: 'assistant', text: "Error: " + err.message }]);
    }
  });

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    setMessages(prev => [...prev, { role: 'user', text: input }]);
    mutation.mutate(input);
    setInput('');
  };

  return (
    <div className="flex flex-col h-full bg-gray-950">
      <div className="p-4 border-b border-gray-800 bg-gray-900 shadow-sm flex items-center justify-between">
        <h1 className="text-xl font-semibold text-white">Copilot</h1>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex max-w-[80%] ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${msg.role === 'user' ? 'bg-blue-600 ml-3' : 'bg-gray-800 mr-3'}`}>
                {msg.role === 'user' ? <User size={16} className="text-white"/> : <Bot size={16} className="text-blue-400"/>}
              </div>
              <div className={`p-4 rounded-2xl ${msg.role === 'user' ? 'bg-blue-600 text-white rounded-tr-sm' : 'bg-gray-800 text-gray-100 rounded-tl-sm border border-gray-700 shadow-sm'}`}>
                <p className="whitespace-pre-wrap">{msg.text}</p>
                {msg.citations && (
                  <div className="mt-4 pt-3 border-t border-gray-700 text-xs text-gray-400">
                    <p className="font-semibold text-gray-300 mb-1">Context Leveraged:</p>
                    <p>{msg.citations.docs?.length || 0} Documents</p>
                    <p>{msg.citations.graph_paths?.length || 0} Graph Edges</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
        {mutation.isPending && (
          <div className="flex justify-start">
             <div className="flex max-w-[80%] flex-row">
                <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-800 mr-3 flex items-center justify-center">
                  <Bot size={16} className="text-blue-400 animate-pulse"/>
                </div>
                <div className="p-4 rounded-2xl bg-gray-800 text-gray-400 rounded-tl-sm border border-gray-700 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-blue-500 animate-bounce"></span>
                  <span className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{animationDelay: '0.2s'}}></span>
                  <span className="w-2 h-2 rounded-full bg-blue-500 animate-bounce" style={{animationDelay: '0.4s'}}></span>
                </div>
             </div>
          </div>
        )}
      </div>

      <div className="p-4 bg-gray-900 border-t border-gray-800">
        <form onSubmit={handleSend} className="max-w-4xl mx-auto relative flex items-center">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            disabled={mutation.isPending}
            placeholder="Ask a question..."
            className="w-full bg-gray-950 border border-gray-700 text-gray-100 rounded-full pl-6 pr-14 py-4 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all shadow-inner"
          />
          <button 
            type="submit" 
            disabled={mutation.isPending || !input.trim()}
            className="absolute right-2 p-2 bg-blue-600 text-white rounded-full hover:bg-blue-500 disabled:opacity-50 transition-colors"
          >
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
};

export default Copilot;
