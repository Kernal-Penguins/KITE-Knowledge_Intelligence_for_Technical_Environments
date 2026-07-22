import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import AmbientGraph from "./AmbientGraph";

export default function FeaturedSection() {
  return (
    <section className="overflow-hidden bg-black px-6 pb-20 pt-6 md:pb-32 md:pt-10">
      <motion.div
        initial={{ opacity: 0, y: 60 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: "-100px" }}
        transition={{ duration: 0.9 }}
        className="relative mx-auto aspect-video max-w-6xl overflow-hidden rounded-3xl bg-white/[0.02]"
      >
        <AmbientGraph className="opacity-80" />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />

        <div className="absolute bottom-0 left-0 right-0 flex flex-col gap-4 p-6 md:flex-row md:items-end md:justify-between md:p-10">
          <div className="liquid-glass max-w-md rounded-2xl p-6 md:p-8">
            <div className="mb-3 text-xs uppercase tracking-widest text-white/50">Our Approach</div>
            <p className="text-sm leading-relaxed text-white md:text-base">
              Every document, sensor reading, and work order becomes a node in one graph. Docling parses it,
              embeddings connect it, and GraphRAG lets you ask it questions in plain language.
            </p>
          </div>

          <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
            <Link
              to="/app/graph"
              className="liquid-glass block rounded-full px-8 py-3 text-sm font-medium text-white"
            >
              Explore the Graph
            </Link>
          </motion.div>
        </div>
      </motion.div>
    </section>
  );
}
