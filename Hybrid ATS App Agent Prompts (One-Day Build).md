# Hybrid ATS App: Agent Prompts (One-Day Build)

Owner: Jeetu · 10 Oct 2026 · Feed PRD v0.2 to each agent first, then paste that person's prompt

Six prompts, one per commit step, in the order the code lands on `main`. Dhrubojyoti has two (step 0 and step 4) because the repo skeleton must exist before Isheeka can commit, and the API can only be wired once Tiyasha's module is in.

## Commit order

| Step | Who | What lands | Commit due (hours from kickoff) |
| --- | --- | --- | --- |
| 0 | Dhrubojyoti | Repo skeleton, contracts, stubs | 0:30 |
| 1 | Isheeka | Parsing, taxonomy, sample data | 2:30 |
| 2 | Samprikta | Scoring engine and ranking | 5:00 |
| 3 | Tiyasha | LLM adapter, JD extraction, explanations, consistency flags | 7:00 |
| 4 | Dhrubojyoti | FastAPI wiring | 8:30 |
| 5 | Adhiraj | Streamlit UI | 11:00 |
| 6 | Everyone | Final test run and demo | 12:00 |

**How to use**

1. Everyone clones the repo that Dhrubojyoti creates in step 0.
2. Paste PRD v0.2 into your agent as context, then paste your prompt below.
3. Start before your turn, building against `contracts/samples/` and `data/samples/`. The deadlines are for pushing, not for starting.
4. When your tests pass: `git pull --rebase`, push to `main`, and post in the group chat: Step N done, pull main.

## Step 0: Dhrubojyoti, repo skeleton and contracts

```
You are the coding agent for Dhrubojyoti, the team lead. Context: the attached PRD v0.2. Read 'Read this first' and sections 9, 10 and 12.

Goal: create the repo skeleton so four teammates can build in parallel against fixed contracts. Time box: 30 minutes.

Tasks
1. Create the repo `ats-sim` with the folder structure in PRD section 10. Add empty __init__.py files in app/, app/parsing/, app/scoring/, app/genai/, app/api/, and a .gitkeep in docs/handoff/, tests/, ui/ and data/samples/.
2. Write contracts/schemas.py by copying the Pydantic models from PRD section 9 exactly. Do not rename or reorder fields.
3. Create contracts/samples/sample_resume.json, sample_jd.json and sample_score.json. They must validate against the schemas and use a synthetic person and a realistic data-analyst JD.
4. Create stub modules with the exact function signatures from PRD section 9 (Module interfaces) in app/parsing/__init__.py, app/scoring/__init__.py and app/genai/__init__.py. Each stub returns the matching sample object so imports and calls work today.
5. Write requirements.txt: fastapi, uvicorn, python-multipart, pydantic>=2, pdfplumber, python-docx, reportlab, scikit-learn, numpy, pandas, sentence-transformers, streamlit, requests, pytest, python-dotenv, anthropic, google-genai.
6. Write .env.example with the variables in PRD section 10, and a .gitignore (venv, .env, __pycache__, .pytest_cache, data/uploads).
7. Write README.md: setup, the four run commands, the commit order table from PRD section 12, and a folder ownership table.
8. Write tests/test_contracts.py: load each sample JSON, validate it with the matching model, and check every stub is importable.
9. Commit to main as 'chore: repo skeleton, contracts and stubs', push, and tell the group that Isheeka is next.

Definition of done: on a clean clone, `pip install -r requirements.txt && pytest tests/test_contracts.py` passes.
```

## Step 1: Isheeka, parsing, taxonomy and sample data

```
You are the coding agent for Isheeka. Context: the attached PRD v0.2. Read 'Read this first' and sections 6, 9 and 12. You are step 1; your commit is due about 2.5 hours after kickoff. Run git pull first: Dhrubojyoti's skeleton and contracts are already on main.

Your module: app/parsing/, plus data/skills_taxonomy.json and data/samples/. You turn unstructured CV and JD files into the ResumeJSON and JDJSON contracts.

Tasks
1. data/skills_taxonomy.json: at least 250 skills across data, ML, GenAI, software, cloud, BI tools and common business skills. Format: canonical name -> {synonyms: [...], category: '...'}. Include common variants (ML = Machine Learning, PowerBI = Power BI, Postgres = PostgreSQL).
2. app/parsing/extract.py: extract_text(file_bytes, filename) using pdfplumber for PDF, python-docx for DOCX (include table text) and a plain read for TXT. Also return metadata: page count, has_tables, has_images, likely_multi_column (guess from word x-positions).
3. app/parsing/sections.py: detect sections (summary, experience, education, projects, skills, certifications) from heading patterns.
4. app/parsing/parse_resume.py: parse_resume(file_bytes, filename) -> ResumeJSON. Fill contact, skills (taxonomy match including synonyms, canonical names out), experience items (title, company, start, end, bullets), education items, projects, certifications, total_experience_years (merge overlapping date ranges), parse_confidence (0 to 1, from sections found and fields filled) and parse_warnings.
5. Fill format_checks with FormatCheck items: text extractable, single column, no tables, no images, standard section headings, contact info present, length at most 2 pages. Each has a short detail.
6. redact_pii(text, contact): replace name, email, phone and links with [NAME], [EMAIL], [PHONE], [LINK]; drop lines that mention date of birth, gender, marital status, nationality or religion. Store the result in redacted_text.
7. parse_jd_rules(jd_text) -> JDJSON: title from the first line; must-have vs nice-to-have from headings (Requirements, Required, Preferred, Nice to have); skills via the taxonomy; min years via regex; education level; responsibilities. Set extraction_method to 'rules'.
8. Sample data in data/samples/: the six synthetic CVs (mix of PDF and DOCX, generated with python-docx and reportlab) and two JDs (.txt) exactly as described in PRD section 12, plus expected.json. Fake names only. Add data/samples/make_samples.py that regenerates them.
9. Tests in tests/test_parsing.py: all six CVs parse; at least 90% have skills, experience and education sections found (cv_06 may miss education); redacted_text contains no email or phone; the taxonomy has at least 250 skills; each JD yields at least 3 must-have skills.
10. Demo: `python -m app.parsing.demo` prints, per sample CV, the sections found, skills, years, parse_confidence and any failed format checks.
11. Handoff note docs/handoff/1-isheeka-parsing.md: what you built in 10 lines, how to run it, assumptions, known limits, and 3 viva questions with short answers (for example: how does a PDF become structured data, why do multi-column PDFs break parsers).
12. Commit small and often, git pull --rebase, push, then ping Samprikta.

Definition of done: PRD section 12, step 1.
```

## Step 2: Samprikta, scoring engine and ranking

```
You are the coding agent for Samprikta. Context: the attached PRD v0.2. Read 'Read this first' and sections 6, 9 and 12. You are step 2; your commit is due about 5 hours after kickoff. Run git pull first: Isheeka's parser, taxonomy and sample data should be on main. If they are not there yet, build against contracts/samples/ and your own small test objects.

Your module: app/scoring/. Input: ResumeJSON + JDJSON + Weights. Output: ScoreJSON. No LLM calls here, and scoring must be deterministic.

Tasks
1. config.py: bands (75 and 50), must-have cap (coverage below 0.5 caps the total at 50), related-skill threshold 0.60, semantic mapping constants (0.15 and 0.50), default Weights.
2. semantic.py: lazy-load all-MiniLM-L6-v2; embed(texts) and similarity(a, b). If the model cannot load, fall back to TF-IDF cosine and log one warning. Cache embeddings.
3. skills_match.py: exact matches on canonical names; related matches by skill-name embedding similarity (threshold from config). Return matched, missing and related (with similarity).
4. metrics.py: six functions exactly as the Prototype formulas in PRD section 6: keyword, semantic, experience, education, impact, format. Each returns a MetricResult with score, weight, matched/missing/related where relevant, evidence (short snippets from the CV bullets) and notes.
5. engine.py: score(resume, jd, weights) -> ScoreJSON. Normalise weights to 1, take the weighted sum rounded to one decimal, compute must_have_coverage, apply the cap, set the band, fill weights_used. Add flags: missing_section, no_metrics (warn when impact is under 20), low_parse_confidence (warn under 0.6), keyword_stuffing (warn when 8 or more skills are listed and over 60% of them never appear in experience or project text), and each missing must-have as an info flag.
6. rank(resumes, jd, weights) -> list[ScoreJSON], best first, with the tie-break order from PRD section 6 (must-have coverage, keyword score, experience score, impact score).
7. Tests in tests/test_scoring.py: same input twice gives identical output; changing weights changes the ranking in a constructed case; the cap triggers when coverage is below 0.5; evidence is non-empty for keyword and experience; the TF-IDF fallback works (monkeypatch the model loader to fail); for each JD in data/samples/expected.json the top CV ranks first and the listed bottom CVs rank in the last two.
8. Demo: `python -m app.scoring.demo` prints a 6 CVs by 2 JDs table with overall score, band and every metric.
9. If the sample test fails, tune the constants in config.py (not the formulas) and record the change in your handoff note.
10. Handoff note docs/handoff/2-samprikta-scoring.md: what you built in 10 lines, how to run it, assumptions, known limits, and 3 viva questions with short answers (why TF-IDF plus embeddings, why deterministic, what the must-have cap does).
11. Commit small and often, git pull --rebase, push, then ping Tiyasha.

Definition of done: PRD section 12, step 2.
```

## Step 3: Tiyasha, GenAI layer

```
You are the coding agent for Tiyasha. Context: the attached PRD v0.2. Read 'Read this first' and sections 6, 9, 10 and 12. You are step 3; your commit is due about 7 hours after kickoff. Run git pull first: the parser and scorer should be on main. If not, build against contracts/samples/.

Your module: app/genai/. You add the LLM-powered parts. The LLM never sets or changes a score, and everything must work with LLM_MODE=off.

Tasks
1. llm.py: complete_json(system, user, model_cls, retries=1). Read LLM_MODE, LLM_PROVIDER, LLM_MODEL and the API key from env. Support 'anthropic' and 'gemini'. Ask for JSON only, validate with the Pydantic model, retry once with a repair prompt, 15-second timeout. Raise LLMUnavailable when the mode is off, the key is missing or the call fails. Never log CV text.
2. prompts.py: short, explicit system prompts for JD extraction and for explanations (output schema, use only the facts provided).
3. jd_extract.py: extract_jd_criteria(jd_text) -> JDJSON. The LLM path returns title, must-have skills, nice-to-have skills, min years, education, domain and responsibilities. Normalise skill names to taxonomy canonical names (synonym lookup; keep unknown skills as given). On any failure fall back to parse_jd_rules and set extraction_method.
4. explain.py: explain(resume, jd, score) -> Explanation. LLM input is the ScoreJSON facts (matched, missing, related, metric scores, flags) plus short evidence snippets from redacted_text only. Output a summary, up to 4 strengths, up to 4 gaps and up to 5 concrete fixes. Grounding check: every strength must mention a matched skill or an evidence snippet, every gap a missing skill or a low-scoring metric; drop anything that does not. Fallback: a template explanation built from the same facts (generated_by='rules').
5. consistency.py: consistency_flags(resume) -> list[Flag], rule-based only: overlapping experience dates (warn), end before start (high), dates in the future (warn), employment gap over 12 months (info), duplicate bullets or entries (info), experience entries with no dates (info). Do NOT build an AI-text detector or claim verification.
6. Evaluation: write 3 extra JDs with hand-labelled must-have skills in data/samples/jd_labels.json (plus the 2 existing JDs). scripts/eval_jd_extraction.py compares rules vs LLM extraction and prints precision and recall of must-have skills. This is your demo number; the LLM column runs only when LLM_MODE=on.
7. Tests in tests/test_genai.py (LLM_MODE=off unless a key is set): extraction falls back to rules; the template explanation is grounded; consistency flags catch a crafted overlap, a future date and a gap; llm.py raises LLMUnavailable cleanly when off; a mocked LLM output that fails validation triggers one retry and then the fallback.
8. Demo: `python -m app.genai.demo` runs the three functions on a sample CV and JD.
9. Handoff note docs/handoff/3-tiyasha-genai.md: what you built in 10 lines, how to run it, assumptions, known limits, and 3 viva questions with short answers (why the LLM never sets the score, how you stop hallucinated explanations, rules vs LLM extraction results, why AI-text detection was cut).
10. Commit small and often, git pull --rebase, push, then ping Dhrubojyoti.

Definition of done: PRD section 12, step 3.
```

## Step 4: Dhrubojyoti, API wiring

```
You are the coding agent for Dhrubojyoti. Context: the attached PRD v0.2. Read 'Read this first' and sections 9, 10, 11 and 12. You are step 4; your commit is due about 8.5 hours after kickoff. Run git pull and the full test suite first. Fix only import or path problems in other people's code; for anything else, message the owner.

Your module: app/api/. Wire parsing, scoring and genai into the FastAPI service. No database: in-memory store.

Tasks
1. main.py: FastAPI app, CORS open for localhost, routes exactly as in the PRD section 10 endpoint table, response models from contracts/schemas.py.
2. store.py: in-memory dicts for jobs, resumes, scores, weights, statuses and cached explanations, with a lock for thread safety.
3. pipeline.py: the candidate and recruiter pipelines from PRD section 10. Candidate analyze: parse, extract criteria, score, add consistency flags, explain. Recruiter: score without LLM calls; generate the explanation on the first detail request and cache it. An LLM failure must never fail a request.
4. Ranking: use rank() and map to RankedRow (rank, name from contact or filename, top 3 matched, missing must-haves, flags_count, status). The weights endpoint re-ranks from stored resumes without re-parsing.
5. Validation: only .pdf, .docx and .txt; max 5 MB per file; max 30 files per job; JD of at least 50 characters; unknown job or resume returns 404; a file that fails to parse goes into `failed` and never stops the batch. All messages human-readable.
6. CSV export: rank, filename, name, overall, band, status, missing must-haves.
7. Tests in tests/test_api.py with FastAPI TestClient and the sample files (LLM_MODE=off): the full candidate flow; the full recruiter flow including re-weighting and a status change; a bad file type; an empty JD.
8. docs/api.md with a curl example per endpoint, and a run script for macOS/Linux and Windows that starts the API.
9. Check the PRD section 11 quality bar: time 1 CV, the 6 samples, and 20 copies of the samples.
10. Handoff note docs/handoff/4-dhrubojyoti-api.md: what you built in 10 lines, how to run it, assumptions, known limits, and 3 viva questions with short answers (how a CV goes from upload to result, why contracts first, how failures are contained).
11. Commit small and often, git pull --rebase, push, then ping Adhiraj with the base URL and the docs/api.md link.

Definition of done: PRD section 12, step 4.
```

## Step 5: Adhiraj, Streamlit UI

```
You are the coding agent for Adhiraj. Context: the attached PRD v0.2. Read 'Read this first' and sections 5, 8, 9, 10 and 12. You are step 5; your commit is due about 11 hours after kickoff. Run git pull first. The API is documented in docs/api.md and PRD section 10. If it is not on main yet, build against a small mock that returns contracts/samples/*.json, then switch to the real API through API_URL.

Your module: ui/ (Streamlit). Talk to the API only; never import app modules.

Tasks
1. ui/api_client.py: one function per endpoint using requests, base URL from API_URL, and clear errors that show the API's message.
2. ui/app.py: home page with a Candidate or Recruiter picker in the sidebar, a short how-scoring-works summary (six metrics and weights), and a visible notice: ATS simulation, advisory only. Add a button that loads the sample JD and CVs from data/samples/ for demos.
3. ui/pages/1_Candidate.py: CV uploader, JD text area and an Analyze button with a spinner. Report: overall score with band colour, six metric bars with their weights, skill chips (green matched, red missing, yellow related), an expander 'What the ATS sees' (sections found, extracted fields, parse confidence and warnings, format checks as pass or fail), flags grouped by severity, and the explanation (summary, strengths, gaps, top-5 fixes).
4. ui/pages/2_Recruiter.py: (a) paste a JD and show the extracted criteria in editable fields (title, must-haves, nice-to-haves, min years, education) with a save button; (b) multi-file uploader with a result line (added, failed with reasons); (c) leaderboard table (rank, name, score, band, top matched, missing must-haves, flags, status dropdown) and weight sliders that normalise to 1 and re-rank on Apply; (d) a candidate detail panel reusing the same report component; (e) CSV download.
5. ui/components.py: the shared report component used by both pages.
6. UX: spinners, empty states, friendly error messages, no stack traces, state kept in st.session_state.
7. Add a 2-minute demo script to README (the steps to click) and 2 screenshots if time allows.
8. Optional smoke test tests/test_ui_smoke.py using streamlit.testing.v1.AppTest that loads each page without error.
9. Handoff note docs/handoff/5-adhiraj-ui.md: what you built in 10 lines, how to run it, assumptions, known limits, and 3 viva questions with short answers (how the user moves through the app, how explainability is shown, why Streamlit for the prototype).
10. Commit small and often, git pull --rebase, push, then tell the group it is ready for the final test run.

Definition of done: PRD section 12, step 5.
```

## Step 6: everyone, final test run

- Fresh clone on one laptop: install, start the API, start the UI, run `pytest`.
- Run both flows with `LLM_MODE=off`, then with `on` if a key is set.
- Each owner fixes bugs in their own module only; freeze `main` at the deadline.
- Rehearse the 2-minute demo; each person explains their module with their handoff note.
