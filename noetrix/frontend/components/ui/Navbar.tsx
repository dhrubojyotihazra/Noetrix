"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ArrowUpRight } from "lucide-react";

export default function Navbar() {
  const pathname = usePathname();
  const [isOpen, setIsOpen] = useState(false);
  const [timeStr, setTimeStr] = useState<string>("");

  // Live ticking clock matching home.full-page.Woblo/home Clock component
  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      setTimeStr(
        now.toLocaleTimeString("en-US", {
          hour: "numeric",
          minute: "2-digit",
          second: "2-digit",
          hour12: true,
        })
      );
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  // Close on route change or Escape
  useEffect(() => {
    setIsOpen(false);
  }, [pathname]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setIsOpen(false);
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  const navLinks = [
    {
      index: "01",
      label: "Candidate Door",
      desc: "Score CV against JD & tailor experience bullets with AI",
      href: "/candidate/analyze",
    },
    {
      index: "02",
      label: "Recruiter Door",
      desc: "Batch shortlist screening & explainable candidate ranking",
      href: "/recruiter/setup",
    },
    {
      index: "03",
      label: "How Scoring Works",
      desc: "6-metric deterministic engine & knockout rules breakdown",
      href: "/how-scoring-works",
    },
    {
      index: "04",
      label: "AI Resume Editor",
      desc: "XYZ bullet re-writer & instant before/after rescore",
      href: "/candidate/editor",
    },
  ];

  return (
    <header className="sticky top-0 z-50 w-full backdrop-blur-md bg-canvas/95">
      {/* Topbar: Balanced logo size + Menu Trigger (Horizontal tab names removed per user request) */}
      <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        {/* Rolled-Back Balanced Brand Logo */}
        <Link href="/" className="group flex items-center gap-3">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            src="/favicon.png"
            alt="Noetrix Logo"
            className="w-10 h-10 sm:w-11 sm:h-11 object-contain transition-transform group-hover:scale-105 shrink-0"
          />
          <div className="flex items-center gap-2">
            <span className="font-display text-3xl uppercase tracking-wider text-ink transition-colors group-hover:text-ink/80">
              NOETRIX
            </span>
            <span className="bg-accent-yellow text-ink text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-widest border border-ink shadow-2xs">
              ATS 1.0
            </span>
          </div>
        </Link>

        {/* Right Actions: Instant CTA + Menu Trigger with burger animation */}
        <div className="flex items-center gap-3.5">
          <Link
            href="/candidate/analyze"
            className="hidden sm:flex items-center gap-2 bg-ink text-canvas font-sans text-xs font-semibold px-5 py-2.5 rounded-full hover:bg-ink-slate transition-all shadow-sm"
          >
            <span>Scan My CV</span>
            <ArrowUpRight className="w-3.5 h-3.5 transition-transform hover:translate-x-0.5 hover:-translate-y-0.5" />
          </Link>

          {/* Menu Trigger Button matching home.full-page.Woblo/home */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="group flex items-center gap-2.5 px-4 py-2 rounded-full border border-ink/30 bg-card-surface/90 hover:bg-card-surface transition-all text-ink focus:outline-none focus:ring-2 focus:ring-ink"
            aria-label={isOpen ? "Close Menu" : "Open Menu"}
          >
            <span className="font-sans text-xs font-bold uppercase tracking-[0.14em]">
              {isOpen ? "Close" : "Menu"}
            </span>

            {/* Animated Burger Lines */}
            <div className="relative w-4 h-3 flex flex-col justify-between">
              <span
                className={`w-full h-[2px] bg-ink rounded-xs transition-transform duration-300 origin-center ${
                  isOpen ? "rotate-45 translate-y-[5px]" : ""
                }`}
              />
              <span
                className={`w-full h-[2px] bg-ink rounded-xs transition-transform duration-300 origin-center ${
                  isOpen ? "-rotate-45 -translate-y-[5px]" : ""
                }`}
              />
            </div>
          </button>
        </div>
      </div>

      {/* Rolling Down Menu Drawer Animation (from home.full-page.Woblo/home) */}
      <div
        className={`w-full overflow-hidden transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] border-b border-ink/15 bg-canvas/98 backdrop-blur-xl ${
          isOpen
            ? "max-h-[85vh] opacity-100 translate-y-0 shadow-2xl"
            : "max-h-0 opacity-0 -translate-y-4 pointer-events-none border-b-0"
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 py-8 sm:py-12 flex flex-col justify-between">
          {/* Numbered Editorial Links */}
          <div className="flex flex-col divide-y divide-ink/15 mb-8">
            {navLinks.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setIsOpen(false)}
                className="group py-5 sm:py-6 flex flex-col sm:flex-row sm:items-baseline justify-between transition-all hover:pl-3"
              >
                <div className="flex items-baseline gap-6 sm:gap-10">
                  <span className="font-mono text-xs sm:text-sm font-bold text-ink/40 tracking-wider">
                    {item.index}
                  </span>
                  <div>
                    <h2 className="font-display text-3xl sm:text-5xl uppercase tracking-tight text-ink group-hover:text-ink/75 transition-colors">
                      {item.label}
                    </h2>
                    <p className="font-sans text-xs sm:text-sm text-ink/60 mt-1 font-medium">
                      {item.desc}
                    </p>
                  </div>
                </div>

                <div className="mt-3 sm:mt-0 flex items-center gap-2 text-ink/40 group-hover:text-ink transition-colors">
                  <span className="font-sans text-xs font-bold uppercase tracking-wider hidden sm:inline">
                    Enter
                  </span>
                  <ArrowUpRight className="w-5 h-5 transition-transform group-hover:translate-x-1 group-hover:-translate-y-1" />
                </div>
              </Link>
            ))}
          </div>

          {/* Meta Footer Row with Live Clock Component */}
          <div className="pt-6 border-t border-ink/15 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs font-sans text-ink/60">
            <div className="flex items-center gap-5">
              <span className="font-semibold text-ink">engine@noetrix.ai</span>
              <span>•</span>
              <span>100% Ephemeral Sessions</span>
            </div>

            <div className="flex items-center gap-5">
              <span>Zero Stored Data</span>
              <span>•</span>
              <span>Deterministic ATS Scoring</span>
            </div>

            {/* Real-Time Live Clock */}
            <div className="flex items-center gap-2 font-mono text-ink tracking-wider bg-card-surface px-4 py-1.5 rounded-full border border-ink/15 shadow-2xs">
              <span className="w-2 h-2 rounded-full bg-accent-emerald animate-pulse" />
              <span className="font-bold tabular-nums">{timeStr || "9:35:00 PM"}</span>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
