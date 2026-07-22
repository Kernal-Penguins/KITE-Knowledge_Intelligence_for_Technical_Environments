import { Link } from "react-router-dom";
import { useState } from "react";
import { ChevronDown, Menu, X } from "lucide-react";
import Logo from "./Logo";

const links = [
  { label: "Platform", hasChevron: true },
  { label: "Solutions", hasChevron: false },
  { label: "Docs", hasChevron: false },
];

export default function Navbar() {
  const [open, setOpen] = useState(false);

  return (
    <nav className="animate-fade-down relative z-20">
      <div className="flex items-center justify-between px-5 py-4 sm:px-8 sm:py-5 lg:px-10">
        <a href="#" className="flex items-center gap-2 text-[#E7ECF2]">
          <Logo className="h-5 w-5 sm:h-6 sm:w-6" />
          <span className="text-[15px] font-semibold tracking-tight">KITE</span>
        </a>

        <div className="hidden items-center gap-8 md:flex">
          {links.map((link) => (
            <a
              key={link.label}
              href="#"
              className="flex items-center gap-1 text-[13px] text-[#B7C0CB] transition-colors hover:text-[#E7ECF2]"
            >
              {link.label}
              {link.hasChevron && <ChevronDown className="h-3.5 w-3.5" />}
            </a>
          ))}
        </div>

        <div className="flex items-center gap-2">
          <Link
            to="/app"
            className="rounded-full bg-[#E08A3C] px-4 py-2 text-[13px] font-medium text-[#0B0F14] transition-colors hover:bg-[#EDA45E] sm:px-5"
          >
            Get Started
          </Link>
          <button
            type="button"
            onClick={() => setOpen((v) => !v)}
            aria-label="Toggle menu"
            className="flex h-9 w-9 items-center justify-center rounded-full text-[#E7ECF2] transition-colors hover:bg-white/10 md:hidden"
          >
            {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </button>
        </div>
      </div>

      {open && (
        <div className="animate-fade-up absolute left-4 right-4 top-full rounded-2xl bg-[#12181F]/90 px-5 py-3 ring-1 ring-white/10 backdrop-blur-xl">
          {links.map((link) => (
            <a
              key={link.label}
              href="#"
              className="block border-b border-white/10 py-3 text-[15px] text-[#B7C0CB] last:border-b-0 hover:text-[#E7ECF2]"
            >
              {link.label}
            </a>
          ))}
        </div>
      )}
    </nav>
  );
}
