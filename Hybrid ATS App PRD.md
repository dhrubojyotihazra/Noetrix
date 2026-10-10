# Hybrid ATS Scorer & Ranker: Product Requirements Document

Owner: Jeetu · Version 0.1 (draft) · 9 Oct 2026 · Working title (no product name chosen yet)

## 1. Summary

One app, two doors. A **candidate** pastes a job description, uploads or fills in their CV, and gets an ATS-style score with a per-metric breakdown and a fix list. A **recruiter** pastes a job description, uploads a batch of CVs, and gets an explainable ranked shortlist. Both doors run on the same scoring engine.

This is an **ATS simulation**, not a copy of Workday, Taleo or any other vendor. Vendors do not publish their scoring logic, so we never claim exact vendor scores.

## 2. Problem and goals

**Problem**

- Candidates get filtered out without knowing whether the cause was keywords, formatting or experience fit.
- Recruiters receive hundreds of CVs per role and screen them inconsistently.
- Open-source tools usually cover one side only (candidate checker or recruiter ranker), rarely both on one engine.

**Goals**

- G1: Give candidates a transparent score, a metric breakdown and concrete fixes.
- G2: Give recruiters a ranked shortlist where every rank can be explained.
- G3: Use one deterministic scoring engine for both sides.
- G4: Keep a human in the loop. Ranking is advisory and never auto-rejects.

**Non-goals (v1)**

- Replicating any specific commercial ATS.
- A CV builder or AI CV rewriter (v1 gives fixes, not rewrites).
- Job board, interview scheduling, video screening.
- Billing and multi-organisation admin.

## 3. Users

- **Candidate:** students, freshers and job-switchers who want to check a CV against one specific JD before applying.
- **Recruiter:** small-company HR and campus placement cells who need to shortlist from big CV batches fast and justify the order.

## 4. Reference repositories: what we steal from each

Star and fork counts were read from each repo's GitHub page on 9 Oct 2026.

| Repo | Stars | Forks | License | Maturity signal | Main thing we take |
| --- | --- | --- | --- | --- | --- |
| [srbhr/Resume-Matcher](https://github.com/srbhr/Resume-Matcher) | 28.3k | 5.0k | Apache-2.0 | 1,469 commits | Overall product flow, scoring UI, LLM adapter |
| [xitanggg/open-resume](https://github.com/xitanggg/open-resume) | 8.9k | 1.0k | AGPL-3.0 | 95 open issues | 'What the ATS sees' parser view, format rules |
| [Rudra-P9/ATSify](https://github.com/Rudra-P9/ATSify) | 0 | 0 | MIT | 59 commits, new | Modular scorer, staged pipeline, red-flag checks |
| [saber-030/SmartATS](https://github.com/saber-030/SmartATS) | 0 | 0 | None shown | 2 commits | Recruiter side: weights, ranking, tie-breaks, status |
| [ramlasyaa/ResumeRank](https://github.com/ramlasyaa/ResumeRank) | 0 | 0 | None shown | 1 commit | TF-IDF + embedding matching, CSV export |

**Read this honestly:** only the top two have real community traction. The bottom three have zero stars and almost no history, so we treat them as design blueprints and write and test our own code. For repos with no license shown, do not copy code.

### 4.1 Resume-Matcher

- **Link:** https://github.com/srbhr/Resume-Matcher
- **Stars / forks / license:** 28.3k / 5.0k / Apache-2.0
- **Stack:** FastAPI (Python) backend, Next.js frontend, TinyDB storage, LiteLLM for multiple model providers, Playwright for PDF export.
- **What we steal**
  - **Master resume:** one saved profile reused for every job. This becomes our Profile page.
  - **Upload, paste JD, review flow:** the candidate flow in section 7 follows it.
  - **Scoring with keyword highlighting:** our report highlights matched and missing keywords inline.
  - **Model-provider adapter:** support local models (Ollama) and cloud providers through one interface.
  - **Repo layout and Docker deploy:** separate backend and frontend apps, one-command container run.
- **What we skip:** cover-letter and rewrite generation (out of scope for v1), and TinyDB (we need SQL for recruiter queries).

### 4.2 OpenResume

- **Link:** https://github.com/xitanggg/open-resume
- **Stars / forks / license:** 8.9k / 1.0k / AGPL-3.0
- **Stack:** Next.js, TypeScript, Redux Toolkit, PDF.js for reading PDFs.
- **What we steal**
  - **Parser-as-a-test:** its parser page helps users confirm ATS readability. We build a 'What the ATS sees' panel showing the sections and fields we extracted, and what got lost.
  - **Parsing approach:** PDF text extraction, then section detection. Its author documents the algorithm at open-resume.com/resume-parser; we study it and write our own.
  - **ATS-friendly format rules:** single column, standard fonts, consistent bullets and margins feed our Format health checks.
  - **Privacy posture:** runs fully in the browser with no data leaving it. This inspires an optional local mode.
- **What we skip:** the code itself. AGPL requires source disclosure for network-hosted derivatives, so we reimplement ideas and never copy code.

### 4.3 ATSify

- **Link:** https://github.com/Rudra-P9/ATSify
- **Stars / forks / license:** 0 / 0 / MIT (59 commits)
- **Stack:** React 19, TypeScript, Vite, Firebase, Gemini.
- **What we steal**
  - **Modular scorer:** separate keyword, format, experience, education and section modules. Our engine mirrors this split.
  - **Staged pipeline:** parse, then NLP (TF-IDF + skills taxonomy), then LLM metadata extraction, then deterministic scorer, then report. The LLM only extracts structure; scoring stays deterministic and repeatable.
  - **Red-flag scanner:** future-dated entries, missing quantified achievements, formatting hazards.
  - **Per-platform rule sets:** Workday, Taleo, iCIMS, Greenhouse, Lever, SuccessFactors. Our v2 'ATS profile' toggle adjusts rule strictness. We label these heuristics.
  - **Report UX:** expandable focus areas (formatting, experience quality, section structure), scan history, PDF report export.
- **Caveat:** zero traction, and its claim to reverse-engineer real vendor logic is unverified. We do not repeat that claim.

### 4.4 SmartATS

- **Link:** https://github.com/saber-030/SmartATS
- **Stars / forks / license:** 0 / 0 / none shown (2 commits)
- **Stack:** Python 3.10+, Streamlit, SQLite, Pydantic.
- **What we steal (our main recruiter-side blueprint)**
  - **Job intake:** upload or paste a JD, then review and edit extracted skills, responsibilities and requirements.
  - **Two-part scoring:** Fit (must-have skills 40, experience 30, domain 20, location 10) and Excellence (education 25, career trajectory 25, achievements 25, skills depth 25), combined 70/30 by default.
  - **Must-have cap:** missing must-have skills cap the fit score at 50.
  - **Per-job weights** with automatic re-scoring on save.
  - **Tie-break order:** must-have coverage, then domain match, then career trajectory, then achievements.
  - **Explainable rankings** with risk flags, plus candidate status (active, advanced, rejected, withdrawn).
  - **Code layout:** typed data models, separate JD parser, CV parser, scoring and ranking modules, and a skills taxonomy JSON file.
- **Caveat:** two commits and no visible license. Design reference only.

### 4.5 ResumeRank

- **Link:** https://github.com/ramlasyaa/ResumeRank
- **Stars / forks / license:** 0 / 0 / none shown (1 commit)
- **Stack:** Python, scikit-learn, sentence-transformers (all-MiniLM-L6-v2), PyPDF2, python-docx, pandas.
- **What we steal**
  - **Two matchers:** TF-IDF with unigrams and bigrams for keyword overlap, and 384-dimension MiniLM embeddings for semantic similarity. These become our Keyword and Semantic metrics.
  - **Match bands** shown next to each score (strong, moderate, weak).
  - **CSV export** of the ranked table and a top-N filter.
  - **Single config file** for method, thresholds and top-N.
- **Caveat:** one commit, tiny. Design reference only.

## 5. Features

Priority: P0 = MVP, P1 = soon after, P2 = later.

**Candidate side**

| ID | Feature | Pri | Inspired by |
| --- | --- | --- | --- |
| C1 | Sign up, choose Candidate role | P0 | n/a |
| C2 | Profile: upload CV (PDF/DOCX) or fill a form, then confirm parsed fields | P0 | Resume-Matcher, OpenResume |
| C3 | Paste a job description (URL import later) | P0 | Resume-Matcher, ATSify |
| C4 | Overall score plus six-metric breakdown | P0 | ATSify, ResumeRank, SmartATS |
| C5 | Keyword gap view with matched and missing terms highlighted | P0 | Resume-Matcher |
| C6 | 'What the ATS sees' parse preview | P0 | OpenResume |
| C7 | Format health checks | P0 | OpenResume, ATSify |
| C8 | Top-5 prioritised fix list | P0 | Resume-Matcher, ATSify |
| C9 | Red flags (future dates, no metrics, missing sections) | P1 | ATSify |
| C10 | Edit and re-score with before/after | P1 | Our own |
| C11 | Scan history | P1 | ATSify |
| C12 | PDF report export | P2 | ATSify |
| C13 | ATS profile toggle (Workday, Greenhouse and others) | P2 | ATSify |

**Recruiter side**

| ID | Feature | Pri | Inspired by |
| --- | --- | --- | --- |
| R1 | Sign up, choose Recruiter role | P0 | n/a |
| R2 | Create job: paste JD, auto-extract must-haves, nice-to-haves, minimum experience, then edit | P0 | SmartATS |
| R3 | Weights and must-have knockout rules per job | P0 | SmartATS |
| R4 | Bulk CV upload and parsing | P0 | SmartATS, ResumeRank |
| R5 | Ranked leaderboard with score bands | P0 | SmartATS, ResumeRank |
| R6 | Candidate detail with score breakdown, evidence snippets and flags | P0 | SmartATS |
| R7 | Status: Shortlist, Hold, Reject | P0 | SmartATS |
| R8 | Auto re-rank when weights change | P0 | SmartATS |
| R9 | CSV export | P1 | ResumeRank |
| R10 | Side-by-side candidate compare | P2 | Our own |
| R11 | Apply link: candidates self-check, then apply into the recruiter's list | P2 | Our hybrid hook |

**Platform**

| ID | Feature | Pri | Inspired by |
| --- | --- | --- | --- |
| P1 | Skills taxonomy file (skills, synonyms, domains) | P0 | SmartATS, ATSify |
| P2 | Delete my data and delete this job | P0 | Our own |
| P3 | Model adapter: local or cloud LLM, optional | P1 | Resume-Matcher |
| P4 | Docker deployment | P1 | Resume-Matcher, OpenResume |

## 6. Scoring engine spec

**Pipeline:** ingest file, extract text, detect sections, normalise, (optional LLM extraction into a fixed schema), deterministic scoring, explanation. The LLM never produces the score. Same input gives the same score.

**Six metrics (default weights)**

| Metric | Weight | How it is computed |
| --- | --- | --- |
| Hard-skill keyword match | 30% | Skills taxonomy match plus TF-IDF overlap with the JD, with synonyms and partial credit |
| Semantic fit | 20% | Cosine similarity of MiniLM embeddings between JD and the CV's experience and project text |
| Experience | 20% | Years versus JD minimum with partial credit, plus title relevance |
| Education and certifications | 10% | Degree level and field match, relevant certifications |
| Impact | 10% | Share of bullets with quantified results (%, numbers, scale) |
| Format and parse health | 10% | Sections detected, contact info found, single column, standard headings, sensible length |

**Candidate view:** weights fixed at defaults, so scores are comparable across scans.

**Recruiter view:** same six metrics with per-job editable weights, plus:

- **Must-have rule:** a missing must-have skill caps the total score at 50 (adapted from SmartATS).
- **Tie-breaks:** must-have coverage, then domain match, then experience, then impact.
- **Bands:** strong, moderate, weak. Thresholds are proposed and must be calibrated on real data (see section 11).

**Explainability contract:** every metric returns a score, the evidence it used (snippets), and what is missing. No rank without a reason.

**Fairness rules**

- Name, gender, age or date of birth, photo, marital status, nationality and religion are removed before scoring.
- Education is scored on degree level and field, not institution prestige.
- Cap the contribution of any single repeated keyword, and flag keyword stuffing or hidden text.
- The recruiter UI always shows that the ranking is advisory.

## 7. User flows

**Candidate**

1. Sign up and choose Candidate.
2. Upload a CV or fill the form, then confirm the parsed fields.
3. Paste the job description.
4. Press Analyze.
5. Report: overall score, six-metric breakdown, matched and missing keywords, 'What the ATS sees' preview, top-5 fixes.
6. Edit the CV, re-score, compare before and after.
7. Revisit past scans in History.

**Recruiter**

1. Sign up and choose Recruiter.
2. New job: paste the JD, review the extracted criteria, edit them.
3. Set weights and must-have rules.
4. Upload CVs in bulk.
5. Parse and score, then see the ranked leaderboard.
6. Open a candidate to see the breakdown, evidence and flags.
7. Mark Shortlist, Hold or Reject, then export CSV.
8. Change weights and the list re-ranks.

**Hybrid hook (P2):** the recruiter shares an apply link that opens the candidate flow with the JD pre-filled. Applicants see their own score and apply, and land in the recruiter's list.

## 8. Sitemap

```
/
├─ /login  /signup
├─ /how-scoring-works
├─ /candidate
│  ├─ /dashboard
│  ├─ /profile
│  ├─ /analyze
│  ├─ /report/:id
│  └─ /history
└─ /recruiter
   ├─ /dashboard
   └─ /jobs
      ├─ /new
      └─ /:jobId
         ├─ /setup
         ├─ /candidates
         └─ /candidates/:id
```

## 9. Data model (core entities)

- **User:** id, role (candidate or recruiter), email.
- **Resume:** owner, file, raw text, parsed JSON (sections, skills, experience, education), parse confidence.
- **JobDescription:** owner, raw text, extracted criteria (must-haves, nice-to-haves, minimum experience, domain), weights.
- **Analysis (candidate):** resume, JD, per-metric scores, evidence JSON, engine version, timestamp.
- **RankedCandidate (recruiter):** job, resume, total score, per-metric scores, flags, status.
- **ScoringConfig:** weights, thresholds, bands, versioned so old scores stay reproducible.

## 10. Proposed architecture and stack

- **Backend:** FastAPI with Pydantic schemas; SQLite for MVP, Postgres later.
- **Parsing:** pdfplumber and python-docx, with PyMuPDF as a fallback.
- **NLP:** scikit-learn TF-IDF, sentence-transformers (all-MiniLM-L6-v2), skills\_taxonomy.json.
- **LLM (optional):** schema-constrained extraction only, through a provider adapter that supports local Ollama.
- **Frontend:** Next.js and Tailwind (the Resume-Matcher pattern). Streamlit is a faster fallback for the first prototype.
- **Deploy:** Docker.

## 11. Non-functional requirements and success metrics

**Targets (proposed, adjust after the first prototype)**

- Score one CV in under 10 seconds without an LLM call; rank 100 CVs in under 60 seconds.
- Deterministic: same CV, JD and config always give the same score.
- Privacy: users can delete files and results; uploads are not used for anything else.
- Parse success: at least 90% of a 50-CV test set has experience, education and skills sections detected.
- Quality: rank correlation (Spearman) of at least 0.6 between engine ranking and human ranking on a labelled set of 30 to 50 CV/JD pairs.
- Candidate value: median score gain of 10+ points after applying the top-5 fixes.
- Recruiter value: shortlist from 50 CVs in under 5 minutes.

## 12. Roadmap (indicative)

- **Phase 0 (week 1):** read and map the five repos, check licenses, set up the repo and the labelled test set.
- **Phase 1 (weeks 2-3):** parsing plus scoring engine core, with tests against the test set.
- **Phase 2 (weeks 4-5):** candidate flow and report UI.
- **Phase 3 (weeks 6-7):** recruiter flow, leaderboard, status and export.
- **Phase 4 (week 8):** calibration, fairness checks, polish, Docker deploy.
- **Later:** ATS profiles, apply link, PDF reports, OCR for scanned CVs, URL import for JDs.

## 13. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Users believe scores equal real ATS results | Label everything 'ATS simulation' and publish how scoring works |
| Three of five reference repos have no traction | Treat as blueprints; write our own tests and calibrate on a labelled set |
| AGPL (OpenResume) or missing license (SmartATS, ResumeRank) | Reimplement ideas only; no code copied from them |
| Bias and regulation: hiring-ranking tools are regulated in some places (for example EU AI Act high-risk rules, NYC Local Law 144 bias audits) | Human in the loop, protected attributes removed, audit log; verify current rules before real hiring use (this is not legal advice) |
| Parsing failures on scanned or multi-column PDFs | Show parse confidence and the 'What the ATS sees' panel; OCR in a later phase |
| LLM output varies between runs | LLM only extracts into a fixed schema; scoring is deterministic |
| Keyword stuffing | Per-keyword cap, repeated-text and hidden-text detection |

## 14. Open questions

- MVP frontend: Next.js or Streamlit?
- Local-first (no accounts) or hosted with accounts?
- Primary segment: campus placement cells or small-company HR?
- Is the apply link needed for the first demo?
- Product name?
