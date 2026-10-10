"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowRight, Sliders, ShieldAlert, Sparkles, Plus, X } from "lucide-react";
import { parseJDText } from "@/lib/api";
import { JDFeatures, ScoringConfig } from "@/lib/types";

export default function RecruiterSetupPage() {
  const router = useRouter();

  const [title, setTitle] = useState("Senior Backend Engineer");
  const [jdText, setJdText] = useState(`Senior Backend Engineer (Python / FastAPI)
Requirements:
- 5+ years of software engineering experience in backend systems
- Strong proficiency in Python, FastAPI, Docker, and PostgreSQL
- Proven track record building high-throughput microservices and REST APIs
- Nice to have: AWS, Kubernetes, Redis caching
Responsibilities:
- Architect and scale distributed backend microservices
- Optimize database queries and improve API response latency`);

  const [mustHaves, setMustHaves] = useState<string[]>(["python", "fastapi", "docker", "postgresql"]);
  const [niceToHaves, setNiceToHaves] = useState<string[]>(["aws", "kubernetes", "redis"]);
  const [minYears, setMinYears] = useState(5);
  const [newMustHave, setNewMustHave] = useState("");

  // Scoring Weights Configuration
  const [weights, setWeights] = useState({
    keyword_match: 30,
    semantic_fit: 20,
    experience: 20,
    education: 10,
    impact: 10,
    format: 10,
  });
  const [mustHaveCapEnabled, setMustHaveCapEnabled] = useState(true);
  const [mustHaveCapValue, setMustHaveCapValue] = useState(50);

  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0);

  const handleAutoExtract = async () => {
    if (!jdText.trim()) return;
    try {
      const parsed = await parseJDText(jdText, title);
      setMustHaves(parsed.must_have_skills);
      setNiceToHaves(parsed.nice_to_have_skills);
      if (parsed.min_experience_years > 0) setMinYears(parsed.min_experience_years);
    } catch (err) {
      console.error("Auto extraction error:", err);
    }
  };

  const handleProceed = () => {
    const jdObject: JDFeatures = {
      title,
      raw_text: jdText,
      must_have_skills: mustHaves,
      nice_to_have_skills: niceToHaves,
      min_experience_years: minYears,
      domain: "Technology",
      responsibilities: [],
      keywords: [...mustHaves, ...niceToHaves],
    };

    const configObject: ScoringConfig = {
      weights: {
        keyword_match: weights.keyword_match / 100,
        semantic_fit: weights.semantic_fit / 100,
        experience: weights.experience / 100,
        education: weights.education / 100,
        impact: weights.impact / 100,
        format: weights.format / 100,
      },
      must_have_cap: mustHaveCapValue,
      enable_must_have_cap: mustHaveCapEnabled,
      strong_band_threshold: 75.0,
      moderate_band_threshold: 50.0,
    };

    sessionStorage.setItem("noetrix_recruiter_jd", JSON.stringify(jdObject));
    sessionStorage.setItem("noetrix_recruiter_config", JSON.stringify(configObject));
    router.push("/recruiter/upload");
  };

  return (
    <div className="max-w-5xl mx-auto px-6 py-12 space-y-10">
      {/* Header */}
      <div className="space-y-2">
        <span className="text-xs font-bold uppercase tracking-widest text-ink/60">
          Recruiter Door · Step 1 of 3
        </span>
        <h1 className="font-display text-5xl uppercase tracking-tight text-ink">
          SET REQUISITION CRITERIA & WEIGHTS
        </h1>
        <p className="font-sans text-sm text-ink/70 max-w-2xl">
          Define mandatory skills, minimum tenure, and scoring parameters. Scores across your applicant batch will be calculated deterministically based on these rules.
        </p>
      </div>

      {/* Step 1: Requisition Definition */}
      <div className="border-2 border-ink rounded-3xl bg-card-surface p-8 shadow-sm space-y-6">
        <h2 className="font-display text-2xl uppercase tracking-wide text-ink">
          1. JOB REQUISITION DETAILS
        </h2>

        <div className="space-y-4">
          <div>
            <label className="text-xs font-bold uppercase tracking-wider text-ink/70 block mb-1">
              Job Title
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-3 border border-ink/20 rounded-xl bg-canvas/30 text-xs font-sans focus:outline-none focus:border-ink font-bold"
            />
          </div>

          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-xs font-bold uppercase tracking-wider text-ink/70">
                Job Description Text
              </label>
              <button
                onClick={handleAutoExtract}
                className="flex items-center gap-1.5 text-xs font-bold text-accent-yellow bg-ink px-3 py-1 rounded-full hover:bg-ink-slate transition-colors"
              >
                <Sparkles className="w-3.5 h-3.5" />
                <span>Auto-Extract Skills</span>
              </button>
            </div>
            <textarea
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              rows={6}
              className="w-full p-4 border border-ink/20 rounded-2xl bg-canvas/30 text-xs font-sans focus:outline-none focus:border-ink resize-y"
            />
          </div>
        </div>

        {/* Must-Have Skills Editor */}
        <div className="pt-4 border-t border-ink/10 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-ink">
              Mandatory Must-Have Skills ({mustHaves.length})
            </span>
            <span className="text-[11px] text-accent-coral font-bold">
              Missing any triggers score cap
            </span>
          </div>

          <div className="flex flex-wrap gap-2">
            {mustHaves.map((skill, idx) => (
              <span
                key={idx}
                className="inline-flex items-center gap-1.5 bg-accent-yellow/30 border border-ink px-3 py-1.5 rounded-full text-xs font-bold text-ink"
              >
                <span>{skill}</span>
                <button
                  onClick={() => setMustHaves(mustHaves.filter((_, i) => i !== idx))}
                  className="hover:text-accent-coral"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </span>
            ))}
          </div>

          <div className="flex gap-2 pt-2">
            <input
              type="text"
              value={newMustHave}
              onChange={(e) => setNewMustHave(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && newMustHave.trim()) {
                  setMustHaves([...mustHaves, newMustHave.trim().toLowerCase()]);
                  setNewMustHave("");
                }
              }}
              placeholder="Add mandatory skill and press Enter..."
              className="px-4 py-2 border border-ink/20 rounded-full bg-canvas/40 text-xs font-sans flex-1"
            />
            <button
              onClick={() => {
                if (newMustHave.trim()) {
                  setMustHaves([...mustHaves, newMustHave.trim().toLowerCase()]);
                  setNewMustHave("");
                }
              }}
              className="bg-ink text-canvas px-4 py-2 rounded-full text-xs font-bold"
            >
              Add
            </button>
          </div>
        </div>
      </div>

      {/* Step 2: Scoring Weights & Knockout Rules */}
      <div className="border-2 border-ink rounded-3xl bg-card-surface p-8 shadow-sm space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="font-display text-2xl uppercase tracking-wide text-ink">
            2. SCORING WEIGHTS & KNOCKOUT RULES
          </h2>
          <span className={`text-xs font-bold px-3 py-1 rounded-full ${totalWeight === 100 ? "bg-accent-emerald/20 text-accent-emerald" : "bg-accent-coral/20 text-accent-coral"}`}>
            Total: {totalWeight}% (Must sum to 100%)
          </span>
        </div>

        {/* Sliders Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-6 text-xs">
          <div>
            <div className="flex justify-between font-bold mb-1">
              <span>Hard-Skill Keyword Match:</span>
              <span>{weights.keyword_match}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="60"
              value={weights.keyword_match}
              onChange={(e) => setWeights({ ...weights, keyword_match: Number(e.target.value) })}
              className="w-full accent-ink"
            />
          </div>

          <div>
            <div className="flex justify-between font-bold mb-1">
              <span>Semantic Fit (MiniLM):</span>
              <span>{weights.semantic_fit}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="40"
              value={weights.semantic_fit}
              onChange={(e) => setWeights({ ...weights, semantic_fit: Number(e.target.value) })}
              className="w-full accent-ink"
            />
          </div>

          <div>
            <div className="flex justify-between font-bold mb-1">
              <span>Experience Tenure:</span>
              <span>{weights.experience}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="40"
              value={weights.experience}
              onChange={(e) => setWeights({ ...weights, experience: Number(e.target.value) })}
              className="w-full accent-ink"
            />
          </div>

          <div>
            <div className="flex justify-between font-bold mb-1">
              <span>Education & Certs:</span>
              <span>{weights.education}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="30"
              value={weights.education}
              onChange={(e) => setWeights({ ...weights, education: Number(e.target.value) })}
              className="w-full accent-ink"
            />
          </div>

          <div>
            <div className="flex justify-between font-bold mb-1">
              <span>Impact (Quantified Metrics):</span>
              <span>{weights.impact}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="30"
              value={weights.impact}
              onChange={(e) => setWeights({ ...weights, impact: Number(e.target.value) })}
              className="w-full accent-ink"
            />
          </div>

          <div>
            <div className="flex justify-between font-bold mb-1">
              <span>Format & ATS Health:</span>
              <span>{weights.format}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="30"
              value={weights.format}
              onChange={(e) => setWeights({ ...weights, format: Number(e.target.value) })}
              className="w-full accent-ink"
            />
          </div>
        </div>

        {/* Soft Knockout Toggle (SmartATS Pattern) */}
        <div className="pt-4 border-t border-ink/10 flex items-center justify-between p-4 bg-canvas/60 rounded-2xl border border-ink/10">
          <div className="space-y-0.5">
            <span className="font-sans font-bold text-xs text-ink block">
              Enforce 50-Point Must-Have Knockout Cap
            </span>
            <span className="text-[11px] text-ink/60">
              Any candidate missing a mandatory skill has their overall score capped at {mustHaveCapValue}.
            </span>
          </div>
          <input
            type="checkbox"
            checked={mustHaveCapEnabled}
            onChange={(e) => setMustHaveCapEnabled(e.target.checked)}
            className="w-5 h-5 accent-ink rounded"
          />
        </div>
      </div>

      {/* Proceed Button */}
      <div className="flex justify-end">
        <button
          onClick={handleProceed}
          className="flex items-center gap-3 bg-ink text-canvas font-sans font-bold text-sm px-8 py-3.5 rounded-full hover:bg-ink-slate transition-all shadow-md group"
        >
          <span>Save Requisition & Proceed to Upload</span>
          <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
        </button>
      </div>
    </div>
  );
}
