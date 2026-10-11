"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Upload, FileText, CheckCircle2, Loader2, ArrowRight, Sparkles, Trash2, AlertCircle, XCircle } from "lucide-react";
import { parseResumeFile, rankResumes } from "@/lib/api";
import { ParsedResume, JDFeatures, ScoringConfig } from "@/lib/types";

const MAX_RESUMES = 50;

// 5 Sample Candidate Resumes for instant 1-click evaluation
const SAMPLE_CANDIDATES: ParsedResume[] = [
  {
    filename: "alice_senior_backend.pdf",
    raw_text: "Alice Walker. Senior Backend Engineer with 6 years experience. Expert in Python, FastAPI, Docker, and PostgreSQL. Architected microservices supporting 20,000 requests/sec. BS in Computer Science.",
    contact: { name: "Alice Walker", email: "alice@example.com", phone: "+1 555-0101", location: "Seattle, WA", linkedin: "", github: "", website: "" },
    summary: "Senior Backend Engineer specializing in high-throughput distributed architectures.",
    sections_detected: ["experience", "education", "skills"],
    work_experience: [
      { id: "1", title: "Senior Backend Engineer", company: "CloudScale Inc", dates: "2020 - Present", location: "Seattle", bullets: [
        "Architected and deployed Python FastAPI microservices handling 20,000+ RPS with 99.99% uptime.",
        "Optimized PostgreSQL database query execution plans, reducing p99 latency by 45%.",
        "Automated Docker container CI/CD pipelines across AWS Kubernetes clusters."
      ]}
    ],
    education: [{ id: "1", institution: "University of Washington", degree: "Bachelor of Science", field_of_study: "Computer Science", dates: "2018", gpa: "3.8", bullets: [] }],
    skills: ["python", "fastapi", "docker", "postgresql", "microservices", "kubernetes", "aws", "redis"],
    projects: [],
    certifications: ["AWS Solutions Architect"],
    parse_confidence: 1.0,
    detected_columns: 1,
    has_tables: false,
    has_graphics: false
  },
  {
    filename: "bob_junior_dev.pdf",
    raw_text: "Bob Miller. Junior Developer with 2 years experience. Familiar with Python, Flask, and SQLite. Helped team with API endpoints.",
    contact: { name: "Bob Miller", email: "bob@example.com", phone: "+1 555-0102", location: "Austin, TX", linkedin: "", github: "", website: "" },
    summary: "Junior software developer looking to grow backend skills.",
    sections_detected: ["experience", "education", "skills"],
    work_experience: [
      { id: "1", title: "Junior Developer", company: "StartupX", dates: "2022 - Present", location: "Austin", bullets: [
        "Assisted senior engineers in writing Python scripts and updating documentation.",
        "Built basic CRUD endpoints using Flask and SQLite database."
      ]}
    ],
    education: [{ id: "1", institution: "Texas State", degree: "Bachelor of Arts", field_of_study: "Information Systems", dates: "2022", gpa: "3.2", bullets: [] }],
    skills: ["python", "flask", "sqlite", "git"],
    projects: [],
    certifications: [],
    parse_confidence: 0.9,
    detected_columns: 1,
    has_tables: false,
    has_graphics: false
  },
  {
    filename: "carol_frontend_specialist.pdf",
    raw_text: "Carol Danvers. Frontend Specialist with 5 years experience in React, TypeScript, Next.js, and CSS. Built responsive web interfaces.",
    contact: { name: "Carol Danvers", email: "carol@example.com", phone: "+1 555-0103", location: "New York, NY", linkedin: "", github: "", website: "" },
    summary: "Frontend developer focused on modern web design systems.",
    sections_detected: ["experience", "education", "skills"],
    work_experience: [
      { id: "1", title: "Frontend Engineer", company: "DesignHub", dates: "2019 - Present", location: "NYC", bullets: [
        "Engineered React and Next.js web applications utilized by 50,000+ monthly active users.",
        "Refactored styling architecture using Tailwind CSS, improving lighthouse score by 30%."
      ]}
    ],
    education: [{ id: "1", institution: "NYU", degree: "Bachelor of Science", field_of_study: "Software Engineering", dates: "2019", gpa: "3.7", bullets: [] }],
    skills: ["react", "typescript", "next.js", "tailwind css", "javascript", "graphql"],
    projects: [],
    certifications: [],
    parse_confidence: 1.0,
    detected_columns: 1,
    has_tables: false,
    has_graphics: false
  },
  {
    filename: "david_devops_lead.pdf",
    raw_text: "David Zhang. Staff Infrastructure & DevOps Lead with 8 years experience. Master of Science. Kubernetes, Terraform, AWS, Docker, Python.",
    contact: { name: "David Zhang", email: "david@example.com", phone: "+1 555-0104", location: "San Francisco, CA", linkedin: "", github: "", website: "" },
    summary: "Infrastructure engineer with strong backend scripting background.",
    sections_detected: ["experience", "education", "skills"],
    work_experience: [
      { id: "1", title: "Lead DevOps Engineer", company: "FinTech Global", dates: "2016 - Present", location: "SF", bullets: [
        "Orchestrated Kubernetes clusters scaling to 500+ microservice nodes.",
        "Automated multi-region infrastructure deployment using Terraform, cutting cloud spend by $120,000 annually.",
        "Wrote Python and Bash automation scripts for backend telemetry and load balancing."
      ]}
    ],
    education: [{ id: "1", institution: "UC Berkeley", degree: "Master of Science", field_of_study: "Computer Engineering", dates: "2016", gpa: "3.9", bullets: [] }],
    skills: ["kubernetes", "docker", "aws", "terraform", "python", "bash", "linux", "ci/cd"],
    projects: [],
    certifications: ["CKA Kubernetes Administrator"],
    parse_confidence: 1.0,
    detected_columns: 1,
    has_tables: false,
    has_graphics: false
  },
  {
    filename: "elena_mid_fullstack.pdf",
    raw_text: "Elena Rostova. Fullstack Engineer with 4 years experience. Python, FastAPI, React, PostgreSQL. Built client dashboards and backend services.",
    contact: { name: "Elena Rostova", email: "elena@example.com", phone: "+1 555-0105", location: "Chicago, IL", linkedin: "", github: "", website: "" },
    summary: "Fullstack developer skilled in Python backend APIs and modern web frontends.",
    sections_detected: ["experience", "education", "skills"],
    work_experience: [
      { id: "1", title: "Fullstack Developer", company: "Midwest Logistics", dates: "2020 - Present", location: "Chicago", bullets: [
        "Developed Python FastAPI REST endpoints integrated with PostgreSQL database.",
        "Constructed responsive React admin portals for 500+ internal depot operators.",
        "Containerized core microservices using Docker for streamlined testing."
      ]}
    ],
    education: [{ id: "1", institution: "University of Illinois", degree: "Bachelor of Science", field_of_study: "Computer Science", dates: "2020", gpa: "3.6", bullets: [] }],
    skills: ["python", "fastapi", "postgresql", "react", "docker", "sql"],
    projects: [],
    certifications: [],
    parse_confidence: 1.0,
    detected_columns: 1,
    has_tables: false,
    has_graphics: false
  }
];

export default function RecruiterUploadPage() {
  const router = useRouter();

  const [jd, setJd] = useState<JDFeatures | null>(null);
  const [config, setConfig] = useState<ScoringConfig | null>(null);
  const [parsedResumes, setParsedResumes] = useState<ParsedResume[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [failedUploads, setFailedUploads] = useState<{ filename: string; reason: string }[]>([]);
  const [currentProgress, setCurrentProgress] = useState<{ current: number; total: number; filename: string } | null>(null);

  useEffect(() => {
    const rawJD = sessionStorage.getItem("noetrix_recruiter_jd");
    const rawConfig = sessionStorage.getItem("noetrix_recruiter_config");

    if (!rawJD || !rawConfig) {
      router.push("/recruiter/setup");
      return;
    }

    try {
      setJd(JSON.parse(rawJD));
      setConfig(JSON.parse(rawConfig));
    } catch {
      router.push("/recruiter/setup");
    }
  }, [router]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const incomingFiles = Array.from(e.target.files);
    e.target.value = ""; // Reset input so same files can be re-selected if needed
    setUploadError(null);

    if (incomingFiles.length === 0) return;

    // Enforce 50 resumes maximum limit
    if (parsedResumes.length >= MAX_RESUMES) {
      setUploadError(`Maximum limit of ${MAX_RESUMES} resumes reached. Clear some resumes before uploading more.`);
      return;
    }

    let filesToProcess = incomingFiles;
    if (parsedResumes.length + incomingFiles.length > MAX_RESUMES) {
      const allowedSlots = MAX_RESUMES - parsedResumes.length;
      setUploadError(
        `Upload limit notice: You can only upload up to ${MAX_RESUMES} resumes total. Processing first ${allowedSlots} of ${incomingFiles.length} selected files.`
      );
      filesToProcess = incomingFiles.slice(0, allowedSlots);
    }

    setIsProcessing(true);
    const newParsed: ParsedResume[] = [];
    const newFailures: { filename: string; reason: string }[] = [];

    for (let i = 0; i < filesToProcess.length; i++) {
      const file = filesToProcess[i];
      setCurrentProgress({ current: i + 1, total: filesToProcess.length, filename: file.name });
      setUploadStatus(`Parsing file ${i + 1} of ${filesToProcess.length}: ${file.name}...`);

      try {
        const parsed = await parseResumeFile(file);
        newParsed.push(parsed);
      } catch (err: any) {
        const reason = err?.message || "Failed to parse document";
        newFailures.push({ filename: file.name, reason });
        console.error(`Failed parsing ${file.name}:`, err);
      }
    }

    if (newParsed.length > 0) {
      setParsedResumes((prev) => [...prev, ...newParsed]);
    }
    if (newFailures.length > 0) {
      setFailedUploads((prev) => [...prev, ...newFailures]);
    }

    setIsProcessing(false);
    setCurrentProgress(null);
    setUploadStatus(null);
  };

  const handleLoadSampleCandidates = () => {
    setUploadError(null);
    setFailedUploads([]);
    setParsedResumes(SAMPLE_CANDIDATES);
  };

  const handleRunRanker = async () => {
    if (!jd || !config || parsedResumes.length === 0) return;

    setIsProcessing(true);
    try {
      const ranked = await rankResumes(parsedResumes, jd, config);
      sessionStorage.setItem("noetrix_ranked_results", JSON.stringify(ranked));
      router.push("/recruiter/results");
    } catch (err) {
      console.error("Ranking error:", err);
      setIsProcessing(false);
    }
  };

  if (!jd || !config) return null;

  return (
    <div className="max-w-5xl mx-auto px-6 py-12 space-y-10">
      {/* Header */}
      <div className="space-y-2">
        <span className="text-xs font-bold uppercase tracking-widest text-ink/60">
          Recruiter Door · Step 2 of 3
        </span>
        <h1 className="font-display text-5xl uppercase tracking-tight text-ink">
          UPLOAD BATCH APPLICANT CVS
        </h1>
        <p className="font-sans text-sm text-ink/70 max-w-2xl">
          Screening for <strong className="text-ink">{jd.title}</strong> ({jd.must_have_skills.length} mandatory must-haves). Upload up to {MAX_RESUMES} resumes or load our demo batch.
        </p>
      </div>

      {/* Error Banner */}
      {uploadError && (
        <div className="p-4 bg-accent-coral/15 border-2 border-accent-coral rounded-2xl flex items-start gap-3 text-ink text-xs font-medium">
          <AlertCircle className="w-5 h-5 text-accent-coral shrink-0 mt-0.5" />
          <div className="flex-1">
            <strong className="block font-bold">Upload Warning</strong>
            {uploadError}
          </div>
          <button onClick={() => setUploadError(null)} className="text-ink/60 hover:text-ink font-bold">Dismiss</button>
        </div>
      )}

      {/* Upload Dropzone */}
      <div className="border-2 border-ink rounded-3xl bg-card-surface p-8 shadow-sm space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div>
            <h2 className="font-display text-2xl uppercase tracking-wide text-ink">
              BATCH RESUME INGESTION
            </h2>
            <span className="text-xs text-ink/60 font-sans">
              Capacity: {parsedResumes.length} / {MAX_RESUMES} resumes
            </span>
          </div>
          <button
            onClick={handleLoadSampleCandidates}
            disabled={isProcessing}
            className="flex items-center gap-2 bg-accent-yellow/40 hover:bg-accent-yellow border border-ink text-xs font-bold px-4 py-2 rounded-full transition-colors disabled:opacity-50"
          >
            <Sparkles className="w-4 h-4 text-ink" />
            <span>Load 5 Demo Candidate Resumes</span>
          </button>
        </div>

        <div className={`border-2 border-dashed border-ink/20 hover:border-ink rounded-2xl p-8 text-center transition-all bg-canvas/30 flex flex-col items-center justify-center ${parsedResumes.length >= MAX_RESUMES ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}>
          <input
            type="file"
            id="batch-files"
            multiple
            accept=".pdf,.docx,.txt"
            onChange={handleFileUpload}
            disabled={isProcessing || parsedResumes.length >= MAX_RESUMES}
            className="hidden"
          />
          <label htmlFor={parsedResumes.length >= MAX_RESUMES ? undefined : "batch-files"} className={`space-y-3 flex flex-col items-center ${parsedResumes.length >= MAX_RESUMES ? 'cursor-not-allowed' : 'cursor-pointer'}`}>
            <div className="w-12 h-12 rounded-full bg-accent-lilac border border-ink flex items-center justify-center">
              <Upload className="w-6 h-6 text-ink" />
            </div>
            <div>
              <span className="font-sans font-bold text-sm text-ink block">
                {parsedResumes.length >= MAX_RESUMES ? `Maximum capacity reached (${MAX_RESUMES} resumes)` : "Select or drop multiple resumes (PDF / DOCX / TXT)"}
              </span>
              <span className="text-xs text-ink/60">Limit: maximum {MAX_RESUMES} resumes per screening batch</span>
            </div>
          </label>
        </div>

        {/* Real-time Progress Indicator */}
        {isProcessing && currentProgress && (
          <div className="p-4 bg-accent-yellow/20 border-2 border-ink rounded-2xl space-y-2">
            <div className="flex items-center justify-between text-xs font-bold text-ink">
              <div className="flex items-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-ink" />
                <span>Processing Document ({currentProgress.current} / {currentProgress.total})</span>
              </div>
              <span className="font-mono">{Math.round((currentProgress.current / currentProgress.total) * 100)}%</span>
            </div>
            <div className="w-full bg-ink/10 h-2 rounded-full overflow-hidden">
              <div
                className="bg-accent-emerald h-full transition-all duration-300"
                style={{ width: `${(currentProgress.current / currentProgress.total) * 100}%` }}
              />
            </div>
            <p className="text-[11px] text-ink/70 truncate font-mono">
              Current: {currentProgress.filename}
            </p>
          </div>
        )}

        {/* Failed Uploads Section */}
        {failedUploads.length > 0 && (
          <div className="p-4 bg-accent-coral/10 border border-accent-coral/40 rounded-2xl space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-accent-coral uppercase tracking-wide flex items-center gap-1.5">
                <XCircle className="w-4 h-4" />
                <span>Parsing Failures ({failedUploads.length})</span>
              </span>
              <button
                onClick={() => setFailedUploads([])}
                className="text-[11px] text-ink/60 hover:text-ink font-semibold"
              >
                Clear errors
              </button>
            </div>
            <div className="space-y-1.5 max-h-36 overflow-y-auto">
              {failedUploads.map((f, i) => (
                <div key={i} className="text-xs flex items-start justify-between bg-canvas/60 p-2 rounded-lg border border-ink/10">
                  <span className="font-semibold text-ink truncate mr-2">{f.filename}</span>
                  <span className="text-ink/60 text-[11px] shrink-0">{f.reason}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Uploaded Queue */}
        <div className="space-y-3 pt-4 border-t border-ink/10">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-ink">
              Ready for Screening ({parsedResumes.length} / {MAX_RESUMES})
            </span>
            {parsedResumes.length > 0 && (
              <button
                onClick={() => {
                  setParsedResumes([]);
                  setFailedUploads([]);
                  setUploadError(null);
                }}
                className="text-xs text-accent-coral font-bold hover:underline"
              >
                Clear all
              </button>
            )}
          </div>

          {parsedResumes.length === 0 ? (
            <p className="text-xs text-ink/50 italic">
              No resumes uploaded yet. Click above to upload or load demo candidates.
            </p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-h-72 overflow-y-auto">
              {parsedResumes.map((res, idx) => (
                <div
                  key={idx}
                  className="flex items-center justify-between p-3 bg-canvas/60 border border-ink/10 rounded-xl text-xs"
                >
                  <div className="flex items-center gap-2.5 truncate">
                    <FileText className="w-4 h-4 text-ink/60 shrink-0" />
                    <div className="truncate">
                      <strong className="text-ink block truncate">{res.contact.name || res.filename}</strong>
                      <span className="text-[10px] text-ink/50">{res.skills.length} skills parsed</span>
                    </div>
                  </div>
                  <button
                    onClick={() => setParsedResumes(parsedResumes.filter((_, i) => i !== idx))}
                    className="text-ink/40 hover:text-accent-coral p-1"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Trigger Button */}
      <div className="flex justify-end">
        <button
          onClick={handleRunRanker}
          disabled={isProcessing || parsedResumes.length === 0}
          className="flex items-center gap-3 bg-ink text-canvas font-sans font-bold text-sm px-8 py-3.5 rounded-full hover:bg-ink-slate disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md group"
        >
          {isProcessing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin text-accent-yellow" />
              <span>Running Deterministic Ranker...</span>
            </>
          ) : (
            <>
              <span>Score & Rank {parsedResumes.length} Candidates</span>
              <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
            </>
          )}
        </button>
      </div>
    </div>
  );
}
