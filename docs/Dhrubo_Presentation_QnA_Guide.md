# 🧠 Dhrubo's Guide: Benchmarks, Empirical Results & Q&A Defense

**Role:** Project Lead & Final Presenter (Slides 10, 11, 12, 13)  
**Project:** Noetrix — Explainable ATS Simulation Engine  
**Live Application:** [https://noetrix-virid.vercel.app](https://noetrix-virid.vercel.app)  
**Backend API:** [https://noetrix-api.onrender.com](https://noetrix-api.onrender.com)  

---

## 💡 1. The 30-Second Big Picture
> *"To prove Noetrix outperforms existing hiring tech, we didn't just guess — we tested **40 diverse resumes** across three paradigms: **Legacy Keyword ATS**, **Pure AI (GPT-4/LLMs)**, and the **Noetrix Hybrid Engine**. We measured three critical dimensions: **Anti-cheating robustness**, **Mathematical score consistency**, and **CPU execution speed**."*

---

## 📊 2. Slide 10: Comparative Benchmarks (Where the Numbers Came From)

We tested a benchmark corpus of 40 resumes (20 genuine engineering CVs + 10 adversarial/cheating CVs + 10 non-traditional formats) across three architectures:

### A. Legacy Keyword ATS — **Gave 94.2% to a Cheating Resume**
* **How It Works:** Legacy enterprise systems (like older Taleo implementations or keyword matchers) operate like search engines, simply counting whether keywords appear in the document text.
* **The Experiment:** We constructed an adversarial "keyword-stuffed" resume containing zero real engineering experience, but loaded with 100% of the job description's technical keywords in an isolated skills dump (and hidden white-font text).
* **The Result:** The legacy ATS was completely compromised. Because it saw 100% keyword overlap without verifying context, it awarded the fake resume a **94.2% match ("Top Shortlist")**.

### B. Pure LLM Screening — **±8.4 Points Score Jitter**
* **How It Works:** Many modern recruitment tools pipe the entire resume and job description directly into an LLM (such as GPT-4) and prompt: *"Rate this candidate from 1 to 100."*
* **The Experiment:** We evaluated the exact same candidate resume through an unconstrained LLM prompt across 50 repeated runs.
* **The Result:** The scores suffered from severe stochastic drift. The exact same candidate scored **82 (Strong Match)** on one iteration and **68 (Moderate Match)** on another, producing a standard deviation of **±8.4 points**. In high-stakes hiring, this randomness creates legal and ethical liability because candidate selection depends on random AI sampling luck.

### C. Noetrix Hybrid Framework — **Capped at 50 / Weak Band & 0.000 Variance**
* **How Noetrix Neutralized Keyword Stuffing:**
  1. Our engine discounts skills mentioned only in a standalone list to **0.5x placement credit**.
  2. Our **Must-Have Soft Knockout Rule** requires contextual proof of mandatory skills in actual work experience or projects. Because the cheating CV had no proof in work bullets, it failed the 50% must-have threshold, triggering the cap at **48.8% – 50.0% ("Weak Match")**.
* **How Noetrix Achieved Determinism:** Because our 6 scoring metrics are calculated with closed-form deterministic mathematical formulas (not LLM sampling), 50 repeated runs on the same resume produced a variance of **exactly 0.000 — identical scores every single time**.

---

## ⚡ 3. Slide 11: Empirical Results (Where 100%, 42.4 ms, and 71/71 Came From)

### A. 100% Reproducible (Zero Score Drift)
* **What It Means:** Whether a candidate uploads their resume now, tomorrow, or 100 times sequentially, their composite score and band classification remain strictly identical.
* **How It Was Measured:** In Chapter 7 of our Master Report, we ran a 50-iteration benchmark across all 40 test resumes (2,000 total evaluations). The mathematical score variance was **0.000**.

### B. 42.4 ms Per Resume (20 Resumes in 0.892 s)
* **What It Means:** Noetrix achieves commercial-grade throughput on standard, cost-effective CPUs without requiring expensive GPU infrastructure.
* **The Breakdown:**
  * **Single Resume Scoring:** All 6 algorithms running in parallel (Regex tokenization, TF-IDF taxonomy, Sentence-Transformers MiniLM embeddings on CPU, career trajectory duration, impact metric detection, and format health) complete in a mean time of **42.4 milliseconds**.
  * **Batch Ranking Throughput:** Scoring, evaluating must-have coverage, and sorting a batch of **20 resumes** using our 6-tier deterministic tie-breaking algorithm finishes in **892 milliseconds (0.892 seconds)** — under one second total.

### C. 71/71 Tests Passed (100% Pass Rate)
* **What It Means:** Every layer of the platform is validated by automated CI/CD unit and integration tests.
* **The Test Suite Breakdown (`pytest`):**
  * **Zero-Fabrication Validator (12 tests):** Proves the system catches and rejects invented numbers, dropped metrics, altered number words, unconfirmed skills, and meaning reversals.
  * **Groq LLM Adapter (13 tests):** Proves thread-safe concurrency (max 3 calls), SHA-256 caching (256 cap with TTL eviction), HTTP 429 backoff retry, and JSON schema repair.
  * **Parsing & Template Safety (18 tests):** Proves PDF/DOCX/TXT extraction, nuanced confidence scoring, and guarantees all 4 ReportLab templates can be re-parsed with zero lost bullets.
  * **Scoring & Anti-Gaming Integrity (15 tests):** Proves must-have cap firing below 50% coverage, band edge thresholds (49.9 vs 50.0), and CSV formula injection protection.
  * **Security & Storage Integrity (13 tests):** Proves PII redaction, CORS domain filtering, file size limits (5 MB max), and verifies zero localStorage persistence.

---

## 🛡️ 4. Examiner & Mentor Defense Cheat Sheet (Q&A Ready)

| If the Examiner Asks... | Your 10-Second Confident Answer: |
| :--- | :--- |
| **"Why not let an LLM do the scoring directly?"** | *"Because LLMs are non-deterministic. In our experiments, an LLM scoring prompt exhibited an 8.4-point score jitter on the exact same resume. Noetrix relies on deterministic math for scoring so every decision is auditable and fair; the LLM is restricted solely to text rewriting under strict validator guardrails."* |
| **"How does your engine detect and stop keyword stuffers?"** | *"We use a two-layer defense: First, skills listed only in an isolated skills dump receive discounted credit (0.5x). Second, our 50% Must-Have Cap requires contextual proof in actual work experience or projects. If a candidate dumps keywords without contextual proof, their score is hard-capped at 50 in the weak band."* |
| **"Did you require expensive GPUs to run this?"** | *"No, our entire NLP pipeline — including Sentence-Transformers MiniLM embeddings — runs entirely on standard CPU in just 42.4 ms per resume. Only bullet rewriting makes an external API call to Groq, which is cached via SHA-256."* |
| **"What happens if the Groq LLM API goes down?"** | *"Noetrix has a 100% offline fallback. If the API is offline or rate-limited, the system falls back to our deterministic rule-based active verb lemma engine, so candidate tailoring never breaks."* |
| **"How do you ensure candidate data privacy?"** | *"Noetrix enforces zero server-side database storage. Resumes are processed ephemerally in server RAM. In the browser, data lives strictly in the active tab's `sessionStorage` and is wiped when the tab is closed or when the candidate clicks 'Clear my data'."* |

---

## 🚀 5. Live Demonstration Checklist

Before your turn to speak:
1. Open a browser tab with the live app: `https://noetrix-virid.vercel.app`
2. Open a second tab with the live API health check: `https://noetrix-api.onrender.com/api/health`
3. Have a sample resume PDF (`sample_resume_alex_chen.pdf`) ready on your desktop to drag and drop if the panel asks for a live demo.
