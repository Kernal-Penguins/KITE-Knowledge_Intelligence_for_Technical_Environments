import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { ArrowUpRight, Upload, MessageSquare, Wrench, Sparkles, ShieldCheck } from "lucide-react";

const capabilities = [
  {
    to: "/app/ingest",
    tag: "Ingestion",
    title: "Parse Any Document",
    description:
      "Maintenance logs, inspection reports, P&IDs, and asset exports -- docling parses each into structured markdown before entity extraction.",
    icon: Upload,
    gradient: "from-[#2a2a2a] to-black",
  },
  {
    to: "/app/copilot",
    tag: "Copilot",
    title: "Ask Your Graph",
    description:
      "A grounded GraphRAG assistant that answers plain-language questions about your assets, citing exactly where each answer came from.",
    icon: MessageSquare,
    gradient: "from-[#232323] to-black",
  },
  {
    to: "/app/rca",
    tag: "Diagnostics",
    title: "Root Cause Analysis",
    description:
      "Traverses an asset's graph context -- failures, inspections, incidents, procedures -- and generates a structured RCA report.",
    icon: Wrench,
    gradient: "from-[#262626] to-black",
  },
  {
    to: "/app/lessons",
    tag: "Pattern Recognition",
    title: "Lessons-Learned Clustering",
    description:
      "Embeds every failure description and links similar failure modes across the plant, so recurring patterns stop hiding in plain sight.",
    icon: Sparkles,
    gradient: "from-[#242424] to-black",
  },
  {
    to: "/app/compliance",
    tag: "Governance",
    title: "Compliance Auditing",
    description:
      "Five deterministic rules run against the graph continuously -- missed inspections, uncertified work, unresolved failures, and more.",
    icon: ShieldCheck,
    gradient: "from-[#282828] to-black",
  },
];

export default function CapabilitiesSection() {
  return (
    <section id="capabilities" className="relative overflow-hidden bg-black px-6 py-28 md:py-40">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(ellipse_at_center,_rgba(255,255,255,0.02)_0%,_transparent_60%)]" />

      <div className="relative mx-auto max-w-6xl">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7 }}
          className="mb-12 flex items-end justify-between md:mb-16"
        >
          <h2 className="text-3xl tracking-tight text-white md:text-5xl">What KITE does</h2>
          <span className="hidden text-sm text-white/40 md:inline">Core capabilities</span>
        </motion.div>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 md:gap-8 lg:grid-cols-3">
          {capabilities.map((cap, i) => (
            <motion.div
              key={cap.to}
              initial={{ opacity: 0, y: 50 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{ duration: 0.8, delay: i * 0.15 }}
            >
              <Link to={cap.to} className="liquid-glass group block overflow-hidden rounded-3xl">
                <div className={`relative flex aspect-video items-center justify-center bg-gradient-to-br ${cap.gradient}`}>
                  <cap.icon className="h-10 w-10 text-white/60 transition-transform duration-700 group-hover:scale-110" />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/40 to-transparent" />
                </div>
                <div className="p-6 md:p-8">
                  <div className="mb-4 flex items-center justify-between">
                    <span className="text-xs uppercase tracking-widest text-white/40">{cap.tag}</span>
                    <span className="liquid-glass rounded-full p-2">
                      <ArrowUpRight className="h-4 w-4 text-white" />
                    </span>
                  </div>
                  <h3 className="mb-3 text-xl tracking-tight text-white md:text-2xl">{cap.title}</h3>
                  <p className="text-sm leading-relaxed text-white/50">{cap.description}</p>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}
