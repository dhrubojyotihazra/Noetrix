#!/usr/bin/env python3
"""
Generate high-resolution publication-grade Mermaid architecture diagrams for Noetrix Report.
Renders 8 technical Mermaid diagrams via Playwright Chromium into PNG assets in docs/diagrams/:
1. fig_4_1_system_architecture.png (Layered System Architecture)
2. fig_4_2_c4_container_model.png (C4 Container Blueprint)
3. fig_4_3_dfd_level_0.png (DFD Level 0 Context Diagram)
4. fig_4_4_dfd_level_1.png (DFD Level 1 Functional Decomposition)
5. fig_4_5_dfd_level_2.png (DFD Level 2 Scoring Core & GenAI Redaction)
6. fig_4_6_flowchart_candidate.png (Candidate Live Audit Workflow Flowchart)
7. fig_4_7_flowchart_recruiter.png (Recruiter Batch Screening Workflow Flowchart)
8. fig_5_1_scoring_pipeline.png (Deterministic Scoring Pipeline & Soft Knockout)
"""

import os
import asyncio
from playwright.async_api import async_playwright

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DIAGRAMS_DIR = os.path.join(WORKSPACE_DIR, "docs", "diagrams")
os.makedirs(DIAGRAMS_DIR, exist_ok=True)

MERMAID_DIAGRAMS = {
    # 1. Figure 4.1: System Architecture
    "fig_4_1_system_architecture": {
        "title": "Figure 4.1: Noetrix High-Level Layered Architecture",
        "subtitle": "Decoupled Three-Tier Topology: Presentation, Services & Ephemeral Generative AI Engine",
        "mermaid": """
flowchart TD
    subgraph L1["Presentation Layer (Next.js 14 / TypeScript)"]
        CP["Candidate Portal<br/>(Dropzone, Radar Chart, Breakdown)"]
        OI["OpenResume Inspector<br/>(Contact, Sections, Skills)"]
        RP["Recruiter Portal<br/>(Requisition Config, Weight Sliders)"]
        RC["Shortlist Leaderboard<br/>(Deterministic Ranks, Dossier Drawer)"]
    end

    subgraph L2["API Gateway & Service Layer (FastAPI Port 8000)"]
        ING["Document Ingestion<br/>(pdfplumber / python-docx)"]
        EXT["Entity & Section Extractor<br/>(Pydantic ParsedResume)"]
        SCO["6-Metric Scoring Core<br/>(Deterministic engine.py)"]
        RNK["Batch Ranker & Tie-Breaker<br/>(6-Tier TimSort Key)"]
        PDF["ReportLab PDF Generator<br/>(ATS-Proof Single Column)"]
    end

    subgraph L3["Analytics, Guardrails & Bounded GenAI Layer"]
        SEM["Sentence-Transformers<br/>(all-MiniLM-L6-v2 384-d Cosine)"]
        PII["Regex PII Redactor<br/>(Client & Server Sanitization)"]
        SEM_TH["Concurrency Semaphore<br/>(Max 3 Active Groq Threads)"]
        LLM["Groq LLaMA 3.3 70B<br/>(temp=0.0, Pydantic Schema)"]
        VAL["Zero-Fabrication Validator<br/>(Token & Metric Cross-Check)"]
    end

    CP -->|HTTP / JSON| ING
    RP -->|Batch Files & JD| ING
    ING --> EXT
    EXT --> SCO
    SCO --> RNK
    RNK --> RC
    SCO --> SEM
    CP --> PII
    PII --> SEM_TH
    SEM_TH --> LLM
    LLM --> VAL
    VAL -->|Verified Bullet| CP
    VAL -.->|Fallback Opener Rules| CP
    CP --> PDF
"""
    },

    # 2. Figure 4.2: C4 Container Blueprint
    "fig_4_2_c4_container_model": {
        "title": "Figure 4.2: C4 Container Topology Blueprint",
        "subtitle": "Container-Level Decomposition of Actors, Web Applications, In-Process ML, and Cloud Inference",
        "mermaid": """
flowchart TB
    CAND["👤 Job Candidate"]
    REC["👤 Recruiter / Hiring Team"]

    subgraph C1["Container 1: Web Application (Next.js 14 / TypeScript)"]
        FE_UI["React Server Components & Interactive Hooks<br/>Port 3000"]
        FE_STATE["Client-Side Session State & PII Sanitizer"]
    end

    subgraph C2["Container 2: Backend API (FastAPI / Uvicorn)"]
        BE_API["REST Endpoints (/api/score, /api/rank, /api/improve)<br/>Port 8000"]
        BE_CORE["Deterministic Scoring Engine & Soft Knockout Gate"]
        BE_EXP["ReportLab PDF Builder & CSV Streamer"]
    end

    subgraph C3["Local In-Process Analytics Engine"]
        EMB["Sentence-Transformers Model<br/>(all-MiniLM-L6-v2, 384-d Dense Embeddings)"]
    end

    subgraph EXT_AI["External AI Service"]
        GROQ["Groq Cloud AI (LLaMA 3.3 70B Versatile)<br/>HTTPS REST API"]
    end

    CAND -->|Uploads Resume / Edits Bullets| FE_UI
    REC -->|Inputs JD / Evaluates Batch| FE_UI
    FE_UI --> FE_STATE
    FE_STATE -->|Asynchronous JSON / HTTP| BE_API
    BE_API --> BE_CORE
    BE_CORE --> EMB
    BE_CORE --> BE_EXP
    BE_CORE -->|Scrubbed Prompts / Semaphore| GROQ
    GROQ -->|Bounded Structured JSON| BE_CORE
    BE_EXP -->|ATS-Clean PDF / CSV Payload| FE_UI
"""
    },

    # 3. Figure 4.3: DFD Level 0 Context Diagram
    "fig_4_3_dfd_level_0": {
        "title": "Figure 4.3: Data Flow Diagram (DFD Level 0 — Context Level)",
        "subtitle": "System Boundary, External Entities, Information Ingestion, and Generated Audit Deliverables",
        "mermaid": """
flowchart LR
    CAND["👤 Candidate<br/>(Job Applicant)"]
    SYS(("0.0<br/>NOETRIX ATS<br/>SYSTEM CORE"))
    REC["👤 Recruiter<br/>(Talent Acquisition)"]

    CAND -->|"1. Resume File (PDF/DOCX)<br/>2. Target Job Description<br/>3. Bullet Tailor Requests"| SYS
    SYS -->|"1. 6-Metric Explainable Scores<br/>2. OpenResume Parse Tree<br/>3. Verified Tailored Bullets<br/>4. ATS Clean PDF"| CAND

    REC -->|"1. Requisition Narrative<br/>2. Mandatory Must-Haves<br/>3. Custom Metric Weights<br/>4. Batch Applicant Resumes"| SYS
    SYS -->|"1. Ranked Shortlist Leaderboard<br/>2. Match Band Badges<br/>3. Slide-Over Audit Dossiers<br/>4. Exported RFC-4180 CSV"| REC
"""
    },

    # 4. Figure 4.4: DFD Level 1 Functional Decomposition
    "fig_4_4_dfd_level_1": {
        "title": "Figure 4.4: Data Flow Diagram (DFD Level 1 — Functional Decomposition)",
        "subtitle": "Decomposition into Document Parsing, Entity Structuring, Scoring, Soft Knockout, and Shortlisting",
        "mermaid": """
flowchart TD
    DOC["Input Document<br/>(PDF / DOCX)"] --> P1["1.0 Document Ingestion<br/>& Format Detection"]
    P1 -->|"Clean Raw Text"| P2["2.0 Entity Extraction<br/>& Section Classification"]
    P2 -->|"ParsedResume Model"| MEM[("Ephemeral Session Memory<br/>(Stateless - Zero Database)")]

    JD["Target Job Requisition"] --> P2_JD["2.1 JD Feature Extraction<br/>(Must-Haves, Experience)"]
    P2_JD --> MEM

    MEM --> P3["3.0 Multi-Metric Scoring Core<br/>(6 Deterministic Channels)"]
    P3 -->|"Raw Composite Score"| P4{"4.0 Soft Knockout Gate<br/>Coverage >= 50%?"}

    P4 -->|No| P4_CAP["Apply 50-Point Cap<br/>Force Match Band: Weak"]
    P4 -->|Yes| P4_PASS["Final Score = Raw Score<br/>Assign Band (Strong/Mod/Weak)"]

    P4_CAP --> P6["6.0 Batch Ranking<br/>& 6-Tier Tie-Breaking"]
    P4_PASS --> P6

    MEM --> P5["5.0 Guardrailed Tailoring<br/>(PII Scrub + Groq LLM)"]
    P5 --> P5_VAL["5.1 Zero-Fabrication Validator<br/>(Token Cross-Check)"]
    P5_VAL -->|"Verified Bullet"| P7["7.0 ReportLab PDF Export<br/>(Single-Column ATS Layout)"]

    P6 -->|"Leaderboard Payload"| OUT_REC["Recruiter Shortlist & CSV"]
    P7 -->|"Clean Resume PDF"| OUT_CAND["Candidate Download"]
"""
    },

    # 5. Figure 4.5: DFD Level 2 Scoring & Privacy Flow
    "fig_4_5_dfd_level_2": {
        "title": "Figure 4.5: DFD Level 2 — GenAI Privacy & Zero-Fabrication Pipeline",
        "subtitle": "Subsystem Dataflow: Regex PII Scrubbing, Concurrency Throttling, and Deterministic Hallucination Guardrails",
        "mermaid": """
flowchart TD
    IN_BULLET["Candidate Bullet Point and Target Skill"] --> STEP1["Step 1: Regex PII Scrubbing<br/>(Strip Name, Email, Phone, URLs)"]
    STEP1 --> STEP2["Step 2: SHA-256 Hash Computation<br/>(Check In-Memory Prompt Cache)"]

    STEP2 --> CACHE_CHECK{"Cache Hit?"}
    CACHE_CHECK -->|Yes| CACHE_RET["Return Cached Tailored Bullet<br/>(0ms Sub-Millisecond Response)"]

    CACHE_CHECK -->|No| STEP3["Step 3: Acquire Semaphore Permit<br/>(Process Concurrency Limit: 3 Slots)"]
    STEP3 --> STEP4["Step 4: Groq LLM Inference<br/>(LLaMA 3.3 70B, temp=0, Pydantic JSON Schema)"]
    STEP4 --> STEP5["Step 5: Zero-Fabrication Validator<br/>(Extract Numbers, Percentages, Technical Tokens)"]

    STEP5 --> VAL_CHECK{"Token and Metric<br/>Set Match?"}
    VAL_CHECK -->|"Yes: Zero Hallucination"| STEP6_PASS["ACCEPT REWRITE<br/>Format into Google XYZ Pattern"]
    VAL_CHECK -->|"No: Invented Facts"| STEP6_FAIL["REJECT LLM OUTPUT<br/>Fallback: 21 Deterministic Regex Rules"]

    STEP6_PASS --> OUT["Return Tailored Bullet to Candidate Portal"]
    STEP6_FAIL --> OUT
"""
    },

    # 6. Figure 4.6: Candidate Flowchart
    "fig_4_6_flowchart_candidate": {
        "title": "Figure 4.6: Candidate Live Audit & Optimization Workflow Flowchart",
        "subtitle": "System Behavioral Flowchart: From Document Upload to ATS-Proof ReportLab PDF Export",
        "mermaid": """
flowchart TD
    START([Start: Candidate Visits Portal]) --> UPLOAD["Upload Resume (PDF / DOCX) & Target JD"]
    UPLOAD --> PARSE["Execute Multi-Format Parser<br/>(Check Column & Table Hazards)"]
    PARSE --> EXTRACT["Extract Contact, Sections & Skills"]
    EXTRACT --> SCORE["Run 6 Deterministic Scoring Modules in Parallel"]
    SCORE --> CALC_RAW["Compute Raw Composite: S_raw = &Sigma; w_i &middot; S_i"]

    CALC_RAW --> KO_CHECK{"Must-Have Skill<br/>Coverage &ge; 50%?"}
    KO_CHECK -->|No| KO_APPLY["Cap Final Score at min(S_raw, 50.0)<br/>Set Match Band to 'Weak'<br/>Flag Knockout Evidence Alert"]
    KO_CHECK -->|Yes| KO_PASS["Final Score = S_raw<br/>Band: Strong (&ge;75) / Moderate (50-74)"]

    KO_APPLY --> DISPLAY["Render Interactive Radar, Breakdown Cards<br/>& OpenResume Parse Inspector"]
    KO_PASS --> DISPLAY

    DISPLAY --> OPT_CHOICE{"Optimize Weak<br/>Bullet Point?"}
    OPT_CHOICE -->|No| EXPORT_CHOICE{"Export ATS PDF?"}
    OPT_CHOICE -->|Yes| IMPROVE["Run Groq Guardrailed Optimizer<br/>(Google XYZ Enhancement)"]
    IMPROVE --> VERIFY{"Zero-Fabrication<br/>Validation Pass?"}
    VERIFY -->|Yes| ACCEPT["Candidate Reviews & Accepts Rewrite"]
    VERIFY -->|No| FALLBACK["Apply Deterministic Opener Rule"]
    FALLBACK --> ACCEPT
    ACCEPT --> RESCORE["Instant Client-Side Re-Score"]
    RESCORE --> DISPLAY

    EXPORT_CHOICE -->|Yes| PDF_GEN["ReportLab Builds Single-Column PDF"]
    PDF_GEN --> END([Finish: Download ATS-Clean PDF])
    EXPORT_CHOICE -->|No| END
"""
    },

    # 7. Figure 4.7: Recruiter Flowchart
    "fig_4_7_flowchart_recruiter": {
        "title": "Figure 4.7: Recruiter Batch Screening & Shortlisting Workflow Flowchart",
        "subtitle": "System Behavioral Flowchart: Automated Requisition Parsing to Audit Dossier Review and CSV Export",
        "mermaid": """
flowchart TD
    START([Start: Recruiter Enters Portal]) --> PASTE_JD["Paste Job Requisition Description"]
    PASTE_JD --> EXT_JD["Auto-Extract Must-Haves, Nice-To-Haves & Tenure"]
    EXT_JD --> TUNE_W["Optionally Adjust 6 Metric Weight Sliders"]
    TUNE_W --> UPLOAD_BATCH["Drag & Drop Batch of Candidate Resumes"]

    UPLOAD_BATCH --> PARALLEL_PROC["Concurrent Asynchronous Parsing & Scoring"]
    PARALLEL_PROC --> EVAL_KO["Evaluate 50% Must-Have Soft Knockout for each Candidate"]
    EVAL_KO --> TIE_BREAK["Apply 6-Tier Deterministic Tie-Breaking Key<br/>SortKey = (-Score, -Coverage, -Kw, -Exp, -Imp, Index)"]

    TIE_BREAK --> LEADERBOARD["Render Dynamic Shortlist Leaderboard<br/>(Filter by Match Band / Must-Have Status)"]

    LEADERBOARD --> DRAWER_ACTION{"Click Candidate Row?"}
    DRAWER_ACTION -->|Yes| OPEN_DRAWER["Open Slide-Over Audit Dossier Drawer<br/>Inspect Dimensional Rationales & Risk Flags"]
    OPEN_DRAWER --> LEADERBOARD

    DRAWER_ACTION -->|No| EXPORT_CSV{"Export Results to CSV?"}
    EXPORT_CSV -->|Yes| STREAM_CSV["Stream RFC-4180 Compliant CSV File<br/>(HRIS-Compatible Audit Data)"]
    STREAM_CSV --> END([Finish: Screening Complete])
    EXPORT_CSV -->|No| END
"""
    },

    # 8. Figure 5.1: Scoring Engine Architecture
    "fig_5_1_scoring_pipeline": {
        "title": "Figure 5.1: End-to-End Scoring Engine & Soft Knockout Architecture",
        "subtitle": "Mathematical Formulation: Multi-Channel Metric Processing, Normalization, and Soft Knockout Ceiling Gate",
        "mermaid": """
flowchart TD
    subgraph IN["Input Entities"]
        RES["Candidate Resume (R)<br/>Parsed Sections, Skills, Bullets, Tenure"]
        JD["Job Description (J)<br/>Must-Haves, Nice-To-Haves, Min Tenure"]
    end

    subgraph ENGINES["Six Deterministic Scoring Channels"]
        D1["D1: Placement Keywords (S_kw)<br/>w1 = 0.30 | Bullets: 1.0, Skills: 0.8, Text: 0.5"]
        D2["D2: Dense Semantic Cosine (S_sem)<br/>w2 = 0.20 | MiniLM 384-d Clamped Mapping"]
        D3["D3: Experience & Verbs (S_exp)<br/>w3 = 0.20 | 60% Tenure + 40% Action Verbs"]
        D4["D4: Prestige-Free Education (S_edu)<br/>w4 = 0.10 | Degree Hierarchy + Cert Bonuses"]
        D5["D5: Quantified Impact Ratio (S_imp)<br/>w5 = 0.10 | Metric Regex Scan (40% Target)"]
        D6["D6: Format & ATS Hygiene (S_fmt)<br/>w6 = 0.10 | 100 - Multi-Column & Table Deductions"]
    end

    RES --> ENGINES
    JD --> ENGINES

    D1 --> SUM["Weighted Summation<br/>S_raw = &Sigma; (w_i &middot; S_i) [Eq. 5.1 & 5.16]"]
    D2 --> SUM
    D3 --> SUM
    D4 --> SUM
    D5 --> SUM
    D6 --> SUM

    SUM --> GATE{"Must-Have Coverage Gate<br/>CoverageRatio &ge; 0.50? [Eq. 5.17]"}

    GATE -->|Coverage &ge; 50%| PASS["S_final = S_raw<br/>Match Band: Strong (&ge;75), Moderate (50-74), or Weak (&lt;50)"]
    GATE -->|Coverage &lt; 50%| KNOCKOUT["Soft Knockout Ceiling Triggered<br/>S_final = min(S_raw, 50.0)<br/>Match Band FORCED to 'Weak' [Eq. 5.18]"]

    PASS --> SORT["6-Tier Deterministic Tie-Breaking Key<br/>SortKey = (-S_final, -CoverageRatio, -S_kw, -S_exp, -S_imp, Index) [Eq. 5.19]"]
    KNOCKOUT --> SORT
"""
    }
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      background: #ffffff;
      padding: 30px;
      display: flex;
      justify-content: center;
      align-items: center;
    }}
    .diagram-card {{
      background: #ffffff;
      border: 2px solid #cbd5e1;
      border-radius: 12px;
      padding: 24px 28px;
      width: 1180px;
      box-shadow: 0 4px 16px rgba(0,0,0,0.06);
    }}
    .diagram-title {{
      font-size: 21px;
      font-weight: 700;
      color: #0f172a;
      text-align: center;
      margin-bottom: 5px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}
    .diagram-subtitle {{
      font-size: 14.5px;
      color: #64748b;
      text-align: center;
      margin-bottom: 22px;
    }}
    .mermaid {{
      display: flex;
      justify-content: center;
      align-items: center;
    }}
    .mermaid svg {{
      max-width: 1140px !important;
      height: auto !important;
    }}
  </style>
  <script>
    mermaid.initialize({{
      startOnLoad: true,
      theme: 'neutral',
      themeVariables: {{
        fontFamily: "'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif",
        fontSize: '17px',
        primaryColor: '#f0f9ff',
        primaryTextColor: '#0369a1',
        primaryBorderColor: '#0284c7',
        lineColor: '#334155',
        secondaryColor: '#ecfdf5',
        tertiaryColor: '#f5f3ff'
      }},
      flowchart: {{
        useMaxWidth: false,
        htmlLabels: true,
        curve: 'basis'
      }}
    }});
  </script>
</head>
<body>
  <div class="diagram-card">
    <div class="diagram-title">{title}</div>
    <div class="diagram-subtitle">{subtitle}</div>
    <div class="mermaid">
{mermaid}
    </div>
  </div>
</body>
</html>
"""

async def render_all_mermaid_diagrams():
    print(f"Launching Playwright Chromium to render {len(MERMAID_DIAGRAMS)} Mermaid diagrams...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        # 3x device scale = crisp print-quality (300 dpi equivalent)
        page = await browser.new_page(viewport={"width": 1600, "height": 1300}, device_scale_factor=3)
        
        for name, data in MERMAID_DIAGRAMS.items():
            out_png = os.path.join(DIAGRAMS_DIR, f"{name}.png")
            html_content = HTML_TEMPLATE.format(
                title=data["title"],
                subtitle=data["subtitle"],
                mermaid=data["mermaid"].strip()
            )
            await page.set_content(html_content, wait_until="networkidle")
            try:
                # Wait for mermaid to render svg
                await page.wait_for_selector(".mermaid svg", timeout=15000)
                await page.wait_for_timeout(1500)  # Extra settle for complex diagrams
                element = await page.query_selector(".diagram-card")
                if element:
                    await element.screenshot(path=out_png)
                    print(f"Rendered Mermaid Diagram: {out_png}")
                else:
                    await page.screenshot(path=out_png)
                    print(f"Rendered Page: {out_png}")
            except Exception as e:
                print(f"Error rendering {name}: {e}")
                
        await browser.close()
    print("All Mermaid architecture diagrams successfully rendered into docs/diagrams/")


if __name__ == "__main__":
    asyncio.run(render_all_mermaid_diagrams())
