import { motion } from "framer-motion";
import AmbientGraph from "./AmbientGraph";

export default function PhilosophySection() {
  return (
    <section id="philosophy" className="overflow-hidden bg-black px-6 py-28 md:py-40">
      <div className="mx-auto max-w-6xl">
        <motion.h2
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.8 }}
          className="mb-16 text-5xl tracking-tight text-white md:mb-24 md:text-7xl lg:text-8xl"
        >
          Signal{" "}
          <span className="italic text-white/40" style={{ fontFamily: "'Instrument Serif', serif" }}>
            x
          </span>{" "}
          Structure
        </motion.h2>

        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 md:gap-12">
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8 }}
            className="aspect-[4/3] overflow-hidden rounded-3xl bg-white/[0.02]"
          >
            <AmbientGraph dim />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true, margin: "-100px" }}
            transition={{ duration: 0.8 }}
            className="flex flex-col justify-center gap-8"
          >
            <div>
              <div className="mb-4 text-xs uppercase tracking-widest text-white/40">
                Every document becomes evidence
              </div>
              <p className="text-base leading-relaxed text-white/70 md:text-lg">
                Maintenance logs, inspection reports, and asset exports get parsed by docling, embedded, and linked
                into the graph automatically -- no manual tagging, no spreadsheets to maintain by hand.
              </p>
            </div>

            <div className="h-px w-full bg-white/10" />

            <div>
              <div className="mb-4 text-xs uppercase tracking-widest text-white/40">Every gap becomes visible</div>
              <p className="text-base leading-relaxed text-white/70 md:text-lg">
                Root cause analysis, lessons-learned clustering, and compliance auditing run directly against that
                graph -- so patterns and gaps surface before they become incidents.
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
