import {
  ParsedResume,
  JDFeatures,
  ScoreResult,
  RankedCandidate,
  ScoringConfig,
  EnhanceBulletResponse,
  TailorResumeResponse,
} from "./types";

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

export async function parseResumeFile(file: File): Promise<ParsedResume> {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/api/parse`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to parse resume" }));
    throw new Error(err.detail || "Failed to parse resume");
  }

  return res.json();
}

export async function parseJDText(rawText: string, title?: string): Promise<JDFeatures> {
  const res = await fetch(`${BASE_URL}/api/parse-jd`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ raw_text: rawText, title }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to parse job description" }));
    throw new Error(err.detail || "Failed to parse job description");
  }

  return res.json();
}

export async function scoreResume(
  resume: ParsedResume,
  jd: JDFeatures,
  config?: ScoringConfig
): Promise<ScoreResult> {
  const res = await fetch(`${BASE_URL}/api/score`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resume, jd, config }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to score resume" }));
    throw new Error(err.detail || "Failed to score resume");
  }

  return res.json();
}

export async function rankResumes(
  resumes: ParsedResume[],
  jd: JDFeatures,
  config?: ScoringConfig
): Promise<RankedCandidate[]> {
  const res = await fetch(`${BASE_URL}/api/rank`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resumes, jd, config }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to rank resumes" }));
    throw new Error(err.detail || "Failed to rank resumes");
  }

  return res.json();
}

export async function enhanceBullet(
  bullet: string,
  jobTitle: string = "",
  targetKeywords: string[] = []
): Promise<EnhanceBulletResponse> {
  const res = await fetch(`${BASE_URL}/api/improve/bullet`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      bullet,
      job_title: jobTitle,
      target_keywords: targetKeywords,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to enhance bullet" }));
    throw new Error(err.detail || "Failed to enhance bullet");
  }

  return res.json();
}

export async function tailorResume(
  resume: ParsedResume,
  jd: JDFeatures,
  strategy: string = "balanced"
): Promise<TailorResumeResponse> {
  const res = await fetch(`${BASE_URL}/api/improve/tailor`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      resume,
      jd,
      prompt_strategy: strategy,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to tailor resume" }));
    throw new Error(err.detail || "Failed to tailor resume");
  }

  return res.json();
}

export async function exportCandidatesCSV(ranked: RankedCandidate[]): Promise<Blob> {
  const res = await fetch(`${BASE_URL}/api/export-csv`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(ranked),
  });

  if (!res.ok) {
    throw new Error("Failed to export CSV");
  }

  return res.blob();
}

export async function getLLMHealth(): Promise<{ mode: string; provider: string; model: string; reachable: boolean }> {
  try {
    const res = await fetch(`${BASE_URL}/api/llm/health`);
    if (!res.ok) return { mode: "off", provider: "groq", model: "", reachable: false };
    return res.json();
  } catch {
    return { mode: "off", provider: "groq", model: "", reachable: false };
  }
}

export async function exportTailoredPDF(resume: ParsedResume, template: string = "classic"): Promise<Blob> {
  const res = await fetch(`${BASE_URL}/api/export-pdf?template=${encodeURIComponent(template)}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(resume),
  });

  if (!res.ok) {
    throw new Error("Failed to export PDF");
  }

  return res.blob();
}
