"""Dense semantic fit scoring using Sentence Transformers (MiniLM)."""

from app.schemas.scoring import MetricScore
from app.schemas.resume import ParsedResume
from app.schemas.jd import JDFeatures
from app.nlp.embeddings import compute_semantic_similarity


def score_semantic_fit(resume: ParsedResume, jd: JDFeatures, weight: float = 0.20) -> MetricScore:
    """Compute dense semantic cosine similarity between JD narrative and resume experience/projects."""
    # Build resume context from experience bullets, summary, and projects
    resume_context_chunks = []
    if resume.summary:
        resume_context_chunks.append(resume.summary)
    for work in resume.work_experience:
        if work.title or work.company:
            resume_context_chunks.append(f"{work.title} at {work.company}")
        resume_context_chunks.extend(work.bullets)
    for proj in resume.projects:
        resume_context_chunks.append(f"Project: {proj.name}")
        resume_context_chunks.extend(proj.bullets)

    resume_text = "\n".join(resume_context_chunks)
    jd_text = jd.raw_text

    sim = compute_semantic_similarity(jd_text, resume_text)
    # PRD Formula: clamp((cos - 0.15) / 0.50) * 100
    # Maps realistic embedding cosine range [0.15, 0.65] linearly to [0%, 100%]
    mapped_ratio = max(0.0, min(1.0, (sim - 0.15) / 0.50))
    score_val = max(0.0, min(100.0, round(mapped_ratio * 100.0, 1)))

    if score_val >= 70.0:
        desc = "High semantic alignment with role responsibilities and technical narrative."
    elif score_val >= 50.0:
        desc = "Moderate contextual alignment; strong domain overlap detected."
    else:
        desc = "Low contextual alignment; resume language differs substantially from JD."

    evidence = [
        f"Contextual similarity cosine score: {round(sim, 3)} (mapped to {score_val}% via PRD clamp).",
        desc
    ]

    return MetricScore(
        score=score_val,
        weight=weight,
        weighted_score=round(score_val * weight, 2),
        evidence=evidence,
        missing=[] if score_val >= 55 else ["Tone and terminology in experience section differs from job description."],
        rationale=f"Evaluated semantic embedding distance between JD duties and candidate experience history ({score_val}% alignment)."
    )
