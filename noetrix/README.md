# Noetrix · Hybrid ATS Scorer & Ranker

> **Capstone Project**: Deterministic 6-Metric Hybrid ATS Simulation Engine  
> **Frontend**: Next.js 15 (React 19, Tailwind CSS) → Deployed to **Vercel**  
> **Backend**: FastAPI (Python 3.11+, scikit-learn, sentence-transformers) → Deployed to **Render**  
> **Architecture**: Stateless backend · No server-side storage; a copy stays in the browser tab until it is closed

---

## 🌟 Overview & Key Innovations

Noetrix is an ATS simulation app with **two doors** powered by **one deterministic scoring engine**:

1. **Candidate Door**:
   - **Upload & Scan**: Ingests PDF/DOCX resumes and parses criteria from any pasted job description.
   - **Transparent Scorecard**: 6-metric breakdown (Hard-Skill Keyword Match, Semantic Fit, Experience, Education, Impact, Format Health).
   - **What the ATS Sees**: OpenResume-style diagnostic view revealing extracted entities vs raw tokens.
   - **AI Resume Editor & Tailor**: Interactive resume editor with 1-click XYZ bullet optimization (*"Accomplished [X] as measured by [Y] by doing [Z]"* + keyword inclusion), missing skill recommendations, side-by-side diff preview modal with estimated score delta, and live re-scoring.
   - **Vector PDF Audit Report**: Client-side single-page A4 export using jsPDF.

2. **Recruiter Door**:
   - **Requisition Setup**: Paste JD, auto-extract mandatory must-haves, set required tenure, and configure custom weight sliders.
   - **Soft Knockout Cap**: Matching fewer than half (<50%) of mandatory must-have skills caps the total score at 50 points and classifies the candidate in the 'weak' match band, preserving visibility without polluting the top ranks.
   - **Bulk Ingestion**: Screen up to 50 CVs with real-time per-file progress (or 1-click load 5 demo candidate resumes).
   - **Explainable Leaderboard**: 6-tier deterministic tie-breaking (`score` → `must-have coverage` → `keywords` → `experience` → `impact` → `FIFO`).
   - **Candidate Dossier Drawer**: Inspect detailed evidence snippets and audit risk flags for each applicant.
   - **Candidate Status Management**: Mark Shortlisted, Hold, or Rejected.
   - **CSV Shortlist Export**: One-click RFC 4180 CSV export.

---

## 🎨 Design System (Inspired by Seamful / Woblo)

- **Typography**: Editorial display headlines using `Anton` (uppercase, tight line-height) and body text in `DM Sans`.
- **Palette**: Warm Parchment `#F6EFE3` canvas, Card Surface `#FDFAF4`, Deep Ink `#0C0F17`.
- **Accents**: Electric Yellow `#FAE425` (Candidate badges & highlights), Pastel Lilac `#DBACF0` (Recruiter badges), Coral `#FF8465` (Warnings/missing skills), Emerald `#10B981` (Matched skills).
- **UI Elements**: 100px rounded pill buttons (`rounded-full`), animated marquee ticker banner, numbered cards (`01`, `02`).

---

## 🚀 Quickstart: Running Locally

### 1. Run Backend (FastAPI)
```bash
cd noetrix/backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- Health check: [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### 2. Run Frontend (Next.js)
```bash
cd noetrix/frontend
npm install
npm run dev
```
- App: [http://localhost:3000](http://localhost:3000)

---

## ☁️ Deployment Guide

### Deploy Backend to Render
1. Connect your repository to [Render](https://render.com).
2. Create a new **Web Service** using the root directory `noetrix/backend` (or point to `noetrix/backend/render.yaml`).
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Note your public backend URL (e.g. `https://noetrix-api.onrender.com`).

### Deploy Frontend to Vercel
1. Connect your repository to [Vercel](https://vercel.com).
2. Set Root Directory to `noetrix/frontend`.
3. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://noetrix-api.onrender.com`
4. Deploy! Next.js will build and serve your app globally.

---

## ⚖️ Legal & Compliance Note
All code in Noetrix is original and clean-room implemented based on architectural concepts from open-source references (Resume-Matcher, ATSify, SmartATS, ResumeRank, OpenResume). No AGPL or unlicensed code was copied.
