"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Sparkles,
  ArrowLeft,
  Plus,
  Trash2,
  RefreshCw,
  Wand2,
  Download,
  FileDown,
} from "lucide-react";
import { ParsedResume, JDFeatures, ScoreResult, DiffItem } from "@/lib/types";
import { enhanceBullet, tailorResume, scoreResume, exportTailoredPDF } from "@/lib/api";
import DiffPreviewModal from "@/components/candidate/DiffPreviewModal";

const JUNK_KEYWORDS = new Set([
  "learning", "machine", "years", "year", "familiarity", "experience", "experienced",
  "model", "models", "qualifications", "qualification", "minimum", "relevant", "proficient",
  "proficiency", "skills", "skill", "ability", "strong", "understanding", "working",
  "knowledge", "required", "requirements", "basic", "preferred", "role", "team",
  "engineer", "engineering", "developer", "development", "work", "responsibilities"
]);

export default function CandidateEditorPage() {
  const router = useRouter();
  const [resume, setResume] = useState<ParsedResume | null>(null);
  const [jd, setJd] = useState<JDFeatures | null>(null);
  const [scoreResult, setScoreResult] = useState<ScoreResult | null>(null);

  const [isEnhancingBullet, setIsEnhancingBullet] = useState<string | null>(null);
  const [isTailoring, setIsTailoring] = useState(false);
  const [isRescoring, setIsRescoring] = useState(false);
  const [isExportingPDF, setIsExportingPDF] = useState(false);
  const [newSkillInput, setNewSkillInput] = useState("");

  // Diff Modal State
  const [isDiffOpen, setIsDiffOpen] = useState(false);
  const [pendingDiffs, setPendingDiffs] = useState<DiffItem[]>([]);
  const [pendingTailoredResume, setPendingTailoredResume] = useState<ParsedResume | null>(null);
  const [tailorGain, setTailorGain] = useState(0);
  const [tailorAfterScore, setTailorAfterScore] = useState(0);
  const [tailorAddedKeywords, setTailorAddedKeywords] = useState<string[]>([]);

  const [selectedTemplate, setSelectedTemplate] = useState<"classic" | "modern" | "compact" | "executive">("classic");

  useEffect(() => {
    const rawResume = sessionStorage.getItem("noetrix_resume") || localStorage.getItem("noetrix_resume");
    const rawJD = sessionStorage.getItem("noetrix_jd") || localStorage.getItem("noetrix_jd");
    const rawScore = sessionStorage.getItem("noetrix_score") || localStorage.getItem("noetrix_score");

    if (!rawResume || !rawJD) {
      router.push("/candidate/analyze");
      return;
    }

    try {
      setResume(JSON.parse(rawResume));
      setJd(JSON.parse(rawJD));
      if (rawScore) setScoreResult(JSON.parse(rawScore));
    } catch {
      router.push("/candidate/analyze");
    }
  }, [router]);

  if (!resume || !jd) {
    return (
      <div className="min-h-[60vh] flex items-center justify-center">
        <RefreshCw className="w-8 h-8 animate-spin text-ink/40" />
      </div>
    );
  }

  // Handle single bullet enhancement
  const handleEnhanceBullet = async (workIndex: number, bulletIndex: number) => {
    const currentBullet = resume.work_experience[workIndex].bullets[bulletIndex];
    const bulletKey = `${workIndex}-${bulletIndex}`;
    setIsEnhancingBullet(bulletKey);

    try {
      const res = await enhanceBullet(
        currentBullet,
        resume.work_experience[workIndex].title,
        scoreResult?.missing_keywords || jd.must_have_skills
      );

      const updated = { ...resume };
      updated.work_experience[workIndex].bullets[bulletIndex] = res.enhanced;
      setResume(updated);
      sessionStorage.setItem("noetrix_resume", JSON.stringify(updated));
    } catch (err) {
      console.warn("Failed to enhance bullet:", err);
    } finally {
      setIsEnhancingBullet(null);
    }
  };

  // Handle adding custom skill
  const handleAddSkill = (skillToAdd: string) => {
    const clean = skillToAdd.trim().toLowerCase();
    if (!clean || resume.skills.map((s) => s.toLowerCase()).includes(clean)) return;

    const updated = {
      ...resume,
      skills: [...resume.skills, clean],
    };
    setResume(updated);
    sessionStorage.setItem("noetrix_resume", JSON.stringify(updated));
    setNewSkillInput("");
  };

  // Handle removing skill
  const handleRemoveSkill = (skillToRemove: string) => {
    const updated = {
      ...resume,
      skills: resume.skills.filter((s) => s.toLowerCase() !== skillToRemove.toLowerCase()),
    };
    setResume(updated);
    sessionStorage.setItem("noetrix_resume", JSON.stringify(updated));
  };

  // Live Re-scoring
  const handleRescore = async () => {
    setIsRescoring(true);
    try {
      const res = await scoreResume(resume, jd);
      setScoreResult(res);
      sessionStorage.setItem("noetrix_score", JSON.stringify(res));
    } catch (err) {
      console.error("Failed to re-score resume:", err);
    } finally {
      setIsRescoring(false);
    }
  };

  // Handle full AI tailoring trigger
  const handleTriggerTailoring = async () => {
    setIsTailoring(true);
    try {
      const res = await tailorResume(resume, jd, "balanced");
      setPendingTailoredResume(res.tailored_resume);
      setPendingDiffs(res.diffs);
      setTailorGain(res.estimated_gain);
      setTailorAfterScore(res.estimated_score_after);
      setTailorAddedKeywords(res.added_keywords);
      setIsDiffOpen(true);
    } catch (err) {
      console.warn("Tailoring request did not complete:", err);
    } finally {
      setIsTailoring(false);
    }
  };

  // Commit selected diff enhancements
  const handleAcceptDiff = (selectedDiffs?: DiffItem[]) => {
    if (!pendingTailoredResume || !selectedDiffs) {
      if (pendingTailoredResume) {
        setResume(pendingTailoredResume);
        sessionStorage.setItem("noetrix_resume", JSON.stringify(pendingTailoredResume));
      }
      setIsDiffOpen(false);
      handleRescore();
      return;
    }

    const updated = { ...resume };
    selectedDiffs.forEach((d) => {
      if (d.section === "skills" && d.change_type === "added") {
        const skillsToAdd = d.modified.replace(/^Grounded from your project evidence:\s*/i, "").split(/,\s*/);
        skillsToAdd.forEach((s) => {
          const clean = s.trim().toLowerCase();
          if (clean && !updated.skills.map((sk) => sk.toLowerCase()).includes(clean)) {
            updated.skills.push(clean);
          }
        });
      } else if (d.section === "experience") {
        const match = d.item_id.match(/work_(\d+)_bullet_(\d+)/);
        if (match) {
          const wIdx = parseInt(match[1]);
          const bIdx = parseInt(match[2]);
          if (updated.work_experience[wIdx] && updated.work_experience[wIdx].bullets[bIdx] !== undefined) {
            updated.work_experience[wIdx].bullets[bIdx] = d.modified;
          }
        }
      } else if (d.section === "projects" && updated.projects) {
        const match = d.item_id.match(/proj_(\d+)_bullet_(\d+)/);
        if (match) {
          const pIdx = parseInt(match[1]);
          const bIdx = parseInt(match[2]);
          if (updated.projects[pIdx] && updated.projects[pIdx].bullets[bIdx] !== undefined) {
            updated.projects[pIdx].bullets[bIdx] = d.modified;
          }
        }
      }
    });

    setResume(updated);
    sessionStorage.setItem("noetrix_resume", JSON.stringify(updated));
    setIsDiffOpen(false);
    handleRescore();
  };

  // Export Tailored PDF
  const handleDownloadPDF = async () => {
    if (!resume) return;
    setIsExportingPDF(true);
    try {
      const blob = await exportTailoredPDF(resume, selectedTemplate);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      const cleanName = (resume.contact.name || "tailored_resume").replace(/\s+/g, "_").toLowerCase();
      a.download = `${cleanName}_${selectedTemplate}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Failed to export PDF:", err);
    } finally {
      setIsExportingPDF(false);
    }
  };

  // Export clean text representation
  const handleDownloadText = () => {
    const textLines = [
      `${resume.contact.name || "CANDIDATE"}`,
      `${resume.contact.email} | ${resume.contact.phone}`,
      "\n--- PROFESSIONAL SUMMARY ---",
      resume.summary,
      "\n--- SKILLS ---",
      resume.skills.join(", "),
      "\n--- WORK EXPERIENCE ---",
      ...resume.work_experience.map(
        (w) => `\n${w.title} at ${w.company} (${w.dates})\n` + w.bullets.map((b) => `• ${b}`).join("\n")
      ),
      "\n--- EDUCATION ---",
      ...resume.education.map((e) => `${e.degree} - ${e.institution}`),
    ];

    const blob = new Blob([textLines.join("\n")], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `Tailored_${(resume.contact.name || "Resume").replace(/\s+/g, "_")}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // Filter out generic junk from missing skills list
  const filteredMissingSkills = (scoreResult?.missing_keywords || []).filter(
    (k) => !JUNK_KEYWORDS.has(k.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto px-6 py-10 space-y-8">
      {/* Top Bar with Live Score Gauge */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 border-b border-ink-border pb-6">
        <div>
          <Link
            href="/candidate/report"
            className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-ink/60 hover:text-ink mb-2"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Audit Report</span>
          </Link>
          <h1 className="font-display text-4xl uppercase tracking-tight text-ink">
            AI RESUME EDITOR & TAILOR
          </h1>
          <p className="font-sans text-xs text-ink/60">
            Edit your bullets and watch the score change.
          </p>
        </div>

        {/* Live Score & Actions */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="flex items-center gap-2.5 bg-card-surface border-2 border-ink px-4 py-2 rounded-full shadow-sm">
            <span className="text-[11px] font-bold uppercase text-ink/60">Live ATS Score:</span>
            <span className="font-display text-2xl text-ink font-bold">
              {scoreResult?.overall_score ?? "--"}%
            </span>
          </div>

          <button
            onClick={handleRescore}
            disabled={isRescoring}
            className="flex items-center gap-2 bg-canvas hover:bg-ink/5 border-2 border-ink px-4 py-2.5 rounded-full text-xs font-bold text-ink transition-colors shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRescoring ? "animate-spin" : ""}`} />
            <span>Re-score</span>
          </button>

          <button
            onClick={handleTriggerTailoring}
            disabled={isTailoring}
            className="flex items-center gap-2 bg-accent-yellow border-2 border-ink px-4 py-2.5 rounded-full text-xs font-bold text-ink hover:bg-accent-yellow/90 transition-all shadow-sm"
          >
            <Wand2 className="w-3.5 h-3.5" />
            <span>{isTailoring ? "Reviewing..." : "Tailor Experience"}</span>
          </button>

          {/* Template Picker with ATS-Safe Badge */}
          <div className="flex items-center gap-2 bg-canvas border-2 border-ink px-3 py-1.5 rounded-full shadow-sm">
            <span className="text-[10px] font-bold uppercase text-ink/60">Template:</span>
            <select
              value={selectedTemplate}
              onChange={(e) => setSelectedTemplate(e.target.value as any)}
              className="bg-transparent text-xs font-bold text-ink outline-none cursor-pointer"
            >
              <option value="classic">Classic Academic</option>
              <option value="modern">Modern Minimal</option>
              <option value="compact">Technical Compact</option>
              <option value="executive">Executive</option>
            </select>
            <span className="inline-flex items-center gap-1 bg-accent-emerald/20 text-accent-emerald text-[9px] font-bold px-2 py-0.5 rounded-full">
              Passes our parser test
            </span>
          </div>

          <button
            onClick={handleDownloadPDF}
            disabled={isExportingPDF}
            className="flex items-center gap-2 bg-ink text-canvas border-2 border-ink px-4 py-2.5 rounded-full text-xs font-bold hover:bg-ink-slate transition-all shadow-sm"
          >
            <FileDown className="w-3.5 h-3.5 text-accent-yellow" />
            <span>{isExportingPDF ? "Generating PDF..." : "Download PDF"}</span>
          </button>

          <button
            onClick={handleDownloadText}
            className="p-2.5 border border-ink/20 rounded-full hover:bg-ink/5 text-ink/70 hover:text-ink transition-colors"
            title="Export clean text"
          >
            <Download className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Pane: Target JD and Missing Skills (4 Cols) */}
        <div className="lg:col-span-4 border-2 border-ink rounded-3xl bg-card-surface p-6 shadow-sm space-y-6">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-bold uppercase tracking-wider text-ink/60">Target Position</span>
              <span className="bg-accent-lilac/40 text-ink border border-ink text-[10px] font-bold px-2 py-0.5 rounded-full">
                Active JD
              </span>
            </div>
            <h3 className="font-display text-2xl uppercase tracking-wide text-ink">{jd.title}</h3>
          </div>

          {/* Missing Skills Quick-Add */}
          {filteredMissingSkills.length > 0 && (
            <div className="space-y-3 pt-4 border-t border-ink/10">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider text-accent-coral">
                  Missing Skills ({filteredMissingSkills.length})
                </span>
                <span className="text-[10px] text-ink/50">Click to add if experienced</span>
              </div>
              <div className="flex flex-wrap gap-1.5">
                {filteredMissingSkills.slice(0, 15).map((skill, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleAddSkill(skill)}
                    className="group inline-flex items-center gap-1 border border-accent-coral/40 bg-accent-coral/5 hover:bg-accent-coral/20 text-ink text-xs px-2.5 py-1 rounded-full transition-colors"
                  >
                    <span>+ {skill}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* JD Requirements Reference */}
          <div className="space-y-3 pt-4 border-t border-ink/10">
            <span className="text-xs font-bold uppercase tracking-wider text-ink/60 block">
              Required Must-Haves
            </span>
            <div className="flex flex-wrap gap-1.5">
              {jd.must_have_skills.map((skill, idx) => {
                const hasSkill = resume.skills.map((s) => s.toLowerCase()).includes(skill.toLowerCase());
                return (
                  <span
                    key={idx}
                    className={`text-xs px-2.5 py-1 rounded-full border font-medium ${
                      hasSkill
                        ? "bg-accent-emerald/20 border-accent-emerald text-ink"
                        : "bg-canvas border-ink/20 text-ink/60"
                    }`}
                  >
                    {hasSkill ? "✓" : "○"} {skill}
                  </span>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Pane: Resume Canvas Editor (8 Cols) */}
        <div className="lg:col-span-8 border-2 border-ink rounded-3xl bg-card-surface p-8 shadow-sm space-y-8">
          {/* Summary Section */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <label className="font-display text-xl uppercase tracking-wide text-ink">
                PROFESSIONAL SUMMARY
              </label>
              <span className="text-xs text-ink/50">Optional narrative hook</span>
            </div>

            <textarea
              value={resume.summary}
              onChange={(e) => {
                const updated = { ...resume, summary: e.target.value };
                setResume(updated);
                sessionStorage.setItem("noetrix_resume", JSON.stringify(updated));
              }}
              rows={3}
              placeholder="Brief professional summary..."
              className="w-full p-4 border border-ink/20 rounded-2xl bg-canvas/30 font-sans text-xs focus:outline-none focus:border-ink transition-all resize-y leading-relaxed"
            />
          </div>

          {/* Skills Cloud Section */}
          <div className="space-y-3 pt-6 border-t border-ink/10">
            <div className="flex items-center justify-between">
              <label className="font-display text-xl uppercase tracking-wide text-ink">
                TECHNICAL SKILLS ({resume.skills.length})
              </label>
              <span className="text-xs text-ink/50">Click tag to remove</span>
            </div>

            <div className="flex flex-wrap gap-2">
              {resume.skills.map((skill, idx) => (
                <span
                  key={idx}
                  className="group inline-flex items-center gap-1.5 bg-canvas border border-ink text-xs font-semibold px-3 py-1.5 rounded-full text-ink shadow-2xs"
                >
                  <span>{skill}</span>
                  <button
                    onClick={() => handleRemoveSkill(skill)}
                    className="hover:text-accent-coral transition-colors"
                  >
                    <Trash2 className="w-3 h-3 text-ink/40 group-hover:text-accent-coral" />
                  </button>
                </span>
              ))}
            </div>

            {/* Add Skill Input */}
            <div className="flex items-center gap-2 pt-2">
              <input
                type="text"
                value={newSkillInput}
                onChange={(e) => setNewSkillInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleAddSkill(newSkillInput)}
                placeholder="Type a skill and press Enter or Add..."
                className="px-4 py-2 border border-ink/20 rounded-full bg-canvas/40 font-sans text-xs focus:outline-none focus:border-ink flex-1"
              />
              <button
                onClick={() => handleAddSkill(newSkillInput)}
                className="bg-ink text-canvas px-4 py-2 rounded-full text-xs font-bold hover:bg-ink-slate transition-colors"
              >
                Add Skill
              </button>
            </div>
          </div>

          {/* Experience Bullets Section */}
          <div className="space-y-6 pt-6 border-t border-ink/10">
            <div className="flex items-center justify-between">
              <label className="font-display text-xl uppercase tracking-wide text-ink">
                WORK EXPERIENCE BULLETS
              </label>
              <span className="text-xs text-ink/50">Strengthen passive openings</span>
            </div>

            {resume.work_experience.map((work, wIdx) => (
              <div key={wIdx} className="border border-ink-border rounded-2xl p-6 bg-canvas/30 space-y-4">
                <div className="flex items-baseline justify-between border-b border-ink/10 pb-2">
                  <div className="font-sans font-bold text-sm text-ink">
                    {work.title} {work.company ? <span className="font-normal text-ink/60">at {work.company}</span> : null}
                  </div>
                  <span className="text-xs text-ink/50">{work.dates}</span>
                </div>

                <div className="space-y-3">
                  {work.bullets.map((bullet, bIdx) => {
                    const isEnhancing = isEnhancingBullet === `${wIdx}-${bIdx}`;

                    return (
                      <div key={bIdx} className="group relative flex items-start gap-2">
                        {/* Auto-growing Textarea */}
                        <textarea
                          value={bullet}
                          onChange={(e) => {
                            const updated = { ...resume };
                            updated.work_experience[wIdx].bullets[bIdx] = e.target.value;
                            setResume(updated);
                            sessionStorage.setItem("noetrix_resume", JSON.stringify(updated));
                          }}
                          onInput={(e) => {
                            const target = e.currentTarget;
                            target.style.height = "auto";
                            target.style.height = `${target.scrollHeight}px`;
                          }}
                          ref={(el) => {
                            if (el) {
                              el.style.height = "auto";
                              el.style.height = `${el.scrollHeight}px`;
                            }
                          }}
                          rows={2}
                          className="flex-1 p-3 border border-ink/15 rounded-xl bg-card-surface text-xs font-sans focus:outline-none focus:border-ink transition-all resize-none overflow-hidden leading-relaxed"
                        />

                        {/* Subtle action buttons on hover */}
                        <div className="flex flex-col gap-1 shrink-0 pt-1">
                          <button
                            onClick={() => handleEnhanceBullet(wIdx, bIdx)}
                            disabled={isEnhancing}
                            title="Strengthen action verb (preserves your facts)"
                            className="p-2 border border-ink/20 rounded-xl hover:bg-accent-yellow/20 text-ink/70 hover:text-ink transition-all opacity-70 group-hover:opacity-100 disabled:opacity-40"
                          >
                            <Sparkles className={`w-3.5 h-3.5 ${isEnhancing ? "animate-spin text-accent-yellow" : ""}`} />
                          </button>

                          <button
                            onClick={() => {
                              const updated = { ...resume };
                              updated.work_experience[wIdx].bullets = work.bullets.filter((_, i) => i !== bIdx);
                              setResume(updated);
                              sessionStorage.setItem("noetrix_resume", JSON.stringify(updated));
                            }}
                            title="Remove bullet"
                            className="p-2 border border-ink/20 rounded-xl hover:bg-accent-coral/20 text-ink/50 hover:text-accent-coral transition-colors opacity-70 group-hover:opacity-100"
                          >
                            <Trash2 className="w-3.5 h-3.5 mx-auto" />
                          </button>
                        </div>
                      </div>
                    );
                  })}

                  {/* Add Bullet to this role */}
                  <button
                    onClick={() => {
                      const updated = { ...resume };
                      updated.work_experience[wIdx].bullets.push("Developed core models and data pipelines.");
                      setResume(updated);
                      sessionStorage.setItem("noetrix_resume", JSON.stringify(updated));
                    }}
                    className="text-xs font-semibold text-ink/70 hover:text-ink flex items-center gap-1 pt-2"
                  >
                    <Plus className="w-3.5 h-3.5" />
                    <span>Add new bullet point</span>
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Projects Bullets Section (if present) */}
          {resume.projects && resume.projects.length > 0 && (
            <div className="space-y-6 pt-6 border-t border-ink/10">
              <div className="flex items-center justify-between">
                <label className="font-display text-xl uppercase tracking-wide text-ink">
                  PROJECT BULLETS ({resume.projects.length})
                </label>
              </div>

              {resume.projects.map((proj, pIdx) => (
                <div key={pIdx} className="border border-ink-border rounded-2xl p-6 bg-canvas/30 space-y-4">
                  <div className="flex items-baseline justify-between border-b border-ink/10 pb-2">
                    <div className="font-sans font-bold text-sm text-ink">{proj.name}</div>
                    {proj.technologies && proj.technologies.length > 0 && (
                      <span className="text-xs text-ink/50">[{proj.technologies.join(", ")}]</span>
                    )}
                  </div>

                  <div className="space-y-3">
                    {proj.bullets.map((bullet, bIdx) => (
                      <div key={bIdx} className="group relative flex items-start gap-2">
                        <textarea
                          value={bullet}
                          onChange={(e) => {
                            const updated = { ...resume };
                            updated.projects[pIdx].bullets[bIdx] = e.target.value;
                            setResume(updated);
                            sessionStorage.setItem("noetrix_resume", JSON.stringify(updated));
                          }}
                          onInput={(e) => {
                            const target = e.currentTarget;
                            target.style.height = "auto";
                            target.style.height = `${target.scrollHeight}px`;
                          }}
                          ref={(el) => {
                            if (el) {
                              el.style.height = "auto";
                              el.style.height = `${el.scrollHeight}px`;
                            }
                          }}
                          rows={2}
                          className="flex-1 p-3 border border-ink/15 rounded-xl bg-card-surface text-xs font-sans focus:outline-none focus:border-ink transition-all resize-none overflow-hidden leading-relaxed"
                        />
                        <button
                          onClick={() => {
                            const updated = { ...resume };
                            updated.projects[pIdx].bullets = proj.bullets.filter((_, i) => i !== bIdx);
                            setResume(updated);
                            sessionStorage.setItem("noetrix_resume", JSON.stringify(updated));
                          }}
                          title="Remove project bullet"
                          className="p-2 border border-ink/20 rounded-xl hover:bg-accent-coral/20 text-ink/50 hover:text-accent-coral transition-colors opacity-70 group-hover:opacity-100"
                        >
                          <Trash2 className="w-3.5 h-3.5 mx-auto" />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Diff Preview Modal */}
      <DiffPreviewModal
        isOpen={isDiffOpen}
        onClose={() => setIsDiffOpen(false)}
        onAccept={handleAcceptDiff}
        diffs={pendingDiffs}
        scoreBefore={scoreResult?.overall_score ?? 50}
        scoreAfter={tailorAfterScore}
        gain={tailorGain}
        addedKeywords={tailorAddedKeywords}
      />
    </div>
  );
}
