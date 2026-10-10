"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Download,
  Sparkles,
  ArrowRight,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  FileSearch,
  Check,
  RefreshCw,
} from "lucide-react";
import { ScoreResult, ParsedResume, JDFeatures } from "@/lib/types";
import { generateScoreReportPDF } from "@/lib/export-pdf";

export default function CandidateReportPage() {
  const router = useRouter();
  const [scoreResult, setScoreResult] = useState<ScoreResult | null>(null);
  const [resume, setResume] = useState<ParsedResume | null>(null);
  const [jd, setJd] = useState<JDFeatures | null>(null);

  useEffect(() => {
    const rawScore = sessionStorage.getItem("noetrix_score");
    const rawResume = sessionStorage.getItem("noetrix_resume");
    const rawJD = sessionStorage.getItem("noetrix_jd");

    if (!rawScore || !rawResume || !rawJD) {
      router.push("/candidate/analyze");
      return;
    }

    try {
      setScoreResult(JSON.parse(rawScore));
      setResume(JSON.parse(rawResume));
      setJd(JSON.parse(rawJD));
    } catch {
      router.push("/candidate/analyze");
    }
  }, [router]);

  if (!scoreResult || !resume || !jd) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <RefreshCw className="w-8 h-8 animate-spin text-ink/40" />
      </div>
    );
  }

  const bandColors = {
    strong: "bg-accent-emerald/20 text-accent-emerald border-accent-emerald",
    moderate: "bg-accent-yellow/30 text-ink border-ink",
    weak: "bg-accent-coral/20 text-accent-coral border-accent-coral",
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-12 space-y-12">
      {/* Top Banner & Quick Actions */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-ink-border pb-8">
        <div>
          <span className="text-xs font-bold uppercase tracking-widest text-ink/60">
            Candidate Audit Report
          </span>
          <h1 className="font-display text-4xl sm:text-5xl uppercase tracking-tight text-ink">
            {scoreResult.candidate_name} · ATS ANALYSIS
          </h1>
          <p className="font-sans text-xs sm:text-sm text-ink/60">
            Scored against <strong className="text-ink">{jd.title}</strong> · File: {scoreResult.filename}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => generateScoreReportPDF(scoreResult)}
            className="flex items-center gap-2 border-2 border-ink bg-card-surface text-ink px-5 py-2.5 rounded-full font-sans text-xs font-bold hover:bg-ink/5 transition-colors shadow-sm"
          >
            <Download className="w-4 h-4" />
            <span>Download PDF Report</span>
          </button>

          <Link
            href="/candidate/editor"
            className="flex items-center gap-2 bg-ink text-canvas px-6 py-2.5 rounded-full font-sans text-xs font-bold hover:bg-ink-slate transition-all shadow-md group"
          >
            <Sparkles className="w-4 h-4 text-accent-yellow" />
            <span>Open AI Resume Editor</span>
            <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
          </Link>
        </div>
      </div>

      {/* Hero Score Card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Overall Score Gauge */}
        <div className="border-2 border-ink rounded-3xl bg-card-surface p-8 shadow-sm flex flex-col justify-between space-y-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-ink/60">Overall ATS Score</span>
              <span className={`text-xs font-bold uppercase px-3 py-0.5 rounded-full border ${bandColors[scoreResult.match_band]}`}>
                {scoreResult.match_band} Match
              </span>
            </div>

            <div className="flex items-baseline gap-2 mt-4">
              <span className="font-display text-7xl text-ink leading-none">{scoreResult.overall_score}</span>
              <span className="text-xl font-bold text-ink/40">/ 100</span>
            </div>

            {scoreResult.is_capped && (
              <div className="mt-4 p-3 bg-accent-coral/15 border border-accent-coral rounded-xl flex items-start gap-2.5 text-xs text-ink">
                <AlertTriangle className="w-4 h-4 text-accent-coral shrink-0 mt-0.5" />
                <span>
                  <strong>Must-Have Cap Triggered:</strong> Missing mandatory technical requirements capped your score at 50 points.
                </span>
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-ink/10 text-xs text-ink/60">
            Deterministic advisory evaluation based on 6 core ATS parsing dimensions.
          </div>
        </div>

        {/* Right: Priority Fixes */}
        <div className="lg:col-span-2 border-2 border-ink rounded-3xl bg-card-surface p-8 shadow-sm space-y-5">
          <div className="flex items-center justify-between">
            <h3 className="font-display text-2xl uppercase tracking-wide text-ink">
              TOP 5 PRIORITIZED ATS FIXES
            </h3>
            <span className="text-xs font-bold text-ink/60 uppercase">Action Plan</span>
          </div>

          <div className="space-y-3">
            {scoreResult.priority_fixes.map((fix, idx) => (
              <div
                key={idx}
                className="flex items-start gap-3 p-3.5 bg-canvas/60 border border-ink/10 rounded-2xl text-xs font-medium text-ink"
              >
                <div className="w-6 h-6 rounded-full bg-accent-yellow border border-ink flex items-center justify-center shrink-0 text-ink font-bold text-xs">
                  {idx + 1}
                </div>
                <div className="flex-1 pt-0.5">{fix}</div>
              </div>
            ))}
          </div>

          <div className="pt-2 flex justify-end">
            <Link
              href="/candidate/editor"
              className="inline-flex items-center gap-1.5 text-xs font-bold text-ink hover:underline uppercase tracking-wider"
            >
              <span>Apply Fixes in AI Editor</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </div>

      {/* 6-Metric Breakdown Grid */}
      <div className="space-y-6">
        <h3 className="font-display text-3xl uppercase tracking-wide text-ink">
          6-METRIC SCORECARD BREAKDOWN
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Object.entries(scoreResult.metrics).map(([key, metric]) => {
            const labels: Record<string, string> = {
              keyword_match: "Hard-Skill Keyword Match (30%)",
              semantic_fit: "Semantic Narrative Fit (20%)",
              experience: "Experience Tenure & Action Verbs (20%)",
              education: "Education & Certifications (10%)",
              impact: "Impact & Quantified Metrics (10%)",
              format: "Format & ATS Readability (10%)",
            };

            return (
              <div
                key={key}
                className="border-2 border-ink rounded-2xl bg-card-surface p-6 shadow-sm flex flex-col justify-between space-y-4"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <span className="text-[11px] font-bold uppercase tracking-wider text-ink/60">
                      {labels[key] || key}
                    </span>
                    <span className="font-display text-2xl text-ink">{metric.score}%</span>
                  </div>

                  <div className="w-full bg-canvas rounded-full h-2 mt-2 border border-ink/10 overflow-hidden">
                    <div
                      className="bg-ink h-full rounded-full transition-all duration-500"
                      style={{ width: `${metric.score}%` }}
                    />
                  </div>

                  <p className="mt-4 font-sans text-xs text-ink/80 leading-relaxed">
                    {metric.rationale}
                  </p>
                </div>

                {metric.evidence.length > 0 && (
                  <div className="pt-3 border-t border-ink/10 text-[11px] text-ink/60 space-y-1">
                    <strong className="text-ink">Verified Evidence:</strong>
                    <p className="italic">{metric.evidence[0]}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

      {/* Keyword Gap View */}
      <div className="border-2 border-ink rounded-3xl bg-card-surface p-8 shadow-sm space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="font-display text-2xl uppercase tracking-wide text-ink">
            KEYWORD COVERAGE AUDIT
          </h3>
          <span className="text-xs font-bold text-ink/60 uppercase">
            {scoreResult.matched_keywords.length} Matched · {scoreResult.missing_keywords.length} Missing
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Matched */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold uppercase text-accent-emerald tracking-wider">
              <Check className="w-4 h-4" />
              <span>Matched Technologies & Skills</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {scoreResult.matched_keywords.map((kw, i) => (
                <span
                  key={i}
                  className="bg-accent-emerald/15 text-accent-emerald border border-accent-emerald/40 text-xs font-semibold px-3 py-1 rounded-full"
                >
                  ✓ {kw}
                </span>
              ))}
            </div>
          </div>

          {/* Missing */}
          <div className="space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold uppercase text-accent-coral tracking-wider">
              <XCircle className="w-4 h-4" />
              <span>Missing from Resume</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {scoreResult.missing_keywords.length === 0 ? (
                <span className="text-xs text-ink/60 italic">All target skills detected!</span>
              ) : (
                scoreResult.missing_keywords.map((kw, i) => (
                  <span
                    key={i}
                    className="bg-accent-coral/15 text-accent-coral border border-accent-coral/40 text-xs font-semibold px-3 py-1 rounded-full"
                  >
                    ✕ {kw}
                  </span>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* "What the ATS Sees" Panel (OpenResume Pattern) */}
      <div className="border-2 border-ink rounded-3xl bg-card-surface p-8 shadow-sm space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileSearch className="w-6 h-6 text-accent-yellow" />
            <h3 className="font-display text-2xl uppercase tracking-wide text-ink">
              WHAT THE ATS SEES
            </h3>
          </div>
          <div className="flex items-center gap-2">
            <span className="bg-accent-lilac/30 text-ink border border-ink text-[11px] font-bold px-3 py-1 rounded-full uppercase tracking-wider">
              {scoreResult.ats_sees.extraction_source || "Extracted by: rules"}
            </span>
            <span className="text-xs font-bold text-ink/60 uppercase hidden sm:inline">Parser Transparency</span>
          </div>
        </div>

        <p className="font-sans text-xs text-ink/70 max-w-2xl">
          Applicant tracking systems strip visual styling and evaluate pure extracted text tokens. Here is the exact structured record extracted from your document:
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
          <div className="p-4 bg-canvas/60 border border-ink/10 rounded-2xl">
            <span className="text-[10px] font-bold uppercase text-ink/50 block">Parsed Name</span>
            <span className="font-bold text-ink text-sm">{scoreResult.ats_sees.candidate_name}</span>
          </div>

          <div className="p-4 bg-canvas/60 border border-ink/10 rounded-2xl">
            <span className="text-[10px] font-bold uppercase text-ink/50 block">Contact Email</span>
            <span className="font-bold text-ink text-sm">{scoreResult.ats_sees.email}</span>
          </div>

          <div className="p-4 bg-canvas/60 border border-ink/10 rounded-2xl">
            <span className="text-[10px] font-bold uppercase text-ink/50 block">Layout Columns</span>
            <span className="font-bold text-ink text-sm">
              {scoreResult.ats_sees.columns_detected} Column{scoreResult.ats_sees.columns_detected > 1 ? "s (Warning)" : " (Clean)"}
            </span>
          </div>

          <div className="p-4 bg-canvas/60 border border-ink/10 rounded-2xl">
            <span className="text-[10px] font-bold uppercase text-ink/50 block">Bullets Extracted</span>
            <span className="font-bold text-ink text-sm">{scoreResult.ats_sees.bullets_extracted_count} Bullets</span>
          </div>
        </div>

        <div className="p-4 bg-canvas/60 border border-ink/10 rounded-2xl text-xs space-y-2">
          <strong className="text-ink">Sections Successfully Isolated:</strong>
          <div className="flex flex-wrap gap-2">
            {scoreResult.ats_sees.sections_detected.map((sec, i) => (
              <span key={i} className="bg-ink/5 border border-ink/20 px-2.5 py-0.5 rounded-full font-bold uppercase text-[10px]">
                {sec}
              </span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
