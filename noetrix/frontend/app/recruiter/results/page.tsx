"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Download,
  Filter,
  CheckCircle2,
  XCircle,
  Clock,
  AlertTriangle,
  ArrowUpDown,
  ChevronDown,
  ChevronUp,
  FileText,
  RefreshCw,
  Sliders,
} from "lucide-react";
import { RankedCandidate, JDFeatures, ScoringConfig } from "@/lib/types";
import { exportCandidatesCSV } from "@/lib/api";

export default function RecruiterResultsPage() {
  const router = useRouter();

  const [ranked, setRanked] = useState<RankedCandidate[]>([]);
  const [jd, setJd] = useState<JDFeatures | null>(null);
  const [config, setConfig] = useState<ScoringConfig | null>(null);
  const [selectedCandidate, setSelectedCandidate] = useState<RankedCandidate | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>("all");

  useEffect(() => {
    const rawRanked = sessionStorage.getItem("noetrix_ranked_results");
    const rawJD = sessionStorage.getItem("noetrix_recruiter_jd");
    const rawConfig = sessionStorage.getItem("noetrix_recruiter_config");

    if (!rawRanked || !rawJD) {
      router.push("/recruiter/setup");
      return;
    }

    try {
      setRanked(JSON.parse(rawRanked));
      setJd(JSON.parse(rawJD));
      if (rawConfig) setConfig(JSON.parse(rawConfig));
    } catch {
      router.push("/recruiter/setup");
    }
  }, [router]);

  if (!jd || ranked.length === 0) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <RefreshCw className="w-8 h-8 animate-spin text-ink/40" />
      </div>
    );
  }

  // Update candidate status
  const handleUpdateStatus = (candidateFilename: string, newStatus: RankedCandidate["status"]) => {
    const updated = ranked.map((c) =>
      c.filename === candidateFilename ? { ...c, status: newStatus } : c
    );
    setRanked(updated);
    sessionStorage.setItem("noetrix_ranked_results", JSON.stringify(updated));
    if (selectedCandidate?.filename === candidateFilename) {
      setSelectedCandidate({ ...selectedCandidate, status: newStatus });
    }
  };

  // CSV Export
  const handleExportCSV = async () => {
    try {
      const blob = await exportCandidatesCSV(ranked);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `Noetrix_Shortlist_${jd.title.replace(/\s+/g, "_")}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export error:", err);
    }
  };

  const filteredCandidates = ranked.filter((c) => {
    if (statusFilter === "all") return true;
    return c.status === statusFilter;
  });

  const bandColors = {
    strong: "bg-accent-emerald/20 text-accent-emerald border-accent-emerald/40",
    moderate: "bg-accent-yellow/30 text-ink border-ink/40",
    weak: "bg-accent-coral/20 text-accent-coral border-accent-coral/40",
  };

  return (
    <div className="max-w-7xl mx-auto px-6 py-12 space-y-10">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-ink-border pb-8">
        <div>
          <span className="text-xs font-bold uppercase tracking-widest text-ink/60">
            Requisition Leaderboard
          </span>
          <h1 className="font-display text-4xl sm:text-5xl uppercase tracking-tight text-ink">
            {jd.title} · CANDIDATE RANKINGS
          </h1>
          <p className="font-sans text-xs sm:text-sm text-ink/60">
            {ranked.length} applicants screened · Deterministic tie-breaking applied
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <Link
            href="/recruiter/setup"
            className="flex items-center gap-2 border-2 border-ink bg-card-surface text-ink px-4 py-2.5 rounded-full font-sans text-xs font-bold hover:bg-ink/5 transition-colors shadow-sm"
          >
            <Sliders className="w-4 h-4" />
            <span>Adjust Weights</span>
          </Link>

          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 bg-ink text-canvas px-5 py-2.5 rounded-full font-sans text-xs font-bold hover:bg-ink-slate transition-all shadow-md"
          >
            <Download className="w-4 h-4 text-accent-yellow" />
            <span>Export CSV Shortlist</span>
          </button>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center justify-between border-b border-ink/10 pb-4">
        <div className="flex items-center gap-2">
          {["all", "shortlisted", "active", "hold", "rejected"].map((tab) => (
            <button
              key={tab}
              onClick={() => setStatusFilter(tab)}
              className={`px-4 py-1.5 rounded-full text-xs font-bold capitalize transition-all ${
                statusFilter === tab
                  ? "bg-ink text-canvas"
                  : "bg-card-surface text-ink/70 hover:bg-ink/5 border border-ink/20"
              }`}
            >
              {tab} (
              {tab === "all"
                ? ranked.length
                : ranked.filter((c) => c.status === tab).length}
              )
            </button>
          ))}
        </div>

        <span className="text-xs text-ink/50 hidden sm:inline">
          Showing {filteredCandidates.length} of {ranked.length}
        </span>
      </div>

      {/* Main Leaderboard & Detail Drawer Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Table View (8 or 12 Cols) */}
        <div className={`${selectedCandidate ? "lg:col-span-7" : "lg:col-span-12"} border-2 border-ink rounded-3xl bg-card-surface overflow-hidden shadow-sm`}>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-sans">
              <thead className="bg-canvas/80 border-b-2 border-ink uppercase tracking-wider text-[11px] font-bold text-ink">
                <tr>
                  <th className="py-4 px-4">Rank</th>
                  <th className="py-4 px-4">Candidate</th>
                  <th className="py-4 px-4">Score</th>
                  <th className="py-4 px-4">Must-Haves</th>
                  <th className="py-4 px-4">Status</th>
                  <th className="py-4 px-4 text-right">Details</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-ink/10">
                {filteredCandidates.map((c) => {
                  const isSelected = selectedCandidate?.filename === c.filename;

                  return (
                    <tr
                      key={c.filename}
                      onClick={() => setSelectedCandidate(c)}
                      className={`cursor-pointer transition-colors ${
                        isSelected ? "bg-accent-yellow/15" : "hover:bg-canvas/50"
                      }`}
                    >
                      {/* Rank */}
                      <td className="py-4 px-4">
                        <span className={`inline-flex items-center justify-center w-7 h-7 rounded-full font-display text-sm ${
                          c.rank === 1 ? "bg-accent-yellow border border-ink font-bold" :
                          c.rank === 2 ? "bg-accent-lilac border border-ink font-bold" :
                          c.rank === 3 ? "bg-accent-coral/40 border border-ink font-bold" :
                          "bg-canvas/80 border border-ink/20"
                        }`}>
                          #{c.rank}
                        </span>
                      </td>

                      {/* Name & File */}
                      <td className="py-4 px-4">
                        <strong className="text-ink text-sm block font-bold">{c.candidate_name}</strong>
                        <span className="text-[10px] text-ink/50">{c.filename}</span>
                      </td>

                      {/* Overall Score */}
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-2">
                          <span className="font-display text-xl text-ink font-bold">
                            {c.overall_score}%
                          </span>
                          <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded-full border ${bandColors[c.match_band]}`}>
                            {c.match_band}
                          </span>
                        </div>
                      </td>

                      {/* Must-Have Coverage */}
                      <td className="py-4 px-4 font-semibold">
                        <span className={c.must_have_coverage === 100 ? "text-accent-emerald font-bold" : "text-accent-coral font-bold"}>
                          {c.must_have_coverage}%
                        </span>
                      </td>

                      {/* Status */}
                      <td className="py-4 px-4" onClick={(e) => e.stopPropagation()}>
                        <select
                          value={c.status}
                          onChange={(e) => handleUpdateStatus(c.filename, e.target.value as RankedCandidate["status"])}
                          className="px-2.5 py-1 border border-ink/20 rounded-full bg-canvas text-xs font-bold capitalize focus:outline-none focus:border-ink cursor-pointer"
                        >
                          <option value="active">Active</option>
                          <option value="shortlisted">Shortlisted</option>
                          <option value="hold">Hold</option>
                          <option value="rejected">Rejected</option>
                        </select>
                      </td>

                      {/* Inspect Action */}
                      <td className="py-4 px-4 text-right">
                        <span className="text-xs font-bold text-ink underline underline-offset-2">
                          {isSelected ? "Inspecting" : "Inspect"}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Candidate Detail Inspection Drawer (5 Cols) */}
        {selectedCandidate && (
          <div className="lg:col-span-5 border-2 border-ink rounded-3xl bg-card-surface p-6 shadow-sm space-y-6 sticky top-28">
            <div className="flex items-start justify-between border-b border-ink/10 pb-4">
              <div>
                <span className="text-[10px] font-bold uppercase tracking-wider text-ink/60">
                  Rank #{selectedCandidate.rank} Candidate Dossier
                </span>
                <h3 className="font-display text-2xl uppercase tracking-wide text-ink">
                  {selectedCandidate.candidate_name}
                </h3>
                <span className="text-xs text-ink/50">{selectedCandidate.filename}</span>
              </div>
              <button
                onClick={() => setSelectedCandidate(null)}
                className="text-xs font-bold uppercase hover:underline text-ink/60"
              >
                Close
              </button>
            </div>

            {/* Score & Must-Have Badges */}
            <div className="flex items-center justify-between p-4 bg-canvas/60 rounded-2xl border border-ink/10">
              <div>
                <span className="text-[10px] font-bold uppercase text-ink/50 block">Composite Fit</span>
                <span className="font-display text-3xl text-ink font-bold">
                  {selectedCandidate.overall_score}%
                </span>
              </div>
              <div className="text-right">
                <span className="text-[10px] font-bold uppercase text-ink/50 block">Must-Have Match</span>
                <span className="font-display text-2xl text-accent-emerald font-bold">
                  {selectedCandidate.must_have_coverage}%
                </span>
              </div>
            </div>

            {/* Risk Flags */}
            {selectedCandidate.risk_flags.length > 0 && (
              <div className="space-y-2">
                <span className="text-xs font-bold uppercase tracking-wider text-accent-coral flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Audit Risk Flags</span>
                </span>
                <div className="space-y-1.5">
                  {selectedCandidate.risk_flags.map((flag, idx) => (
                    <div key={idx} className="p-2.5 bg-accent-coral/10 border border-accent-coral/30 rounded-xl text-xs text-ink">
                      {flag}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 6 Metric Breakdown with Evidence */}
            <div className="space-y-3">
              <span className="text-xs font-bold uppercase tracking-wider text-ink block">
                Evidence & Metric Scorecard
              </span>

              <div className="space-y-3 max-h-72 overflow-y-auto">
                {Object.entries(selectedCandidate.metrics).map(([key, metric]) => (
                  <div key={key} className="p-3 bg-canvas/40 border border-ink/10 rounded-xl space-y-1 text-xs">
                    <div className="flex justify-between font-bold capitalize">
                      <span>{key.replace("_", " ")}:</span>
                      <span className="font-display text-sm">{metric.score}%</span>
                    </div>
                    <p className="text-[11px] text-ink/70 leading-relaxed">{metric.rationale}</p>
                    {metric.evidence.length > 0 && (
                      <p className="text-[10px] text-accent-emerald italic">
                        Evidence: {metric.evidence[0]}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Status Selector */}
            <div className="pt-4 border-t border-ink/10 flex items-center justify-between">
              <span className="text-xs font-bold text-ink">Set Requisition Status:</span>
              <div className="flex gap-1.5">
                {(["shortlisted", "hold", "rejected"] as const).map((s) => (
                  <button
                    key={s}
                    onClick={() => handleUpdateStatus(selectedCandidate.filename, s)}
                    className={`px-3 py-1 rounded-full text-xs font-bold capitalize border transition-all ${
                      selectedCandidate.status === s
                        ? "bg-ink text-canvas border-ink"
                        : "bg-canvas text-ink/70 border-ink/20 hover:border-ink"
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
