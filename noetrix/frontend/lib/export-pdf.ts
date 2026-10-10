import { jsPDF } from "jspdf";
import { ScoreResult } from "./types";

export function generateScoreReportPDF(result: ScoreResult): void {
  const doc = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: "a4",
  });

  const pageWidth = 210;
  const margin = 18;
  const contentWidth = pageWidth - margin * 2;

  // Background Header Bar (Warm Parchment / Deep Ink)
  doc.setFillColor(12, 15, 23);
  doc.rect(0, 0, pageWidth, 28, "F");

  // Title
  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.setTextColor(246, 239, 227);
  doc.text("NOETRIX · ATS AUDIT REPORT", margin, 18);

  doc.setFontSize(10);
  doc.setTextColor(219, 172, 240);
  doc.text("DETERMINISTIC ATS SIMULATION", pageWidth - margin - 60, 18);

  let y = 38;

  // Candidate Name & Summary
  doc.setFont("helvetica", "bold");
  doc.setFontSize(14);
  doc.setTextColor(12, 15, 23);
  doc.text(`Candidate: ${result.candidate_name}`, margin, y);

  y += 6;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(10);
  doc.setTextColor(100, 100, 100);
  doc.text(`File: ${result.filename} | Match Band: ${result.match_band.toUpperCase()}`, margin, y);

  // Score Badge
  y += 12;
  doc.setFillColor(246, 239, 227);
  doc.roundedRect(margin, y, contentWidth, 24, 3, 3, "F");

  doc.setFont("helvetica", "bold");
  doc.setFontSize(22);
  doc.setTextColor(12, 15, 23);
  doc.text(`OVERALL ATS SCORE: ${result.overall_score} / 100`, margin + 6, y + 15);

  y += 32;

  // 6 Metric Breakdown
  doc.setFont("helvetica", "bold");
  doc.setFontSize(12);
  doc.setTextColor(12, 15, 23);
  doc.text("METRIC BREAKDOWN", margin, y);

  y += 6;
  doc.setDrawColor(200, 200, 200);
  doc.line(margin, y, pageWidth - margin, y);

  y += 8;
  const metricNames: Record<string, string> = {
    keyword_match: "Hard-Skill Keyword Match (30%)",
    semantic_fit: "Semantic Narrative Fit (20%)",
    experience: "Experience Tenure & Action Verbs (20%)",
    education: "Education & Certifications (10%)",
    impact: "Impact & Quantified Achievements (10%)",
    format: "Format & ATS Readability (10%)",
  };

  doc.setFontSize(9);
  for (const [key, label] of Object.entries(metricNames)) {
    const metric = result.metrics[key];
    if (!metric) continue;

    doc.setFont("helvetica", "bold");
    doc.setTextColor(12, 15, 23);
    doc.text(`${label}:`, margin, y);

    doc.setFont("helvetica", "bold");
    if (metric.score >= 75) doc.setTextColor(16, 185, 129);
    else if (metric.score >= 50) doc.setTextColor(217, 119, 6);
    else doc.setTextColor(239, 68, 68);
    doc.text(`${metric.score}%`, margin + 85, y);

    y += 5;
    doc.setFont("helvetica", "normal");
    doc.setTextColor(80, 80, 80);
    doc.text(metric.rationale.substring(0, 110), margin + 4, y);

    y += 8;
  }

  // Priority Fixes
  y += 4;
  doc.setFont("helvetica", "bold");
  doc.setFontSize(12);
  doc.setTextColor(12, 15, 23);
  doc.text("PRIORITY FIXES", margin, y);

  y += 6;
  doc.line(margin, y, pageWidth - margin, y);

  y += 8;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(9);
  doc.setTextColor(12, 15, 23);

  result.priority_fixes.forEach((fix, idx) => {
    doc.text(`${idx + 1}. ${fix}`, margin, y);
    y += 6;
  });

  // Footer Disclaimer
  doc.setFontSize(8);
  doc.setTextColor(120, 120, 120);
  doc.text(
    "Advisory evaluation simulated by Noetrix. Scoring is deterministic with human oversight.",
    margin,
    285
  );

  doc.save(`Noetrix_Report_${result.candidate_name.replace(/\s+/g, "_")}.pdf`);
}
