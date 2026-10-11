"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Upload, FileText, ArrowRight, Loader2, Sparkles, CheckCircle2, ShieldCheck } from "lucide-react";
import { parseResumeFile, parseJDText, scoreResume, getLLMHealth } from "@/lib/api";

const SAMPLE_JDS = [
  {
    title: "Senior Backend Engineer",
    text: `Senior Backend Engineer (Python / FastAPI)
Requirements:
- 5+ years of software engineering experience in backend systems
- Strong proficiency in Python, FastAPI, Docker, and PostgreSQL
- Proven track record building high-throughput microservices and REST APIs
- Familiarity with AWS, Kubernetes, and Redis caching
Responsibilities:
- Architect and scale distributed backend microservices
- Optimize database queries and improve API response latency
- Collaborate with frontend engineers to ship critical product features`,
  },
  {
    title: "Fullstack React / Node.js Developer",
    text: `Fullstack Developer (React & TypeScript)
Requirements:
- 3+ years experience with React, TypeScript, Next.js, and Node.js
- Proficiency with Tailwind CSS, GraphQL, and modern state management
- Experience writing automated unit and integration tests (Jest, Playwright)
- Nice to have: Docker, CI/CD pipelines, MongoDB
Responsibilities:
- Build responsive, accessible user interfaces with clean architecture
- Develop scalable backend endpoints and integrate third-party APIs`,
  },
];

export default function CandidateAnalyzePage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isLLMOn, setIsLLMOn] = useState(false);

  useEffect(() => {
    getLLMHealth().then((h) => {
      if (h.mode === "on") setIsLLMOn(true);
    });
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError("Please upload your resume file (PDF or DOCX).");
      return;
    }
    if (!jdText.trim()) {
      setError("Please paste the target job description.");
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // 1. Parse resume
      const parsedResume = await parseResumeFile(file);

      // 2. Parse job description
      const parsedJD = await parseJDText(jdText);

      // 3. Compute deterministic ATS score
      const scoreResult = await scoreResume(parsedResume, parsedJD);

      // Save in session storage only (no server-side storage; stays in browser tab until closed)
      sessionStorage.setItem("noetrix_resume", JSON.stringify(parsedResume));
      sessionStorage.setItem("noetrix_jd", JSON.stringify(parsedJD));
      sessionStorage.setItem("noetrix_score", JSON.stringify(scoreResult));

      router.push("/candidate/report");
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "Failed to analyze resume. Make sure the backend server is running.";
      setError(message);
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-12">
      {/* Header */}
      <div className="mb-10 space-y-2">
        <span className="text-xs font-bold uppercase tracking-widest text-ink/60">
          Candidate Door · Step 1 of 3
        </span>
        <h1 className="font-display text-5xl sm:text-6xl uppercase tracking-tight text-ink">
          SCAN YOUR CV AGAINST A TARGET JOB
        </h1>
        <p className="font-sans text-sm sm:text-base text-ink/70 max-w-2xl">
          Upload your resume and paste the job description to run our 6-metric ATS evaluation. No server-side storage; a copy stays in the browser tab until it is closed.
        </p>
      </div>

      {error && (
        <div className="mb-8 p-4 bg-accent-coral/20 border-2 border-accent-coral rounded-2xl text-xs font-semibold text-ink">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
        {/* Left: File Upload */}
        <div className="border-2 border-ink rounded-3xl bg-card-surface p-8 shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-2xl uppercase tracking-wide text-ink">
              1. UPLOAD RESUME
            </h2>
            <span className="text-xs font-bold text-ink/60 uppercase">PDF / DOCX</span>
          </div>

          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-2xl p-8 text-center transition-all cursor-pointer flex flex-col items-center justify-center min-h-[220px] ${
              file ? "border-accent-emerald bg-accent-emerald/5" : "border-ink/20 hover:border-ink hover:bg-ink/5"
            }`}
          >
            <input
              type="file"
              id="resume-file"
              accept=".pdf,.docx,.doc,.txt"
              onChange={handleFileChange}
              className="hidden"
            />
            <label htmlFor="resume-file" className="cursor-pointer space-y-3 flex flex-col items-center">
              {file ? (
                <>
                  <div className="w-12 h-12 rounded-full bg-accent-emerald/20 flex items-center justify-center text-accent-emerald">
                    <CheckCircle2 className="w-6 h-6" />
                  </div>
                  <div>
                    <span className="font-sans font-bold text-sm text-ink block">{file.name}</span>
                    <span className="text-xs text-ink/60">{(file.size / 1024).toFixed(1)} KB · Click to replace</span>
                  </div>
                </>
              ) : (
                <>
                  <div className="w-12 h-12 rounded-full bg-accent-yellow border border-ink flex items-center justify-center">
                    <Upload className="w-6 h-6 text-ink" />
                  </div>
                  <div>
                    <span className="font-sans font-bold text-sm text-ink block">
                      Drag & Drop your resume here
                    </span>
                    <span className="text-xs text-ink/60">or browse from your device (PDF, DOCX up to 4MB)</span>
                  </div>
                </>
              )}
            </label>
          </div>

          <div className="bg-canvas/60 p-4 rounded-xl border border-ink/10 text-xs text-ink/70 space-y-1">
            <strong>ATS Readability Tip:</strong> Single-column resumes with standard headings (Experience, Education, Skills) score highest.
          </div>

          {isLLMOn && (
            <div className="bg-blue-50/90 border border-blue-200 text-blue-900 px-4 py-3 rounded-xl text-xs flex items-center gap-2.5">
              <ShieldCheck className="w-4 h-4 text-blue-600 shrink-0" />
              <span>AI features send your CV text with name, email and phone removed to Groq.</span>
            </div>
          )}
        </div>

        {/* Right: Job Description */}
        <div className="border-2 border-ink rounded-3xl bg-card-surface p-8 shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="font-display text-2xl uppercase tracking-wide text-ink">
              2. PASTE JOB DESCRIPTION
            </h2>
            <div className="flex gap-2">
              {SAMPLE_JDS.map((preset, idx) => (
                <button
                  key={idx}
                  onClick={() => setJdText(preset.text)}
                  className="text-[11px] font-bold text-ink bg-canvas hover:bg-accent-yellow/40 border border-ink px-2.5 py-1 rounded-full transition-colors"
                >
                  Preset {idx + 1}
                </button>
              ))}
            </div>
          </div>

          <textarea
            value={jdText}
            onChange={(e) => setJdText(e.target.value)}
            rows={10}
            placeholder="Paste the full job description here (requirements, responsibilities, skills)..."
            className="w-full p-4 border border-ink/20 rounded-2xl bg-canvas/30 font-sans text-xs focus:outline-none focus:border-ink focus:ring-1 focus:ring-ink transition-all resize-y"
          />

          <button
            onClick={handleAnalyze}
            disabled={isLoading || !file || !jdText.trim()}
            className="w-full group flex items-center justify-center gap-3 bg-ink text-canvas font-sans font-bold text-base py-4 rounded-full hover:bg-ink-slate disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin text-accent-yellow" />
                <span>Running Deterministic ATS Engine...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5 text-accent-yellow" />
                <span>Analyze & Generate Report</span>
                <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
