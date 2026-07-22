import { ArrowUp, Network } from "lucide-react";
import { Link } from "react-router-dom";
import Navbar from "./Navbar";
import GraphBackground from "./GraphBackground";
import ScaledDashboard from "./ScaledDashboard";
import DashboardMockup from "./DashboardMockup";

export default function Hero() {
  return (
    <section className="relative flex min-h-[100svh] flex-col overflow-hidden">
      <GraphBackground />

      <div className="relative z-20">
        <Navbar />
      </div>

      <div className="relative z-20 shrink-0 flex-1 min-h-8 sm:min-h-12 lg:min-h-16" />

      <div className="relative z-20 px-5 text-center">
        <h1 className="font-normal leading-[1.05] tracking-tight text-[#E7ECF2]">
          <span className="block animate-fade-up text-[40px] min-[400px]:text-[44px] sm:text-6xl lg:text-7xl xl:text-[80px]">
            Map every asset.
          </span>
          <span className="block animate-fade-up text-[40px] min-[400px]:text-[44px] sm:text-6xl lg:text-7xl xl:text-[80px] [animation-delay:100ms]">
            Instantly connected.
          </span>
        </h1>

        <form
          className="animate-fade-up [animation-delay:220ms] mx-auto mt-5 w-full max-w-xl sm:mt-6"
          onSubmit={(e) => e.preventDefault()}
        >
          <div className="flex items-center gap-3 rounded-full bg-white/[0.06] py-1.5 pl-5 pr-1.5 ring-1 ring-white/10 backdrop-blur-md">
            <input
              type="text"
              placeholder="How does Pump-204 connect to Valve-17?"
              className="flex-1 bg-transparent py-2 text-sm text-[#E7ECF2] outline-none placeholder-[#7C8894] sm:text-base"
            />
            <button
              type="submit"
              aria-label="Query the graph"
              className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#E08A3C] text-[#0B0F14] transition-transform hover:scale-105 active:scale-95 sm:h-10 sm:w-10"
            >
              <ArrowUp className="h-4 w-4 sm:h-[18px] sm:w-[18px]" />
            </button>
          </div>
        </form>

        <p className="animate-fade-up [animation-delay:340ms] mx-auto mt-4 max-w-md text-sm leading-relaxed text-[#9AA5B1] sm:mt-5 sm:text-base lg:text-lg">
          Turn scattered plant data into one living graph
          <br />
          -- and see how every <Network className="-mt-1 inline h-4 w-4 text-[#4FD1C5]" /> asset connects.
        </p>

        <div className="animate-fade-up [animation-delay:460ms] mt-4 flex flex-wrap items-center justify-center gap-3 sm:mt-5">
          <Link
            to="/app"
            className="rounded-full bg-[#E08A3C] px-6 py-2.5 text-sm font-medium text-[#0B0F14] transition-all hover:bg-[#EDA45E] hover:shadow-lg"
          >
            Start Free Trial
          </Link>
          <a
            href="#"
            className="rounded-full px-6 py-2.5 text-sm font-medium text-[#E7ECF2] ring-1 ring-white/15 transition-colors hover:bg-white/10"
          >
            Talk to an Engineer
          </a>
        </div>
      </div>

      <div className="relative z-20 shrink-0 flex-1 min-h-10 sm:min-h-12 lg:min-h-16" />

      <div className="animate-hero-rise relative z-10 -mb-10 mx-auto w-[92%] max-w-4xl shrink-0 sm:-mb-20 sm:w-[84%] lg:-mb-32 lg:w-[72%] [animation-delay:620ms]">
        <ScaledDashboard>
          <DashboardMockup />
        </ScaledDashboard>
      </div>
    </section>
  );
}
