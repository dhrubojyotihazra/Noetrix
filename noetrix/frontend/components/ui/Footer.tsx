import Link from "next/link";
import { ShieldCheck, Sparkles, RefreshCw } from "lucide-react";

export default function Footer() {
  return (
    <footer className="w-full bg-ink text-canvas border-t-2 border-ink pt-14 sm:pt-16 pb-8 px-6">
      <div className="max-w-7xl mx-auto flex flex-col lg:flex-row justify-between items-start gap-10">
        <div>
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-accent-yellow flex items-center justify-center shrink-0 shadow-md border border-ink">
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src="/favicon.png" alt="Noetrix Logo" className="w-8 h-8 sm:w-9 sm:h-9 object-contain select-none" />
            </div>
            <span className="font-display text-4xl sm:text-5xl uppercase tracking-wider text-canvas">
              NOETRIX
            </span>
          </div>
          <p className="mt-4 sm:mt-5 font-sans text-sm text-canvas/85 max-w-md leading-relaxed font-normal">
            Check a CV against a job description, or rank a batch of CVs. Every score comes with its reasons.
          </p>
        </div>

        {/* Ephemeral badges */}
        <div className="flex flex-col sm:flex-row gap-4 sm:gap-5 font-sans text-xs text-canvas/90">
          <div className="flex items-center gap-2 border border-canvas/25 px-3.5 py-2 rounded-full">
            <ShieldCheck className="w-4 h-4 text-accent-yellow" />
            <span>Nothing is saved</span>
          </div>
          <div className="flex items-center gap-2 border border-canvas/25 px-3.5 py-2 rounded-full">
            <RefreshCw className="w-4 h-4 text-accent-lilac" />
            <span>Reload the page to clear your data</span>
          </div>
          <div className="flex items-center gap-2 border border-canvas/25 px-3.5 py-2 rounded-full">
            <Sparkles className="w-4 h-4 text-accent-coral" />
            <span>A person makes the final call</span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto mt-12 pt-6 border-t border-canvas/15 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 text-xs sm:text-sm text-canvas/75">
        <div className="flex flex-col gap-1.5">
          <p>© 2026 Noetrix. A capstone project.</p>
          <p className="text-[11px] sm:text-xs text-canvas/60">
            ATS simulation. Scores are estimates, not what any real hiring system would output.
          </p>
        </div>
        <div className="flex flex-wrap gap-6 font-medium">
          <Link href="/how-scoring-works" className="text-canvas/80 hover:text-accent-yellow transition-colors hover:underline">
            How scoring works
          </Link>
          <Link href="/candidate/analyze" className="text-canvas/80 hover:text-accent-yellow transition-colors hover:underline">
            Scan my CV
          </Link>
          <Link href="/recruiter/setup" className="text-canvas/80 hover:text-accent-yellow transition-colors hover:underline">
            Rank candidates
          </Link>
        </div>
      </div>
    </footer>
  );
}
