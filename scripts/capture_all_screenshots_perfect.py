#!/usr/bin/env python3
"""
Exhaustive high-resolution screenshot generator for Noetrix report Chapter 6.
Seeds realistic state into sessionStorage, suppresses Next.js dev overlays,
and captures every screen in pristine, publication-grade clarity.
"""
import os
import json
import asyncio
from playwright.async_api import async_playwright

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCREENSHOTS_DIR = os.path.join(WORKSPACE_DIR, "docs", "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

BASE = "http://localhost:3000"

MOCK_RESUME = {
    "filename": "Alex_Chen_Staff_ML_Engineer.pdf",
    "raw_text": "Alex Chen\nStaff Machine Learning Engineer\nEmail: alex.chen@domain.org\nSan Francisco, CA\nSummary: 7+ years of experience leading ML infrastructure and LLM serving pipelines.",
    "contact": {
        "name": "Alex Chen",
        "email": "alex.chen@domain.org",
        "phone": "+1 (415) 890-1234",
        "location": "San Francisco, CA",
        "linkedin": "linkedin.com/in/alexchen-ml",
        "github": "github.com/alexchen",
        "website": "alexchen.dev"
    },
    "summary": "Accomplished Staff Machine Learning Engineer with 7+ years architecting high-throughput distributed LLM serving systems and automated MLOps pipelines.",
    "sections_detected": ["Contact Information", "Professional Summary", "Work Experience", "Education", "Skills", "Key Projects"],
    "work_experience": [
        {
            "id": "exp-1",
            "company": "Anthropic AI Labs",
            "title": "Staff ML Infrastructure Engineer",
            "dates": "2022 - Present",
            "location": "San Francisco, CA",
            "bullets": [
                "Architected low-latency vLLM inference serving engine handling 12,000 req/sec across 256 H100 GPU nodes with 99.99% uptime.",
                "Reduced p99 inference latency by 42% through flash-attention kernel optimization and dynamic continuous batching.",
                "Orchestrated cross-functional deployment of Ray cluster on Kubernetes, accelerating multi-modal fine-tuning cycles by 3.5x."
            ]
        },
        {
            "id": "exp-2",
            "company": "Scale AI",
            "title": "Senior Machine Learning Engineer",
            "dates": "2019 - 2022",
            "location": "San Francisco, CA",
            "bullets": [
                "Built distributed data ingestion pipelines processing 45 TB daily sensor data using Apache Spark and PyTorch Lightning.",
                "Deployed automated synthetic data generation workflows, improving target benchmark F1-score from 0.76 to 0.89."
            ]
        }
    ],
    "education": [
        {
            "id": "edu-1",
            "institution": "Stanford University",
            "degree": "Master of Science",
            "field_of_study": "Computer Science (Machine Learning)",
            "dates": "2017 - 2019",
            "gpa": "3.92 / 4.00",
            "bullets": ["Graduate researcher in Stanford AI Lab (SAIL). Published 2 papers at NeurIPS."]
        }
    ],
    "skills": ["Python", "PyTorch", "Kubernetes", "Docker", "MLOps", "vLLM", "Ray", "Triton", "FastAPI", "PostgreSQL", "Redis", "Distributed Training"],
    "projects": [
        {
            "id": "proj-1",
            "name": "Open-Source FastSpec",
            "role": "Creator & Maintainer",
            "dates": "2023",
            "technologies": ["Python", "CUDA", "C++", "PyTorch"],
            "bullets": ["Open-source speculative decoding engine with 1,800+ GitHub stars."]
        }
    ],
    "certifications": ["AWS Certified Machine Learning - Specialty"],
    "parse_confidence": 0.96,
    "detected_columns": 1,
    "has_tables": False,
    "has_graphics": False
}

MOCK_JD = {
    "title": "Staff Machine Learning Engineer",
    "raw_text": "Staff Machine Learning Engineer (LLM Inference & Distributed Systems)\nRequirements: 5+ years experience in Python, PyTorch, Kubernetes, MLOps, Distributed Systems.",
    "must_have_skills": ["Python", "PyTorch", "Kubernetes", "MLOps", "Distributed Training"],
    "nice_to_have_skills": ["vLLM", "Ray", "Triton", "FastAPI", "Docker", "AWS"],
    "min_experience_years": 5,
    "domain": "Artificial Intelligence / Machine Learning",
    "responsibilities": [
        "Architect and optimize distributed model training and high-throughput inference serving infrastructure.",
        "Collaborate with research teams to deploy state-of-the-art transformer architectures into production.",
        "Establish automated MLOps CI/CD pipelines ensuring model safety, guardrails, and compliance."
    ],
    "keywords": ["Python", "PyTorch", "Kubernetes", "MLOps", "Distributed Systems", "vLLM", "Ray", "FastAPI", "Latency", "Throughput"]
}

MOCK_SCORE = {
    "candidate_name": "Alex Chen",
    "filename": "Alex_Chen_Staff_ML_Engineer.pdf",
    "overall_score": 84.5,
    "raw_fit_score": 84.5,
    "is_capped": False,
    "match_band": "strong",
    "metrics": {
        "keyword_match": {
            "score": 92.0,
            "weight": 0.30,
            "weighted_score": 27.6,
            "evidence": ["Python", "PyTorch", "Kubernetes", "MLOps", "Distributed Training", "vLLM", "Ray", "FastAPI"],
            "missing": ["AWS"],
            "rationale": "Matches 8 of 9 extracted domain technical skills with high density in work experience."
        },
        "semantic_similarity": {
            "score": 86.0,
            "weight": 0.20,
            "weighted_score": 17.2,
            "evidence": ["High semantic cosine match between LLM serving background and target role responsibilities."],
            "missing": [],
            "rationale": "all-MiniLM-L6-v2 cosine distance indicates excellent narrative fit."
        },
        "experience_relevance": {
            "score": 88.0,
            "weight": 0.20,
            "weighted_score": 17.6,
            "evidence": ["7.2 years total tenure vs. 5.0 years required."],
            "missing": [],
            "rationale": "Seniority and career trajectory exceed baseline target requisition."
        },
        "education_match": {
            "score": 95.0,
            "weight": 0.10,
            "weighted_score": 9.5,
            "evidence": ["M.S. in Computer Science (Machine Learning) from Stanford University."],
            "missing": [],
            "rationale": "Direct degree level and domain alignment."
        },
        "quantified_impact": {
            "score": 82.0,
            "weight": 0.10,
            "weighted_score": 8.2,
            "evidence": ["12,000 req/sec", "256 H100 nodes", "42% latency reduction", "3.5x fine-tuning cycle acceleration"],
            "missing": [],
            "rationale": "Every experience bullet includes verified Google XYZ quantified metrics."
        },
        "format_ats_readability": {
            "score": 90.0,
            "weight": 0.10,
            "weighted_score": 9.0,
            "evidence": ["Single column detected", "Zero non-standard tables", "Standard headings verified"],
            "missing": [],
            "rationale": "Pure ATS-optimized layout ensures zero parse ambiguities."
        }
    },
    "matched_keywords": ["Python", "PyTorch", "Kubernetes", "MLOps", "Distributed Training", "vLLM", "Ray", "FastAPI"],
    "missing_keywords": ["AWS"],
    "priority_fixes": [
        "Mention AWS production environments explicitly in cloud infrastructure bullets.",
        "Highlight experience with Prometheus/Grafana observability dashboards."
    ],
    "risk_flags": [],
    "ats_sees": {
        "candidate_name": "Alex Chen",
        "email": "alex.chen@domain.org",
        "phone": "+1 (415) 890-1234",
        "location": "San Francisco, CA",
        "sections_detected": ["Contact Information", "Professional Summary", "Work Experience", "Education", "Skills", "Key Projects"],
        "skills_count": 12,
        "is_multi_column": False,
        "has_tables": False,
        "has_images": False,
        "parse_confidence": 0.96
    }
}

MOCK_RECRUITER_CONFIG = {
    "weights": {
        "keyword_match": 0.30,
        "semantic_similarity": 0.20,
        "experience_relevance": 0.20,
        "education_match": 0.10,
        "quantified_impact": 0.10,
        "format_ats_readability": 0.10
    },
    "must_have_cap": 50.0,
    "enable_must_have_cap": True,
    "strong_band_threshold": 75.0,
    "moderate_band_threshold": 50.0
}

MOCK_RANKED_CANDIDATES = [
    {
        "rank": 1,
        "filename": "Alex_Chen_Staff_ML.pdf",
        "candidate_name": "Alex Chen",
        "overall_score": 84.5,
        "raw_fit_score": 84.5,
        "is_capped": False,
        "match_band": "strong",
        "status": "shortlisted",
        "notes": "Top tier candidate: 7+ yrs experience, distributed training, low-latency inference.",
        "must_have_coverage": 100,
        "sorting_key": [84.5, 92.0, 86.0, 88.0, 95.0, 82.0],
        "metrics": MOCK_SCORE["metrics"],
        "matched_must_haves": ["Python", "PyTorch", "Kubernetes", "MLOps", "Distributed Training"],
        "missing_must_haves": [],
        "risk_flags": [],
        "ats_sees": MOCK_SCORE["ats_sees"]
    },
    {
        "rank": 2,
        "filename": "Priya_Sharma_Senior_MLOps.pdf",
        "candidate_name": "Priya Sharma",
        "overall_score": 79.2,
        "raw_fit_score": 79.2,
        "is_capped": False,
        "match_band": "strong",
        "status": "reviewing",
        "notes": "Strong MLOps background with Kubeflow and Ray; 6 years tenure.",
        "must_have_coverage": 80,
        "sorting_key": [79.2, 85.0, 82.0, 84.0, 90.0, 75.0],
        "metrics": MOCK_SCORE["metrics"],
        "matched_must_haves": ["Python", "PyTorch", "Kubernetes", "MLOps"],
        "missing_must_haves": ["Distributed Training"],
        "risk_flags": [],
        "ats_sees": MOCK_SCORE["ats_sees"]
    },
    {
        "rank": 3,
        "filename": "Marcus_Vance_Data_Scientist.pdf",
        "candidate_name": "Marcus Vance",
        "overall_score": 68.0,
        "raw_fit_score": 68.0,
        "is_capped": False,
        "match_band": "moderate",
        "status": "reviewing",
        "notes": "Solid modeling experience; lacks Kubernetes and distributed clusters.",
        "must_have_coverage": 60,
        "sorting_key": [68.0, 70.0, 74.0, 72.0, 85.0, 60.0],
        "metrics": MOCK_SCORE["metrics"],
        "matched_must_haves": ["Python", "PyTorch", "MLOps"],
        "missing_must_haves": ["Kubernetes", "Distributed Training"],
        "risk_flags": ["Missing 2 of 5 must-have technologies"],
        "ats_sees": MOCK_SCORE["ats_sees"]
    },
    {
        "rank": 4,
        "filename": "Devon_Lee_Junior_Dev.pdf",
        "candidate_name": "Devon Lee",
        "overall_score": 45.0,
        "raw_fit_score": 62.0,
        "is_capped": True,
        "match_band": "weak",
        "status": "rejected",
        "notes": "Soft Knockout capped at 50 points: covered under 50% must-have skills.",
        "must_have_coverage": 40,
        "sorting_key": [45.0, 48.0, 52.0, 40.0, 80.0, 50.0],
        "metrics": MOCK_SCORE["metrics"],
        "matched_must_haves": ["Python", "PyTorch"],
        "missing_must_haves": ["Kubernetes", "MLOps", "Distributed Training"],
        "risk_flags": ["Must-Have Knockout Triggered", "Tenure Deficit (-3.2 yrs)"],
        "ats_sees": MOCK_SCORE["ats_sees"]
    }
]

CLEAN_PAGE_CSS = """
  nextjs-portal,
  [data-nextjs-dialog-overlay],
  [class*="toast"],
  div[role="alert"],
  #__next-build-watcher {
    display: none !important;
  }
"""

async def clean_page(page):
    """Remove any dev overlays or toasts."""
    await page.evaluate(f"""() => {{
        const style = document.createElement('style');
        style.textContent = `{CLEAN_PAGE_CSS}`;
        document.head.appendChild(style);
        document.querySelectorAll('nextjs-portal, [class*="toast"]').forEach(e => e.remove());
    }}""")

async def seed_session(page, key_val_dict):
    script = ";".join([
        f"sessionStorage.setItem({json.dumps(k)}, {json.dumps(json.dumps(v))})"
        for k, v in key_val_dict.items()
    ])
    await page.evaluate(f"() => {{ {script}; }}")

async def run_capture():
    print("Launching Playwright for perfect Chapter 6 Visual Showcase capture...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2
        )
        page = await ctx.new_page()

        # 1. Landing Hero
        print("Capturing 01_landing_hero.png...")
        await page.goto(f"{BASE}/", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await clean_page(page)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "01_landing_hero.png"))

        # 2. How Scoring Works
        print("Capturing 02_how_scoring_works.png...")
        await page.goto(f"{BASE}/how-scoring-works", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await clean_page(page)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "02_how_scoring_works.png"))

        # 3. Candidate Upload Empty
        print("Capturing 03_candidate_upload_empty.png...")
        await page.goto(f"{BASE}/candidate/analyze", wait_until="networkidle")
        await page.wait_for_timeout(1000)
        await clean_page(page)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "03_candidate_upload_empty.png"))

        # 4. Candidate Upload Filled
        print("Capturing 04_candidate_upload_filled.png...")
        try:
            preset_btn = await page.query_selector("button:has-text('Preset 1')")
            if preset_btn:
                await preset_btn.click()
                await page.wait_for_timeout(400)
        except Exception:
            pass
        await clean_page(page)
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "04_candidate_upload_filled.png"))

        # 5. Candidate Score Overview
        print("Capturing 05_candidate_score_overview.png...")
        await seed_session(page, {
            "noetrix_resume": MOCK_RESUME,
            "noetrix_jd": MOCK_JD,
            "noetrix_score": MOCK_SCORE
        })
        await page.goto(f"{BASE}/candidate/report", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await clean_page(page)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "05_candidate_score_overview.png"))

        # 6. What the ATS Sees
        print("Capturing 06_candidate_what_the_ats_sees.png...")
        await clean_page(page)
        await page.evaluate("window.scrollTo(0, 520)")
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "06_candidate_what_the_ats_sees.png"))

        # 7. Skills and Impact
        print("Capturing 07_candidate_skills_and_impact.png...")
        await clean_page(page)
        await page.evaluate("window.scrollTo(0, 1150)")
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "07_candidate_skills_and_impact.png"))

        # 8. Candidate Editor Overview
        print("Capturing 08_candidate_editor_overview.png...")
        await page.goto(f"{BASE}/candidate/editor", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await clean_page(page)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "08_candidate_editor_overview.png"))

        # 9. Editor Bullet Enhanced
        print("Capturing 09_candidate_editor_bullet_enhanced.png...")
        await clean_page(page)
        await page.evaluate("window.scrollTo(0, 420)")
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "09_candidate_editor_bullet_enhanced.png"))

        # 10. Candidate Tailor Diff Modal
        print("Capturing 10_candidate_tailor_diff_modal.png...")
        try:
            # Route intercept for instant tailor diff response
            async def handle_tailor_route(route):
                await route.fulfill(
                    status=200,
                    content_type="application/json",
                    body=json.dumps({
                        "tailored_resume": MOCK_RESUME,
                        "diffs": [
                            {
                                "id": "diff-1",
                                "section": "experience",
                                "item_id": "work_0_bullet_0",
                                "original": "Worked on low-latency inference engine across H100 GPU nodes.",
                                "modified": "Architected low-latency vLLM inference serving engine handling 12,000 req/sec across 256 H100 GPU nodes with 99.99% uptime.",
                                "explanation": "Formatted into authoritative Google XYZ structure with active action verb and clear business outcome.",
                                "change_type": "improved"
                            },
                            {
                                "id": "diff-2",
                                "section": "skills",
                                "item_id": "skills_added",
                                "original": "",
                                "modified": "Grounded from your project evidence: vLLM, Flash-Attention, Ray",
                                "explanation": "Added verified skills directly evidenced in candidate work experience text.",
                                "change_type": "added"
                            }
                        ],
                        "estimated_gain": 5.7,
                        "estimated_score_after": 90.2,
                        "added_keywords": ["vLLM", "Flash-Attention", "Ray"]
                    })
                )
            await page.route("**/api/candidate/tailor", handle_tailor_route)
            await page.evaluate("window.scrollTo(0, 0)")
            await page.wait_for_timeout(300)
            tailor_btn = await page.query_selector("button:has-text('Tailor Experience')")
            if tailor_btn:
                await tailor_btn.click()
                await page.wait_for_timeout(1200)
        except Exception as e:
            print("Tailor modal click error:", e)
        await clean_page(page)
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "10_candidate_tailor_diff_modal.png"))
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(400)

        # 11. Editor Rescored
        print("Capturing 11_candidate_editor_rescored.png...")
        await clean_page(page)
        await page.evaluate("window.scrollTo(0, 680)")
        await page.wait_for_timeout(600)
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "11_candidate_editor_rescored.png"))

        # 12. Recruiter Requisition Setup
        print("Capturing 12_recruiter_requisition_setup.png...")
        await page.goto(f"{BASE}/recruiter/setup", wait_until="networkidle")
        await page.wait_for_timeout(1200)
        await clean_page(page)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "12_recruiter_requisition_setup.png"))

        # 13. Recruiter Upload Batch
        print("Capturing 13_recruiter_upload_batch.png...")
        await seed_session(page, {
            "noetrix_recruiter_jd": MOCK_JD,
            "noetrix_recruiter_config": MOCK_RECRUITER_CONFIG
        })
        await page.goto(f"{BASE}/recruiter/upload", wait_until="networkidle")
        await page.wait_for_timeout(1200)
        await clean_page(page)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "13_recruiter_upload_batch.png"))

        # 14. Recruiter Leaderboard
        print("Capturing 14_recruiter_leaderboard.png...")
        await seed_session(page, {
            "noetrix_recruiter_jd": MOCK_JD,
            "noetrix_recruiter_config": MOCK_RECRUITER_CONFIG,
            "noetrix_ranked_results": MOCK_RANKED_CANDIDATES
        })
        await page.goto(f"{BASE}/recruiter/results", wait_until="networkidle")
        await page.wait_for_timeout(1500)
        await clean_page(page)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "14_recruiter_leaderboard.png"))

        # 15. Recruiter Candidate Dossier Drawer
        print("Capturing 15_recruiter_candidate_dossier_drawer.png...")
        try:
            # Click the inspect button or first candidate row
            inspect_btn = await page.query_selector("span:has-text('Inspect'), tbody tr")
            if inspect_btn:
                await inspect_btn.click()
                await page.wait_for_timeout(1000)
        except Exception as e:
            print("Dossier drawer click error:", e)
        await clean_page(page)
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "15_recruiter_candidate_dossier_drawer.png"))

        await browser.close()

    print("All 15 screenshots captured in pristine quality!")

if __name__ == "__main__":
    asyncio.run(run_capture())
