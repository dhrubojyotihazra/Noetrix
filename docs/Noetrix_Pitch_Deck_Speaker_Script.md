# 🎙️ Noetrix Capstone Presentation — Complete Speaker Script

**Project Title:** Noetrix: Explainable Resume Screening and Tailoring with Guardrailed Generative AI  
**Institution:** Brainware University | Dept. of CSE (CS & DS) | Oct 2026  
**Industry Partner:** Ardent Computech Pvt. Ltd. | Mentor: Mr. Mahendra Dutta  
**Live URL:** [https://noetrix-virid.vercel.app](https://noetrix-virid.vercel.app)  
**Total Presentation Time:** ~8 to 10 minutes (~45–60 seconds per slide)

---

## 👥 Speaker Roster & Slide Assignment

| Speaker | Assigned Slides | Topics Covered |
| :--- | :--- | :--- |
| **Adhiraj Das** | **Slides 1, 2, 3** | Introduction, Agenda, Problem Statement, Solution & Outcomes |
| **Isheeka Mukhopadhyay** | **Slides 4, 5** | Core Engineering Pillars, Dual Portal (Candidate & Recruiter Doors) |
| **Samprikta De** | **Slides 6, 7** | 6-Metric Scoring Engine, Must-Have Cap, 4-Stage Architectural Pipeline |
| **Tiyasha Baidya** | **Slides 8, 9** | Guardrailed Tailoring, Zero-Fabrication Validator, Production Tech Stack |
| **Dhrubojyoti Hazra (Dhrubo)** | **Slides 10, 11, 12, 13** | Benchmarks, Empirical Results (71/71 Tests), Team Credits, Live Demo & Q&A |

---

## 🎬 Section 1: Adhiraj Das (Slides 1 – 3)

### Slide 1: Title Slide
**Visual on screen:** Noetrix logo, project title, student names, mentor, and Brainware University logo.

> *"Respected mentor Mr. Mahendra Dutta, faculty members, and fellow classmates — a very warm good morning.*
>
> *I am **Adhiraj Das**, and today my team and I are proud to present our capstone engineering project: **Noetrix** — an explainable resume screening and tailoring platform powered by guardrailed generative AI.*
>
> *This project was built under the guidance of our industry mentor at Ardent Computech Pvt. Ltd., developed by our team: Dhrubojyoti Hazra, Isheeka Mukhopadhyay, Samprikta De, myself Adhiraj, and Tiyasha Baidya.*
>
> *Let us walk you through how Noetrix solves one of the most frustrating bottlenecks in modern hiring."*

---

### Slide 2: Agenda
**Visual on screen:** Clean 8-item agenda table mapping all 13 slides.

> *"Here is how we have structured today’s presentation:*
>
> *We will start with the real-world problem and our overarching solution. Then, we will explore our two user portals — one for candidates and one for recruiters.*
>
> *Next, we will break down the mathematical engine that scores resumes, how we guard against AI hallucinations during resume tailoring, our modern cloud tech stack, and our empirical benchmarks.*
>
> *Finally, we will present our test results, introduce each team member’s role, and show you our live deployed application.*
>
> *Let us dive right into the core idea of Noetrix."*

---

### Slide 3: Overview (Problem, Solution & Outcome)
**Visual on screen:** Three cards: 01 The Problem, 02 The Solution, 03 The Outcome, plus the live link `noetrix-virid.vercel.app`.

> *"Today, traditional Applicant Tracking Systems (ATS) are essentially black boxes. Qualified job seekers are rejected by rigid keyword filters without ever knowing why. On the other hand, candidates who cheat by stuffing invisible white keywords often rank at the very top, while generative AI screeners introduce unpredictable score jitter and hallucinations.*
>
> *Noetrix solves this by replacing the black box with a **transparent, dual-sided platform**.*
>
> *We combine a **100% deterministic 6-metric scoring engine** with **strictly guardrailed AI tailoring**.*
>
> *The outcome? Fully reproducible scores with zero score jitter, lightning-fast processing at **42.4 milliseconds per resume**, and **zero server-side data retention** — keeping candidate data completely safe in their browser session.*
>
> *Now, I would like to invite **Isheeka** to walk us through our engineering objectives and portals."*

---

## 🎬 Section 2: Isheeka Mukhopadhyay (Slides 4 – 5)

### Slide 4: Objectives and Goals
**Visual on screen:** Three pillar cards: Auditable Scores, Zero Fabrication, and Privacy by Design.

> *"Thank you, Adhiraj.*
>
> *Hello everyone, I am **Isheeka Mukhopadhyay**. To build Noetrix, our team focused on three core engineering pillars:*
>
> *First, **Auditable Scores**: Every single score must have clear mathematical evidence behind it. We decomposed scoring into six weighted dimensions and introduced a 50-point soft knockout cap to stop under-qualified or gaming profiles.*
>
> *Second, **Zero Fabrication**: While AI is great at writing, it is notorious for inventing fake facts. Our system restructures bullet points into Google's proven XYZ format — Accomplished [X], Measured by [Y], by doing [Z] — while an automated validator strictly blocks any invented skills, fake numbers, or company changes.*
>
> *Third, **Privacy by Design**: Candidates shouldn't have to surrender their personal data to test a resume. Noetrix redacts personal contact information before any AI processing, runs stateless in-memory sessions, and stores zero resumes on the server."*

---

### Slide 5: Dual Portal Architecture
**Visual on screen:** Candidate Door vs Recruiter Door illustrations and features.

> *"To serve both sides of the hiring table, Noetrix is built with two distinct doors:*
>
> *The **Candidate Door** is designed for the job seeker. A candidate uploads their resume and pastes a target job description. Instantly, they see exactly what the ATS sees — their exact score breakdown, matched and missing keywords, format health warnings, and suggested bullet rewrites that they can accept or reject with one click.*
>
> *The **Recruiter Door** is designed for hiring teams. Recruiters can drag and drop batches of dozens of resumes at once, customize the weights to fit the role, and immediately receive a ranked leaderboard with transparent tie-breaking telemetry and candidate dossiers.*
>
> *Now, let us examine the mathematical engine under the hood. I will hand over to **Samprikta**."*

---

## 🎬 Section 3: Samprikta De (Slides 6 – 7)

### Slide 6: Scoring Engine (Weights, Cap & Tie-Breaker)
**Visual on screen:** The 6-metric breakdown table (30%, 20%, 20%, 10%, 10%, 10%), Must-Have Cap, and Tie-breaking rule.

> *"Thank you, Isheeka. Hello everyone, I am **Samprikta De**.*
>
> *In Noetrix, **the AI never assigns a numerical score**. Instead, every score is calculated by our deterministic scoring engine across six auditable dimensions:*
>
> *1. **Keyword Match (30%)**: Checks technical taxonomy skills. To stop keyword stuffing, skills found only in a list without context receive discounted 0.5 credit.*  
> *2. **Semantic Fit (20%)**: Uses dense sentence embeddings to measure overall contextual meaning.*  
> *3. **Experience & Seniority (20%)**: Evaluates role duration, career trajectory, and strong action verbs.*  
> *4. **Education Alignment (10%)**: Checks degree level without university prestige bias.*  
> *5. **Quantified Impact (10%)**: Rewards measurable metrics, percentages, and dollar impact.*  
> *6. **ATS Format Hygiene (10%)**: Checks for single-column layout, standard headings, and clean parsability.*
>
> *Crucially, we enforce a **50-Point Must-Have Knockout Cap**: If a candidate covers fewer than 50% of the job's mandatory requirements, their total score is capped at 49.0 in the weak band, regardless of their other scores.*
>
> *And if candidates tie, our engine uses a 6-tier deterministic tie-breaker: Composite Score, then Must-Have Coverage, then Keywords, Experience, Impact, and finally arrival order."*

---

### Slide 7: How It Works (The 4-Stage Pipeline)
**Visual on screen:** 4 connected stages: 1. Ingest, 2. Score, 3. Guard, 4. Rank.

> *"Here is how that workflow runs in practice, from raw upload to ranked dossier, in four clean stages:*
>
> *Stage 1 is **Ingest**: Our parser ingests PDF, DOCX, or text files, extracting sections, dates, contact details, and bullet points while flagging multi-column tables that might break legacy scanners.*
>
> *Stage 2 is **Score**: The resume is evaluated across our 6 metrics, extracting embeddings locally via MiniLM and checking the 50% must-have threshold.*
>
> *Stage 3 is **Guard**: Before any tailoring suggestions are generated, all PII like phone numbers and emails are redacted. Any proposed rewrite is rigorously checked by our Zero-Fabrication Validator.*
>
> *Stage 4 is **Rank**: For recruiters, resumes are sorted onto an auditable leaderboard with candidate dossiers and one-click PDF/CSV export.*
>
> *To explain how our generative AI guardrails work, I'll pass the microphone to **Tiyasha**."*

---

## 🎬 Section 4: Tiyasha Baidya (Slides 8 – 9)

### Slide 8: Guardrailed Tailoring (Zero-Fabrication Validator)
**Visual on screen:** Google XYZ rewrite diagram, validation checklist (Numbers, Skills, Titles, Meaning Reversal).

> *"Thank you, Samprikta. Good morning everyone, I am **Tiyasha Baidya**.*
>
> *When job seekers use tools like ChatGPT to polish their resumes, the AI frequently hallucinates — inventing metrics like 'increased sales by 40%' that the candidate never achieved. This damages candidate integrity.*
>
> *In Noetrix, resume tailoring is strictly guardrailed:*
>
> *First, we prompt the LLM to rewrite weak passive openers into strong Google XYZ statements — for example, turning 'Worked on building recommendation system' into 'Built recommendation system using PyTorch'.*
>
> *Immediately after the LLM responds, our **deterministic Zero-Fabrication Validator** inspects the output. It checks five non-negotiable rules:*
> *• Did the rewrite add any new number not in the original? **Rejected.***  
> *• Did it drop or mutate existing numbers? **Rejected.***  
> *• Did it inject unconfirmed skills or alter job titles? **Rejected.***  
> *• Did it reverse the meaning of the bullet? **Rejected.***  
>
> *If any check fails, the system safely falls back to our rule-based active verb lemma engine. Most importantly, the human stays in control: the candidate gets a clean side-by-side diff view to accept or decline each change."*

---

### Slide 9: Production Tech Stack
**Visual on screen:** Three cards: Frontend (Next.js 15, React 19), Backend & NLP (FastAPI, Docker), GenAI (Groq LLaMA, temp 0).

> *"To bring this platform to life, we designed a decoupled, cloud-native three-tier architecture:*
>
> *On the **Frontend**, we use **Next.js 15.1** with **React 19**, TypeScript, and Tailwind CSS, deployed on Vercel's global edge network. This gives us lightning-fast page loads and responsive, accessible UI components.*
>
> *On the **Backend**, we run a high-performance **FastAPI** service packaged in Docker on Render. For NLP, we rely on `pdfplumber`, `python-docx`, Sentence-Transformers for semantic embeddings, scikit-learn for TF-IDF keyword extraction, and ReportLab for producing ATS-compliant PDFs.*
>
> *For **Generative AI**, we integrate with the **Groq cloud** using LLaMA 3.3 70B and LLaMA 3.1 8B at temperature zero. Every request uses strict Pydantic schemas, thread-safe in-memory SHA-256 caching, automatic rate-limit backoff, and 100% deterministic offline fallback if the API is offline.*
>
> *Now, our project lead **Dhrubo** will share our benchmark comparisons, test results, and demonstrate the live platform."*

---

## 🎬 Section 5: Dhrubojyoti Hazra (Slides 10 – 13)

### Slide 10: Comparative Benchmarks
**Visual on screen:** Comparison of Legacy ATS vs Pure LLM Screening vs Noetrix Hybrid.

> *"Thank you, Tiyasha. Good morning everyone, I am **Dhrubojyoti Hazra**.*
>
> *To validate Noetrix, we ran head-to-head benchmark experiments against legacy keyword ATS platforms and pure LLM screeners:*
>
> *• **Legacy Keyword ATS**: When we fed an adversarial resume packed with a giant list of technical keywords but zero real experience, legacy tools awarded it an astounding **94.2% match**. They were completely fooled.*  
> *• **Pure Zero-Shot LLM**: When we asked an LLM alone to score resumes, it suffered from severe non-determinism — showing an **8.4-point score variance** on the exact same resume across runs.*  
> *• **Noetrix**: Our hybrid architecture shut down both vulnerabilities. The keyword-stuffed resume was penalized and capped in the weak band because it lacked contextual proof outside the skills list. And because our scoring formulas are deterministic math, our score variance across repeated runs was **exactly 0.0** — identical results every single time."*

---

### Slide 11: Empirical Results & Verification
**Visual on screen:** Three big metric badges: 100% Reproducible, 42.4 ms Per Resume, 71/71 Tests Passed.

> *"Our empirical verification confirms three key engineering milestones:*
>
> *First, **100% Score Reproducibility**: Zero score drift and zero variance across repeated runs, making hiring audits completely trustworthy.*
>
> *Second, **Sub-50 Millisecond Latency**: Evaluating a resume takes an average of just **42.4 milliseconds on standard CPU**. In our batch testing, 20 resumes were completely parsed, scored, and ranked in under 0.9 seconds.*
>
> *Third, **Robust Test Suite**: We have implemented **71 automated unit, integration, guardrail, and security tests** in `pytest`. All 71 tests pass with a 100% success rate, verifying everything from CSV formula injection protection to ATS PDF recyclability and PII redaction."*

---

### Slide 12: Engineering Team
**Visual on screen:** Team member cards with roles, student IDs, and Industry Mentor acknowledgement.

> *"This project was a collaborative effort where each team member owned critical engineering modules:*
>
> *• **Adhiraj Das** engineered our bullet tailoring, diff generation, and ATS PDF export.*  
> *• **Isheeka Mukhopadhyay** led our document parsing, multi-column detection, and layout hygiene analysis.*  
> *• **Samprikta De** developed the 6-metric scoring core, the must-have cap, and recruiter batch ranking.*  
> *• **Tiyasha Baidya** spearheaded GenAI guardrails, PII redaction, and fairness evaluation.*  
> *• And **I** served as project lead, directing system architecture, API design, and full-stack cloud deployment.*
>
> *We extend our sincere gratitude to our mentor, **Mr. Mahendra Dutta** from Ardent Computech Pvt. Ltd., for his invaluable industry guidance throughout this capstone journey."*

---

### Slide 13: Conclusion, Live Demo & Q&A
**Visual on screen:** Live Demo link `noetrix-virid.vercel.app`, API documentation `noetrix-api.onrender.com/docs`, GitHub repository `github.com/dhrubojyotihazra/Noetrix`, and Ardent Computech address.

> *"In conclusion, Noetrix demonstrates that recruitment technology does not have to be a secretive black box or an ungrounded AI experiment. By pairing deterministic scoring with guardrailed intelligence, we can empower job seekers with honest feedback while giving recruiters fast, merit-based candidate shortlists.*
>
> *Our full system is live right now:*
> *• The web application is accessible at **`noetrix-virid.vercel.app`**.*  
> *• Interactive API documentation is available on our Render service.*  
> *• And our entire codebase, test suite, and benchmarks are open on GitHub at **`github.com/dhrubojyotihazra/Noetrix`**.*
>
> *We invite everyone to try out the live portal, and we now welcome any questions or feedback from our mentor and the panel.*
>
> *Thank you very much!"*

---

## 💡 Quick Tips for Presentation Day

1. **Keep Eye Contact:** Look at the mentor and panel, not just the slides.
2. **Smooth Hand-offs:** Always use the transition phrase at the end of your section to invite the next teammate by name.
3. **Live Demo Backup:** Keep a browser tab already open at `https://noetrix-virid.vercel.app` and `https://noetrix-api.onrender.com/api/health` so you can switch instantly if asked for a live demonstration.
4. **Pacing:** Speak at a calm, conversational speed. Do not rush through the numbers — let the 42.4 ms and 71/71 test statistics sink in!
