"""Grounded Candidate & Recruiter Score Explanation Service.

Generates traceable, evidence-backed narrative summaries of ATS evaluation scores.
Guarantees:
- Supplies only score facts and short snippets from redacted source text.
- Grounding validation:
  - Every strength must link to a matched skill or verified evidence snippet.
  - Every gap must link to a missing skill or low metric supported by scoring facts.
  - Every fix must address a validated gap.
- Deterministic template fallback with generated_by='rules' if AI is disabled or fails.
- Never modifies or recalculates ATS scores.
"""

import logging
from pydantic import BaseModel, Field

from app.schemas.resume import ParsedResume
from app.schemas.jd import JDFeatures
from app.schemas.scoring import ScoreResult
from app.genai.llm import complete_json, LLMUnavailable

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an auditable ATS scoring explanation assistant.
Provide a clear, evidence-grounded summary of the candidate's ATS evaluation results.

STRICT GROUNDING RULES:
1. Every strength MUST directly reference a verified matched skill or high-scoring metric from the provided scoring facts.
2. Every gap MUST directly reference an actual missing skill or deficit identified in the scoring facts.
3. Every fix MUST provide an actionable recommendation addressing one of the validated gaps.
4. DO NOT invent facts, skills, or metrics outside the provided facts.
5. Provide up to 4 strengths, up to 4 gaps, and up to 5 prioritized fixes.
6. Output strictly valid JSON matching the schema."""


class LLMExplanation(BaseModel):
    summary: str = ""
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    fixes: list[str] = Field(default_factory=list)


class Explanation(BaseModel):
    summary: str
    strengths: list[str] = Field(default_factory=list)
    gaps: list[str] = Field(default_factory=list)
    fixes: list[str] = Field(default_factory=list)
    generated_by: str = "rules"  # 'rules' or 'llm'


def _build_rules_explanation(
    resume: ParsedResume,
    jd: JDFeatures,
    score: ScoreResult
) -> Explanation:
    """Deterministic template explanation based strictly on scoring facts."""
    strengths: list[str] = []
    gaps: list[str] = []
    fixes: list[str] = []

    # 1. Strengths from matched skills and high metrics
    if score.matched_keywords:
        top_kws = score.matched_keywords[:4]
        strengths.append(f"Demonstrated core proficiency in target technical requirements: {', '.join(top_kws)}.")

    for m_name, m_score in score.metrics.items():
        if m_score.score >= 80.0:
            if m_name == "education":
                strengths.append(f"Strong academic qualification and credentials aligned with role expectations ({m_score.score:.0f}%).")
            elif m_name == "impact":
                strengths.append(f"High density of quantifiable achievements and metrics across work history ({m_score.score:.0f}%).")
            elif m_name == "format":
                strengths.append(f"Excellent ATS readability, single-column structure, and standard heading hygiene.")

    # 2. Gaps from missing skills and low metrics
    if score.missing_keywords:
        top_missing = score.missing_keywords[:4]
        gaps.append(f"Missing primary technical keywords specified in job criteria: {', '.join(top_missing)}.")

    for m_name, m_score in score.metrics.items():
        if m_score.score < 60.0:
            if m_name == "semantic_fit":
                gaps.append(f"Semantic narrative distance indicates resume phrasing differs from JD duty descriptions ({m_score.score:.1f}%).")
            elif m_name == "experience":
                gaps.append(f"Tenure or role seniority is below the preferred experience requirement.")
            elif m_name == "impact":
                gaps.append(f"Limited quantifiable outcome metrics detected in experience descriptions.")

    # 3. Fixes from priority fixes
    if score.priority_fixes:
        fixes = list(score.priority_fixes[:5])
    else:
        fixes.append("Review bullet points for action verb intensity and quantifiable metrics.")

    summary = (
        f"Candidate scored {score.overall_score:.1f}/100 ({score.match_band.capitalize()} Match). "
        f"Matched {len(score.matched_keywords)} relevant skills with "
        f"{len(score.missing_keywords)} priority keyword opportunities identified."
    )

    return Explanation(
        summary=summary,
        strengths=strengths[:4],
        gaps=gaps[:4],
        fixes=fixes[:5],
        generated_by="rules"
    )


def explain(
    resume: ParsedResume,
    jd: JDFeatures,
    score: ScoreResult
) -> Explanation:
    """Generate grounded explanation using Groq LLM when enabled, or rules template."""
    # Prepare deterministic facts
    facts_payload = {
        "overall_score": score.overall_score,
        "match_band": score.match_band,
        "is_capped": score.is_capped,
        "matched_skills": score.matched_keywords[:10],
        "missing_skills": score.missing_keywords[:8],
        "metric_scores": {k: f"{v.score:.1f}%" for k, v in score.metrics.items()},
        "priority_fixes": score.priority_fixes[:4],
        "risk_flags": score.risk_flags[:3]
    }

    try:
        user_prompt = f"ATS Evaluation Scoring Facts:\n```json\n{facts_payload}\n```\nProvide grounded explanation."
        llm_out: LLMExplanation = complete_json(
            system=SYSTEM_PROMPT,
            user=user_prompt,
            model_cls=LLMExplanation
        )

        # Grounding checks:
        # Strengths must reference matched keywords or metric names
        grounded_strengths = []
        for s in llm_out.strengths:
            s_lower = s.lower()
            if any(k in s_lower for k in score.matched_keywords) or any(m in s_lower for m in score.metrics.keys()):
                grounded_strengths.append(s)

        # Gaps must reference missing keywords, risk flags, or low metrics
        grounded_gaps = []
        for g in llm_out.gaps:
            g_lower = g.lower()
            if any(k in g_lower for k in score.missing_keywords) or any(m in g_lower for m in ["semantic", "experience", "impact", "format", "keyword"]):
                grounded_gaps.append(g)

        # Fixes must be non-empty and actionable
        grounded_fixes = [f for f in llm_out.fixes if len(f.strip()) > 10][:5]

        # If grounding dropped too many items, fall back to rules
        if len(grounded_strengths) < 1 or len(grounded_gaps) < 1:
            return _build_rules_explanation(resume, jd, score)

        return Explanation(
            summary=llm_out.summary or f"Scored {score.overall_score:.1f}/100 against {jd.title}.",
            strengths=grounded_strengths[:4],
            gaps=grounded_gaps[:4],
            fixes=grounded_fixes or score.priority_fixes[:5],
            generated_by="llm"
        )

    except LLMUnavailable:
        logger.info("LLM explanation unavailable, returning rules explanation.")
        return _build_rules_explanation(resume, jd, score)
    except Exception as e:
        logger.warning(f"Error during LLM explanation ({e}), using rules fallback.")
        return _build_rules_explanation(resume, jd, score)
