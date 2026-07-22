import { NavLink, Outlet } from "react-router-dom";
import { LayoutGrid, Upload, Share2, ShieldCheck, MessageSquare, Wrench, Sparkles, Search, Inbox } from "lucide-react";
import Logo from "../components/Logo";
import { useHealth } from "../hooks/useKiteApi";

const navItems = [
  { to: "/app", label: "Overview", icon: LayoutGrid, end: true },
  { to: "/app/ingest", label: "Ingest", icon: Upload },
  { to: "/app/search", label: "Search", icon: Search },
  { to: "/app/copilot", label: "Copilot", icon: MessageSquare },
  { to: "/app/rca", label: "RCA", icon: Wrench },
  { to: "/app/lessons", label: "Lessons-Learned", icon: Sparkles },
  { to: "/app/compliance", label: "Compliance", icon: ShieldCheck },
  { to: "/app/graph", label: "Graph Explorer", icon: Share2 },
  { to: "/app/review", label: "Review Queue", icon: Inbox },
];

export default function AppShell() {
  const { data: health } = useHealth();
  const allOk = health?.status === "ok";

  return (
    <div className="flex min-h-screen bg-[#0B0F14] text-[#E7ECF2]">
      <aside className="flex w-60 shrink-0 flex-col border-r border-white/5 bg-[#0E1319] px-4 py-5">
        <div className="mb-6 flex items-center gap-2 px-1">
          <Logo className="h-5 w-5 text-[#E7ECF2]" />
          <span className="text-[15px] font-semibold tracking-tight">KITE</span>
        </div>

        {/* Workspace badge — driven from env var when set, otherwise generic */}
        <div className="mb-5 flex items-center gap-2 rounded-lg bg-white/[0.03] px-3 py-2 ring-1 ring-white/5">
          <div className="flex h-6 w-6 items-center justify-center rounded bg-[#c1502e] text-[10px] font-semibold">
            K
          </div>
          <div className="min-w-0">
            <div className="truncate text-[12px] font-medium text-white/85">
              {import.meta.env.VITE_WORKSPACE_NAME ?? "My Workspace"}
            </div>
            <div className="text-[10px] text-white/40">Workspace</div>
          </div>
        </div>

        <nav className="flex flex-col gap-1" aria-label="Main navigation">
          {navItems.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              className={({ isActive }) =>
                `flex items-center gap-2.5 rounded-lg px-3 py-2 text-[13px] transition-colors ${
                  isActive
                    ? "bg-white/[0.08] text-white"
                    : "text-white/55 hover:bg-white/[0.04] hover:text-white/85"
                }`
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>

        <div className="mt-auto rounded-lg bg-white/[0.03] px-3 py-2.5 ring-1 ring-white/5">
          <div className="text-[10px] tracking-wider text-white/35">BACKEND STATUS</div>
          <div className="mt-1 text-sm font-medium" style={{ color: allOk ? "#28c840" : "#E08A3C" }}>
            {health ? (allOk ? "All connected" : "Degraded") : "Checking…"}
          </div>
          {!allOk && health && (
            <div className="mt-0.5 text-[10px] text-white/30">
              Some services may be temporarily unavailable.
            </div>
          )}
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-white/5 px-6 py-3.5">
          <div className="text-sm text-white/50">
            {import.meta.env.VITE_WORKSPACE_NAME ?? "My Workspace"}{" "}
            <span className="mx-1.5 text-white/20">/</span>{" "}
            <span className="text-white/80">Knowledge Graph</span>
          </div>
          {/* User avatar — initials from env or generic */}
          <div className="flex h-7 w-7 items-center justify-center rounded-full bg-[#E08A3C] text-[11px] font-semibold text-[#0B0F14]">
            {(import.meta.env.VITE_USER_INITIALS ?? "KT").slice(0, 2).toUpperCase()}
          </div>
        </header>

        <main className="min-w-0 flex-1 overflow-y-auto px-6 py-6">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
