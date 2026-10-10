# Third-Party Notices & Intellectual Property Attributions

## 1. Clean-Room Architectural Statement
In strict adherence to the project specification (PRD v0.2 Section 13) and software licensing compliance:

**Zero code, markup, styles, or binary assets were directly copied from any external reference repository.**
All modules within Noetrix—including the deterministic 6-metric scoring engine, PDF/DOCX layout parsers, ReportLab single-column resume templates, GenAI validator layer, and Next.js/Tailwind user interfaces—are original, clean-room implementations developed from scratch.

---

## 2. Architectural References & Inspirations
The following open-source projects served strictly as high-level conceptual blueprints and architectural references:

### Resume-Matcher
- **Repository:** https://github.com/srbhr/Resume-Matcher
- **License:** Apache License 2.0
- **Attribution & Usage:** Studied for vector similarity concepts and TF-IDF keyword extraction architectures. No code copied.

### OpenResume
- **Repository:** https://github.com/citrushack/open-resume
- **License:** GNU Affero General Public License v3.0 (AGPL-3.0)
- **Attribution & Usage:** Studied as a behavioral reference for ATS single-column formatting constraints and section header recognition patterns. In strict compliance with AGPL boundary isolation, **no source code, components, or styles were adapted or imported**.

### Reactive Resume
- **Repository:** https://github.com/AmruthPillai/reactive-resume
- **License:** MIT License
- **Attribution & Usage:** Studied for resume data schemas and multi-section organization concepts. No code copied.

### SmartATS & ResumeRank
- **Attribution & Usage:** Referenced for candidate ranking logic and batch recruiter workflow concepts. All scoring metrics and knockout rules were independently derived and implemented in Python.

---

## 3. Core Open-Source Dependencies & Libraries

| Dependency | License | Purpose in Noetrix |
| :--- | :--- | :--- |
| **FastAPI** | MIT | High-performance backend REST API framework |
| **Pydantic** | MIT | Deterministic data validation and JSON schema enforcement |
| **ReportLab** | BSD | Pure-Python single-column PDF document generation |
| **RapidFuzz** | MIT | Levenshtein and token-set fuzzy matching for source grounding |
| **Sentence-Transformers** | Apache 2.0 | Dense semantic embeddings (`all-MiniLM-L6-v2`) |
| **scikit-learn** | BSD 3-Clause | TF-IDF feature extraction and cosine metrics |
| **Groq Python SDK** | Apache 2.0 | Groq Cloud Generative AI client adapter |
| **Next.js** | MIT | React application framework |
| **Tailwind CSS** | MIT | Utility-first CSS design system |
| **Lucide React** | ISC | Modern UI icons |
