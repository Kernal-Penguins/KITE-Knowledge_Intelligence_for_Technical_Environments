import { Link } from "react-router-dom";
import Logo from "../Logo";

const navLinks = [
  { label: "Features", href: "#capabilities" },
  { label: "Philosophy", href: "#philosophy" },
  { label: "About", href: "#about" },
];

function scrollTo(id: string) {
  document.getElementById(id)?.scrollIntoView({ behavior: "smooth" });
}

export default function LandingNavbar() {
  return (
    <div className="relative z-20 px-6 py-6">
      <nav className="liquid-glass mx-auto flex max-w-5xl items-center justify-between rounded-full px-6 py-3">
        <div className="flex items-center gap-2">
          <Logo className="h-6 w-6 text-white" />
          <span className="text-lg font-semibold text-white">KITE</span>
          <div className="ml-8 hidden gap-8 md:flex">
            {navLinks.map((link) => (
              <button
                key={link.label}
                onClick={() => scrollTo(link.href.slice(1))}
                className="text-sm font-medium text-white/80 transition-colors hover:text-white"
              >
                {link.label}
              </button>
            ))}
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={() => scrollTo("hero-email")}
            className="text-sm font-medium text-white transition-opacity hover:opacity-80"
          >
            Sign Up
          </button>
          <Link
            to="/app"
            className="liquid-glass rounded-full px-6 py-2 text-sm font-medium text-white transition-colors hover:bg-white/5"
          >
            Login
          </Link>
        </div>
      </nav>
    </div>
  );
}
