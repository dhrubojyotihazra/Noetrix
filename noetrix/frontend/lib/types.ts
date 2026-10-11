export interface ContactInfo {
  name: string;
  email: string;
  phone: string;
  location: string;
  linkedin: string;
  github: string;
  website: string;
}

export interface WorkEntry {
  id: string;
  company: string;
  title: string;
  dates: string;
  location: string;
  bullets: string[];
}

export interface EduEntry {
  id: string;
  institution: string;
  degree: string;
  field_of_study: string;
  dates: string;
  gpa: string;
  bullets: string[];
}

export interface ProjectEntry {
  id: string;
  name: string;
  role: string;
  dates: string;
  technologies: string[];
  bullets: string[];
}

export interface ParsedResume {
  filename: string;
  raw_text: string;
  contact: ContactInfo;
  summary: string;
  sections_detected: string[];
  work_experience: WorkEntry[];
  education: EduEntry[];
  skills: string[];
  projects: ProjectEntry[];
  certifications: string[];
  parse_confidence: number;
  detected_columns: number;
  has_tables: boolean;
  has_graphics: boolean;
}

export interface JDFeatures {
  title: string;
  raw_text: string;
  must_have_skills: string[];
  nice_to_have_skills: string[];
  min_experience_years: number;
  domain: string;
  responsibilities: string[];
  keywords: string[];
}

export interface MetricScore {
  score: number;
  weight: number;
  weighted_score: number;
  evidence: string[];
  missing: string[];
  rationale: string;
}

export interface ScoringConfig {
  weights: Record<string, number>;
  must_have_cap: number;
  enable_must_have_cap: boolean;
  strong_band_threshold: number;
  moderate_band_threshold: number;
}

export interface ScoreResult {
  candidate_name: string;
  filename: string;
  overall_score: number;
  raw_fit_score: number;
  is_capped: boolean;
  match_band: "strong" | "moderate" | "weak";
  metrics: Record<string, MetricScore>;
  matched_keywords: string[];
  missing_keywords: string[];
  priority_fixes: string[];
  risk_flags: string[];
  ats_sees: {
    candidate_name: string;
    email: string;
    phone: string;
    location: string;
    sections_detected: string[];
    skills_extracted_count: number;
    skills_list: string[];
    work_roles_extracted: string[];
    bullets_extracted_count: number;
    columns_detected: number;
    tables_detected: boolean;
    extraction_source?: string;
  };
}

export interface RankedCandidate {
  rank: number;
  candidate_name: string;
  filename: string;
  overall_score: number;
  match_band: "strong" | "moderate" | "weak";
  must_have_coverage: number;
  years_experience: number;
  status: "active" | "shortlisted" | "hold" | "rejected";
  risk_flags: string[];
  metrics: Record<string, MetricScore>;
  resume_summary: string;
}

export interface EnhanceBulletResponse {
  original: string;
  enhanced: string;
  keywords_included: string[];
  metrics_added: string[];
  rationale: string;
}

export interface DiffItem {
  section: string;
  item_id: string;
  change_type: "added" | "modified" | "removed";
  original: string;
  modified: string;
}

export interface TailorResumeResponse {
  tailored_resume: ParsedResume;
  diffs: DiffItem[];
  added_keywords: string[];
  bullets_enhanced_count: number;
  estimated_score_before: number;
  estimated_score_after: number;
  estimated_gain: number;
}

export interface Explanation {
  summary: string;
  strengths: string[];
  gaps: string[];
  fixes: string[];
  generated_by: string;
}

