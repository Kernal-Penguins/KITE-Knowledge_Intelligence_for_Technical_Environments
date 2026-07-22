import { useState, type FormEvent } from "react";
import { ArrowRight, Github, Mail, BookOpen } from "lucide-react";
import LandingNavbar from "./LandingNavbar";
import AmbientGraph from "./AmbientGraph";

const REPO_URL = "https://github.com/Kernal-Penguins/KITE-Knowledge_Intelligence_for_Technical_Environments";

function scrollTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
}

export default function HeroSection() {
  const [email, setEmail] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!email.trim() || !email.includes("@")) return;
    // No newsletter endpoint exists on the backend yet -- this gives real
    // feedback locally rather than doing nothing on click.
    setSubmitted(true);
    setEmail("");
  };

  return (
    <div id="hero" className="relative flex min-h-screen flex-col overflow-hidden bg-black">
      <div className="absolute inset-0 h-full w-full object-cover">
        <AmbientGraph />
      </div>
      <div className="absolute inset-0 bg-gradient-to-b from-black/40 via-black/10 to-black" />

      <LandingNavbar />

      <div className="relative z-10 flex flex-1 -translate-y-[10%] flex-col items-center justify-center px-6 py-12 text-center">
        <h1
          className="whitespace-nowrap text-6xl tracking-tight text-white sm:text-7xl md:text-8xl lg:text-9xl"
          style={{ fontFamily: "'Instrument Serif', serif" }}
        >
          Know your plant. <em className="italic">All</em> of it.
        </h1>

        <form
          id="hero-email"
          onSubmit={handleSubmit}
          className="liquid-glass mt-10 flex w-full max-w-xl items-center gap-3 rounded-full py-2 pl-6 pr-2"
        >
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
            className="flex-1 bg-transparent text-white outline-none placeholder:text-white/40"
          />
          <button
            type="submit"
            aria-label="Request early access"
            className="rounded-full bg-white p-3 text-black transition-transform hover:scale-105 active:scale-95"
          >
            <ArrowRight className="h-5 w-5" />
          </button>
        </form>

        <p className="mt-4 max-w-md px-4 text-sm leading-relaxed text-white">
          {submitted
            ? "Thanks -- we'll be in touch when your workspace is ready."
            : "Turn scattered maintenance logs, inspections, and asset data into one living knowledge graph. Get early access to KITE."}
        </p>

        <button
          onClick={() => scrollTo("about")}
          className="liquid-glass mt-8 rounded-full px-8 py-3 text-sm font-medium text-white transition-colors hover:bg-white/5"
        >
          See How It Works
        </button>
      </div>

      <div className="relative z-10 flex justify-center gap-4 pb-12">
        <a
          href={REPO_URL}
          target="_blank"
          rel="noreferrer"
          aria-label="View source on GitHub"
          className="liquid-glass rounded-full p-4 text-white/80 transition-all hover:bg-white/5 hover:text-white"
        >
          <Github className="h-5 w-5" />
        </a>
        <a
          href="mailto:hello@kite.io"
          aria-label="Email KITE"
          className="liquid-glass rounded-full p-4 text-white/80 transition-all hover:bg-white/5 hover:text-white"
        >
          <Mail className="h-5 w-5" />
        </a>
        <button
          onClick={() => scrollTo("capabilities")}
          aria-label="Jump to capabilities"
          className="liquid-glass rounded-full p-4 text-white/80 transition-all hover:bg-white/5 hover:text-white"
        >
          <BookOpen className="h-5 w-5" />
        </button>
      </div>
    </div>
  );
}
