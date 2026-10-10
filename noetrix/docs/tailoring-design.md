# Resume Bullet Tailoring Design & Zero-Fabrication Methodology

## 1. Reference Architecture: Resume-Matcher Analysis
[Resume-Matcher (srbhr/Resume-Matcher)](https://github.com/srbhr/Resume-Matcher) is an open-source ATS analyzer and resume improver. In inspecting its backend architecture, key prompt patterns and tailoring flows emerge:

### 1.1. How the Reference Constructs Prompts
- **Prompt Structure:** Resume-Matcher passes the raw candidate resume text and target job description to LiteLLM / model providers, prompting for tailored bullet points that emphasize relevant keywords and competencies.
- **Action Verbs & Impact:** Prompts instruct the model to use strong action verbs (following the Google XYZ formula: *Accomplished [X] as measured by [Y] by doing [Z]*).
- **Keyword Alignment:** It instructs the LLM to highlight skills that bridge the gap between the candidate's existing experience and the job's mandatory requirements.

### 1.2. Output Structure
Resume-Matcher returns structured JSON containing:
- Original bullet
- Proposed tailored bullet
- Explanation / rationale of the changes made
- Targeted keywords embedded

### 1.3. How the Reference Attempts to Prevent Unsupported Claims
- In its system prompts, Resume-Matcher asks the model not to invent facts or hallucinate degrees or past positions.
- **Limitation:** In practice, relying *solely* on prompt instructions often fails with generative LLMs. Standard LLMs frequently introduce unconfirmed technologies (e.g. injecting "TensorFlow" or "CI/CD" where only Python was mentioned) and fabricate arbitrary metrics (e.g. "boosting throughput by 35%" or "serving 10,000+ users") to satisfy the XYZ metric framing requirement.

---

## 2. Conceptual Adaptations for Noetrix

In Noetrix, we conceptually adapted the best parts of Resume-Matcher's design while eliminating its hallucination vulnerabilities:

1. **Per-Bullet Atomic Rewriting:** Instead of rewriting the entire resume in one unconstrained generation, Noetrix processes bullets atomically (`one bullet per LLM call`), maintaining exact context and containment.
2. **Strict Non-Bullet Isolation:** Non-bullet lines (degree titles, job titles, companies, dates, certification headers, and inline tech stacks like `Flask · React · DistilBERT`) are strictly filtered out and never sent to the LLM.
3. **Grounded Keyword Bridging:** Instead of letting the LLM invent missing skills, Noetrix only surfaces skills that have verifiable evidence elsewhere in the candidate's portfolio (e.g., if a candidate used `DistilBERT` or `Hugging Face`, Noetrix suggests the canonical skill `transformers`).
4. **Honest Placeholder Prompts for Missing Metrics:** If a bullet lacks a quantified metric, Noetrix never invents numbers. Instead, it prompts the candidate to supply their real, verifiable metric, or keep the bullet without metrics.

---

## 3. Noetrix's Deterministic Zero-Fabrication Validator

To guarantee 100% truthful output that protects candidates during live recruitment and viva evaluations, Noetrix implements an **independent, deterministic validator** that runs *after* every LLM rewrite.

The validator does not rely on another LLM; it executes deterministic checks in Python:

### 3.1. Number & Metric Verification
- Extracts all numeric tokens, percentages, multipliers, and currency values (`extract_numbers`) from both original and proposed bullets.
- **Rule:** Every number in the rewritten bullet must exist in the original bullet or in explicit user-confirmed inputs. If the rewrite contains any new number (e.g., `35%`, `10,000+`, `$50k`), the rewrite is immediately **rejected**.

### 3.2. Unconfirmed Skill Verification
- Scans all technical taxonomy skills (`ALL_TAXONOMY_SKILLS`) in the rewrite.
- **Rule:** Any new skill present in the rewrite that was absent in the original bullet must be present in the candidate's existing profile or user-confirmed skills. Unconfirmed skills (e.g. injecting `TensorFlow` into a Scikit-Learn project) are immediately **rejected**.

### 3.3. Meaning & Polarity Preservation
- Monitors semantic action polarity pairs (e.g., `prevented`, `avoided`, `mitigated` vs. `engineered`, `caused`, `created`).
- **Rule:** Swapping a defensive or preventive action into a generative action (such as changing *"Prevented train-test leakage"* to *"Engineered train-test leakage"*) is immediately **rejected**.

### 3.4. Rejection & Fallback Behavior
- If any check fails, the AI rewrite is rejected, the original bullet is preserved untouched, and the rejection reason is logged (with zero CV text logged).
- When `LLM_MODE=off` or the LLM is unavailable, Noetrix seamlessly falls back to its deterministic rule-based weak opener optimizer (`WEAK_OPENER_REPLACEMENTS`), upgrading passive openings (`worked on`, `helped with`) to strong active verbs (`Developed`, `Architected`) without touching factual content.

---

## 4. Scoring Integrity Guarantee

- **The LLM never calculates or modifies scores.**
- After edits are accepted by the user in the interactive diff modal, the resume is re-scored exclusively by Noetrix's deterministic 6-metric ATS engine.
- The score gain shown in the UI exactly equals `post_tailored_score - baseline_score`.
