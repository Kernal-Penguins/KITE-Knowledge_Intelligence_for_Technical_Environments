import React from 'react';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { Bot, FileWarning, ShieldCheck, BookOpen, Settings } from 'lucide-react';
import Copilot from './pages/Copilot';
import RCA from './pages/RCA';
import Compliance from './pages/Compliance';
import Lessons from './pages/Lessons';
import Admin from './pages/Admin';

const App = () => {
  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-950 text-gray-100 font-sans dark">
        {/* Sidebar */}
        <div className="w-16 md:w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
          <div className="p-4 flex items-center justify-center md:justify-start border-b border-gray-800">
            <Bot className="w-8 h-8 text-blue-500" />
            <span className="hidden md:block ml-3 font-bold text-xl tracking-tight text-white">KITE</span>
          </div>
          <nav className="flex-1 overflow-y-auto py-4">
            <ul className="space-y-2 px-2">
              <NavItem to="/" icon={<Bot />} label="Copilot" />
              <NavItem to="/rca" icon={<FileWarning />} label="RCA Agent" />
              <NavItem to="/compliance" icon={<ShieldCheck />} label="Compliance" />
              <NavItem to="/lessons" icon={<BookOpen />} label="Lessons" />
            </ul>
          </nav>
          <div className="p-4 border-t border-gray-800">
            <NavItem to="/admin" icon={<Settings />} label="Admin" />
          </div>
        </div>

        {/* Main Content */}
        <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
          <Routes>
            <Route path="/" element={<Copilot />} />
            <Route path="/rca" element={<RCA />} />
            <Route path="/compliance" element={<Compliance />} />
            <Route path="/lessons" element={<Lessons />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
};

const NavItem = ({ to, icon, label }: { to: string; icon: React.ReactNode; label: string }) => (
  <li>
    <Link
      to={to}
      className="flex items-center px-3 py-2.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors group"
    >
      <span className="flex items-center justify-center w-6 h-6">{icon}</span>
      <span className="hidden md:block ml-3 font-medium">{label}</span>
    </Link>
  </li>
);

export default App;
