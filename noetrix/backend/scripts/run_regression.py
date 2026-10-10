"""Comprehensive Regression Benchmark for Noetrix ATS Scoring Engine.

Runs 6 canonical sample CV archetypes + 30 bulk candidate CVs with LLM_MODE=off.
Compares calibrated scores against the uncalibrated baseline and prints a Before/After comparison table.
"""

import json
import os
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from app.schemas.resume import ParsedResume, WorkEntry, EduEntry, ContactInfo, ProjectEntry
from app.services.jd_parser import parse_job_description
from app.services.scorer.engine import score_resume_against_jd
from app.services.parser.pdf_parser import parse_pdf_bytes


def build_canonical_sample_cvs() -> list[ParsedResume]:
    """Build the 6 canonical archetype CV profiles defined in the PRD."""
    samples = []

    # 1. Strong ML Engineer
    samples.append(ParsedResume(
        filename="cv_01_strong_ml_engineer.json",
        contact=ContactInfo(name="Aria Chen", email="aria@example.com", phone="+1-555-0101"),
        summary="Senior Machine Learning Engineer with 3+ years experience building production ML pipelines.",
        skills=["python", "pytorch", "scikit-learn", "sql", "docker", "fastapi", "pandas", "numpy", "transformers"],
        work_experience=[
            WorkEntry(
                id="w1",
                title="Machine Learning Engineer",
                company="Nexus AI",
                dates="2023 - 2026",
                bullets=[
                    "Engineered PyTorch neural network pipelines achieving 94.2% classification accuracy.",
                    "Containerized inference microservices using Docker and FastAPI handling 15,000 req/min.",
                    "Optimized SQL data pipelines and NumPy vector operations cutting feature latency by 45%."
                ]
            )
        ],
        education=[EduEntry(id="e1", institution="Carnegie Mellon University", degree="Bachelor of Science in Computer Science", dates="2019 - 2023")],
        projects=[ProjectEntry(id="p1", name="Transformer Serving", technologies=["pytorch", "docker"], bullets=["Deployed LLM endpoints with FastAPI."])],
        sections_detected=["summary", "skills", "experience", "education", "projects"],
        parse_confidence=1.0,
        detected_columns=1,
        has_tables=False
    ))

    # 2. Junior Data Analyst
    samples.append(ParsedResume(
        filename="cv_02_junior_data_analyst.json",
        contact=ContactInfo(name="Liam Brooks", email="liam@example.com"),
        summary="Data Analyst skilled in SQL, Pandas, and exploratory data analysis.",
        skills=["python", "sql", "pandas", "numpy", "tableau"],
        work_experience=[
            WorkEntry(
                id="w1",
                title="Junior Data Analyst",
                company="MetricsCorp",
                dates="2025 - 2026",
                bullets=[
                    "Analyzed customer engagement metrics across 50,000 records using SQL and Pandas.",
                    "Built automated executive dashboards tracking weekly cohort retention."
                ]
            )
        ],
        education=[EduEntry(id="e1", institution="University of Washington", degree="Bachelor of Science in Statistics", dates="2021 - 2025")],
        sections_detected=["summary", "skills", "experience", "education"],
        parse_confidence=1.0,
        detected_columns=1
    ))

    # 3. Experienced Backend Developer (Missing ML)
    samples.append(ParsedResume(
        filename="cv_03_senior_backend_dev.json",
        contact=ContactInfo(name="Marcus Vance", email="marcus@example.com"),
        summary="Senior Backend Engineer with 5+ years building distributed cloud systems.",
        skills=["python", "fastapi", "docker", "sql", "postgresql", "redis", "aws"],
        work_experience=[
            WorkEntry(
                id="w1",
                title="Senior Backend Engineer",
                company="CloudScale",
                dates="2021 - 2026",
                bullets=[
                    "Architected high-throughput FastAPI microservices serving 40,000 requests per second.",
                    "Containerized 12 core services using Docker and automated CI/CD pipelines.",
                    "Optimized PostgreSQL schema indexes reducing query response times by 65%."
                ]
            )
        ],
        education=[EduEntry(id="e1", institution="Georgia Tech", degree="Bachelor of Science in Computer Engineering", dates="2017 - 2021")],
        sections_detected=["summary", "skills", "experience", "education"],
        parse_confidence=1.0,
        detected_columns=1
    ))

    # 4. Keyword Stuffer
    samples.append(ParsedResume(
        filename="cv_04_keyword_stuffer.json",
        contact=ContactInfo(name="Sam Taylor", email="sam@example.com"),
        summary="Tech professional with broad exposure across modern software stacks.",
        skills=["python", "pytorch", "scikit-learn", "sql", "docker", "fastapi", "pandas", "numpy", "ci/cd", "kubernetes", "tensorflow", "spark", "hadoop", "c++", "java"],
        work_experience=[
            WorkEntry(
                id="w1",
                title="Technical Associate",
                company="General Systems",
                dates="2025 - 2026",
                bullets=[
                    "Worked on various assigned tasks across the team.",
                    "Assisted with general code maintenance and meetings."
                ]
            )
        ],
        education=[EduEntry(id="e1", institution="State College", degree="Bachelor of Arts in General Studies", dates="2020 - 2024")],
        sections_detected=["summary", "skills", "experience", "education"],
        parse_confidence=0.8,
        detected_columns=1
    ))

    # 5. Missing Education & Certifications
    samples.append(ParsedResume(
        filename="cv_05_missing_education.json",
        contact=ContactInfo(name="Jordan Reed", email="jordan@example.com"),
        summary="Self-taught Machine Learning developer with open-source project portfolio.",
        skills=["python", "pytorch", "docker", "fastapi", "scikit-learn"],
        work_experience=[
            WorkEntry(
                id="w1",
                title="ML Developer",
                company="Open Source Contributor",
                dates="2024 - 2026",
                bullets=[
                    "Trained PyTorch computer vision models on 10,000 images achieving 89% mAP.",
                    "Built FastAPI service containerized in Docker for real-time edge inference."
                ]
            )
        ],
        education=[],  # Missing education
        sections_detected=["summary", "skills", "experience"],
        parse_confidence=0.75,
        detected_columns=1
    ))

    # 6. Non-Technical Profile
    samples.append(ParsedResume(
        filename="cv_06_non_technical.json",
        contact=ContactInfo(name="Chloe Davis", email="chloe@example.com"),
        summary="Account Manager and Sales Executive with 4 years client relationship experience.",
        skills=["sales", "client management", "crm", "lead generation", "negotiation", "communication"],
        work_experience=[
            WorkEntry(
                id="w1",
                title="Account Executive",
                company="SalesForce Partners",
                dates="2022 - 2026",
                bullets=[
                    "Managed portfolio of 35 corporate accounts generating $1.2M in annual revenue.",
                    "Conducted weekly client presentations and closed 92% of qualified inbound leads."
                ]
            )
        ],
        education=[EduEntry(id="e1", institution="Boston University", degree="Bachelor of Science in Business Administration", dates="2018 - 2022")],
        sections_detected=["summary", "skills", "experience", "education"],
        parse_confidence=1.0,
        detected_columns=1
    ))

    return samples


def build_bulk_cvs() -> list[ParsedResume]:
    """Generate 30 bulk candidate CV profiles spanning realistic variations."""
    bulk = []
    
    # Check if local PDF files exist in Desktop 'Resumes and CVs'
    desktop_cv_dir = Path("c:/Users/HP/Desktop/dhruv/Resumes and CVs")
    if desktop_cv_dir.exists():
        pdf_files = list(desktop_cv_dir.glob("*.pdf"))
        for p in pdf_files:
            try:
                with open(p, "rb") as f:
                    parsed = parse_pdf_bytes(f.read(), filename=p.name)
                    if parsed and len(parsed.skills) > 0:
                        bulk.append(parsed)
            except Exception:
                pass

    # Ensure we reach exactly 30 bulk CVs by generating structured profile variations
    names = [
        "Devon Patel", "Elena Rostova", "Kavya Nair", "Rohan Mehta", "Sarah Connor",
        "Wei Zhang", "Tariq Mansoor", "Aisha Al-Mansoor", "Lucas Silva", "Hannah Schmidt",
        "Ananya Sharma", "Dmitri Volkov", "Priya Sen", "Carlos Mendez", "Fatima Zahra",
        "James Wilson", "Mei Lin", "Arjun Reddy", "Zoe Kravitz", "Kenji Sato",
        "Gabriel Dupont", "Sunita Rao", "Mateo Rossi", "Fatima Hassan", "Vikram Malhotra",
        "Olga Ivanova", "Rahul Bose", "Camila Fernandez", "Jin Woo", "Nadia Petrova"
    ]

    skill_profiles = [
        ["python", "pytorch", "docker", "sql", "pandas"],
        ["python", "fastapi", "sql", "numpy", "docker"],
        ["sql", "python", "pandas", "tableau"],
        ["python", "scikit-learn", "pandas", "numpy"],
        ["docker", "kubernetes", "python", "ci/cd"],
        ["python", "pytorch", "fastapi", "docker", "scikit-learn", "sql", "pandas", "numpy"],
        ["react", "node.js", "typescript", "python"],
        ["python", "sql", "aws", "docker"],
        ["pytorch", "python", "opencv", "computer vision"],
        ["fastapi", "python", "postgresql", "redis"]
    ]

    needed = max(0, 30 - len(bulk))
    for i in range(needed):
        name = names[i % len(names)]
        skills = skill_profiles[i % len(skill_profiles)]
        exp_yrs = 1.0 + (i % 5)
        bulk.append(ParsedResume(
            filename=f"bulk_cv_{i+1:02d}_{name.replace(' ', '_').lower()}.json",
            contact=ContactInfo(name=name, email=f"{name.replace(' ', '.').lower()}@example.com"),
            summary=f"Software & ML practitioner with {exp_yrs:.1f} years practical engineering experience.",
            skills=skills,
            work_experience=[
                WorkEntry(
                    id="w1",
                    title="Software Engineer",
                    company=f"TechCorp {i+1}",
                    dates=f"{2026 - int(exp_yrs)} - 2026",
                    bullets=[
                        f"Developed core software modules utilizing {skills[0]} and {skills[1] if len(skills) > 1 else 'tools'}.",
                        f"Delivered microservices with 99.8% uptime handling real-time data flows."
                    ]
                )
            ],
            education=[EduEntry(id="e1", institution="Technical University", degree="Bachelor of Technology in Computer Science", dates="2020 - 2024")],
            sections_detected=["summary", "skills", "experience", "education"],
            parse_confidence=0.95,
            detected_columns=1
        ))

    return bulk[:30]


def run_regression_suite():
    print("=" * 85)
    print("NOETRIX ATS REGRESSION BENCHMARK — DETERMINISTIC ENGINE (LLM_MODE=OFF)")
    print("=" * 85)

    # Load Target JD (JD 01: Associate / Junior ML Engineer)
    labels_file = backend_root / "data" / "samples" / "jd_labels.json"
    with open(labels_file, "r", encoding="utf-8") as f:
        jds = json.load(f)
    jd = parse_job_description(jds[0]["text"])

    print(f"Target Role: {jd.title}")
    print(f"Must-Have Skills ({len(jd.must_have_skills)}): {', '.join(jd.must_have_skills)}")
    print(f"Min Experience Required: {jd.min_experience_years} yrs\n")

    samples = build_canonical_sample_cvs()
    bulk = build_bulk_cvs()

    # Pre-calibrated baselines for the 6 canonical samples
    # Under old buggy baseline:
    # - Must-have cap falsely capped any CV missing 1 skill to 50.0
    # - Semantic was raw unscaled cosine * 100
    # - Impact counted wrapped lines
    old_baselines = {
        "cv_01_strong_ml_engineer.json": 50.0,    # Falsely capped at 50
        "cv_02_junior_data_analyst.json": 46.2,
        "cv_03_senior_backend_dev.json": 50.0,    # Falsely capped at 50
        "cv_04_keyword_stuffer.json": 34.1,
        "cv_05_missing_education.json": 41.5,
        "cv_06_non_technical.json": 18.5,
    }

    print("-" * 85)
    print(f"{'PART 1: 6 CANONICAL ARCHETYPE CVs':^85}")
    print("-" * 85)
    print(f"{'CANDIDATE / PROFILE':<32} | {'OLD SCORE':<10} | {'NEW SCORE':<10} | {'DELTA':<8} | {'BAND':<10} | {'CAPPED?'}")
    print("-" * 85)

    for cv in samples:
        res = score_resume_against_jd(cv, jd)
        old = old_baselines.get(cv.filename, 50.0)
        delta = res.overall_score - old
        sign = "+" if delta >= 0 else ""
        capped_str = "YES (Cap 50)" if res.is_capped else "No"
        print(f"{cv.filename[:32]:<32} | {old:>8.1f}% | {res.overall_score:>8.1f}% | {sign}{delta:>6.1f}% | {res.match_band:<10} | {capped_str}")

    print("\n" + "-" * 85)
    print(f"{'PART 2: 30 BULK CANDIDATE CVs BATCH AUDIT':^85}")
    print("-" * 85)
    print(f"{'CANDIDATE NAME / FILE':<35} | {'NEW SCORE':<10} | {'BAND':<10} | {'MUST-HAVE COV':<14} | {'STATUS'}")
    print("-" * 85)

    strong_count = 0
    mod_count = 0
    weak_count = 0

    for idx, cv in enumerate(bulk, 1):
        res = score_resume_against_jd(cv, jd)
        name = cv.contact.name or cv.filename.replace(".pdf", "").replace(".json", "")
        mh_cov = f"{len([s for s in jd.must_have_skills if s in [m.lower() for m in res.matched_keywords]])}/{len(jd.must_have_skills)}"
        
        if res.match_band == "strong":
            strong_count += 1
            status = "Shortlist"
        elif res.match_band == "moderate":
            mod_count += 1
            status = "Review"
        else:
            weak_count += 1
            status = "Knockout"

        print(f"{name[:35]:<35} | {res.overall_score:>8.1f}% | {res.match_band:<10} | {mh_cov:<14} | {status}")

    print("-" * 85)
    print(f"BATCH SUMMARY -> Total CVs: {len(bulk)} | Strong: {strong_count} | Moderate: {mod_count} | Weak: {weak_count}")
    print("=" * 85 + "\n")


if __name__ == "__main__":
    run_regression_suite()
