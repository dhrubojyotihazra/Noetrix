"use client";

import { useState } from "react";
import Link from "next/link";
import { ArrowRight, Plus, Minus } from "lucide-react";

interface WorkflowStep {
  number: string;
  title: string;
  summary: string;
  details: string;
}

const RECRUITER_STEPS: WorkflowStep[] = [
  {
    number: "01",
    title: "Configure custom scoring rubric",
    summary: "Set custom weights across 6 metrics and define mandatory soft-knockout skills for the role.",
    details: "Adjust sliders for keywords, semantic similarity, experience, education, section completeness, and impact metrics. Weights auto-normalize to 100%. Set knockout thresholds that cap missing must-haves at 50/100."
  },
  {
    number: "02",
    title: "Batch upload up to 50 resumes",
    summary: "Drop candidate resumes in PDF, DOCX, or TXT format for parallel structure extraction.",
    details: "High-throughput ephemeral ingestion pipeline parses text, isolates contact headers, extracts experience sections, and normalizes skill tokens across the entire batch in seconds."
  },
  {
    number: "03",
    title: "Automated 6-metric deterministic audit",
    summary: "Every candidate is scored through transparent rules without black-box hallucinations.",
    details: "Runs exact token placement weighting, sentence-transformer MiniLM embeddings, strict degree tier mapping, and 10 quantifiable impact regex patterns without probabilistic drift."
  },
  {
    number: "04",
    title: "Live leaderboard with dynamic sliders",
    summary: "Re-rank candidates instantaneously by shifting priority weights on the active leaderboard.",
    details: "Client-side and backend recalculation shifts candidate positions in real time without re-uploading files, letting recruiting teams test different talent priorities with zero delay."
  },
  {
    number: "05",
    title: "Inspect candidate cards & evidence",
    summary: "Drill down into any applicant to see line-by-line keyword matches, detected metrics, and parse fidelity.",
    details: "View exact matched bullet excerpts, missing mandatory skill warnings, education domain tier alignment, and full raw plaintext parser output with itemized evidence."
  },
  {
    number: "06",
    title: "Triage statuses & export audit CSV",
    summary: "Mark candidates as Shortlist, Hold, or Reject, then download a comprehensive hiring ledger.",
    details: "Generate an audit-ready CSV with individual metric scores, knockout flags, and candidate rankings for compliance and hiring committees. 100% ephemeral zero-retention session."
  }
];

export default function RecruiterWorkflow() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleStep = (idx: number) => {
    setOpenIndex((current) => (current === idx ? null : idx));
  };

  return (
    <section className="bg-canvas text-ink py-24 sm:py-32 px-6 border-t-2 border-ink relative">
      <div className="max-w-7xl mx-auto">
        {/* Section Header: Left Display Title + Right Link (Matching Seamful Image 2) */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-12 sm:mb-16">
          <div>
            <span className="font-sans text-xs sm:text-sm font-bold uppercase tracking-widest text-ink/60 block mb-2">
              THE RECRUITER SUITE
            </span>
            <h2 className="font-display text-5xl sm:text-7xl lg:text-8xl uppercase tracking-tight text-ink leading-none">
              SIX STEPS, IN FULL
            </h2>
          </div>

          <Link
            href="/recruiter/setup"
            className="inline-flex items-center gap-2 font-sans font-bold text-sm sm:text-base text-ink hover:underline tracking-tight pb-1"
          >
            <span>Open recruiter suite</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {/* 6-Row Table / Accordion (Matching Seamful Image 2) */}
        <div className="border-t border-ink/20">
          {RECRUITER_STEPS.map((step, idx) => {
            const isOpen = openIndex === idx;

            return (
              <div
                key={step.number}
                className="border-b border-ink/20 transition-colors hover:bg-ink/[0.02]"
              >
                <button
                  type="button"
                  onClick={() => toggleStep(idx)}
                  className="w-full text-left py-6 sm:py-8 flex flex-col md:flex-row md:items-center gap-4 md:gap-8 group"
                >
                  {/* Column 1: Giant Muted Anton Numeral */}
                  <span className="font-display text-4xl sm:text-5xl text-ink/25 select-none leading-none w-16 sm:w-20 shrink-0 group-hover:text-ink/40 transition-colors">
                    {step.number}
                  </span>

                  {/* Column 2: Step Title */}
                  <span className="font-sans font-bold text-base sm:text-lg text-ink w-full md:w-72 lg:w-80 shrink-0 tracking-tight">
                    {step.title}
                  </span>

                  {/* Column 3: Summary Description */}
                  <span className="font-sans text-xs sm:text-sm text-ink/70 leading-relaxed flex-1 pr-4">
                    {step.summary}
                  </span>

                  {/* Column 4: Expand Icon (+) */}
                  <span className="w-8 flex justify-end text-ink/40 text-xl font-light group-hover:text-ink transition-colors shrink-0">
                    {isOpen ? (
                      <Minus className="w-5 h-5 text-ink" />
                    ) : (
                      <Plus className="w-5 h-5 text-ink/50 group-hover:text-ink" />
                    )}
                  </span>
                </button>

                {/* Expanded Technical Details Panel */}
                {isOpen && (
                  <div className="pb-7 pl-0 md:pl-28 pr-6 sm:pr-12 text-ink/80 text-xs sm:text-sm font-sans leading-relaxed animate-in fade-in slide-in-from-top-1 duration-200">
                    <div className="bg-card-surface border border-ink/10 rounded-2xl p-5 shadow-xs">
                      <span className="font-bold text-ink uppercase text-[11px] tracking-wider block mb-1.5">
                        Technical Specification & Guardrails:
                      </span>
                      <p>{step.details}</p>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
