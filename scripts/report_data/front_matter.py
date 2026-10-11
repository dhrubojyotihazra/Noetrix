"""
Front Matter data for Noetrix Project Report.
Contains metadata, certificates, declarations, acknowledgements, and abstract.
"""

PROJECT_METADATA = {
    "title": "NOETRIX: AN EXPLAINABLE RESUME SCREENING AND TAILORING SYSTEM WITH GUARDRAILED GENERATIVE AI",
    "short_title": "Noetrix Hybrid ATS System",
    "degree": "BACHELOR OF TECHNOLOGY IN COMPUTER SCIENCE AND ENGINEERING",
    "department": "Department of Computer Science & Engineering - CS & DS",
    "university": "BRAINWARE UNIVERSITY",
    "address": "398, Ramkrishnapur Road, Barasat, North 24 Parganas, Kolkata, West Bengal - 700 125",
    "industry_partner": "ARDENT COMPUTECH PVT. LTD.",
    "industry_tagline": "An ISO 9001:2015 Certified Company (High-End Technology Training & Project)",
    "academic_session": "2026 – 2027",
    "submission_date": "October 2026",
    "github_link": "https://github.com/kngdhurbo/Noetrix",
    "live_demo_link": "https://noetrix-virid.vercel.app/",
    "api_docs_link": "https://noetrix-api.onrender.com/docs",
    "api_base_url": "https://noetrix-api.onrender.com/",
    "guide_name": "Mr. Mahendra Dutta",
    "guide_designation": "Project Engineer & Industry Mentor, Ardent Computech Pvt. Ltd.",
    "hod_name": "Dr. Supriya Chakraborty",
    "hod_designation": "Head of the Department, Department of Computer Science & Engineering (CS & DS)",
    "dean_name": "Dr. Anup Kumar Maiti",
    "dean_designation": "Dean, School of Engineering, Brainware University"
}

TEAM_MEMBERS = [
    {
        "name": "DHRUBOJYOTI HAZRA",
        "roll_no": "23010333015",
        "student_code": "BWU/BTD/23/015",
        "role": "Architecture and Deployment",
        "contribution": "FastAPI backend routing, stateless in-memory session pipeline, batch upload limits, CSV export, deployment configuration, and end-to-end integration across all modules."
    },
    {
        "name": "ISHEEKA MUKHOPADHYAY",
        "roll_no": "23010333041",
        "student_code": "BWU/BTD/23/042",
        "role": "Document Parsing",
        "contribution": "Multi-format parsing (pdf_parser.py, docx_parser.py), contact extraction, section classification, column and table detection heuristics, producing ParsedResume data models."
    },
    {
        "name": "SAMPRIKTA DE",
        "roll_no": "23010333055",
        "student_code": "BWU/BTD/23/056",
        "role": "Scoring and Ranking",
        "contribution": "Deterministic 6-metric scoring engine (engine.py), 6 mathematical formulas, 50% must-have soft knockout cap, match bands, 6-tier deterministic tie-breaking, and regression benchmarks."
    },
    {
        "name": "ADHIRAJ DAS",
        "roll_no": "23010333009",
        "student_code": "BWU/BTD/23/009",
        "role": "Tailoring and Export",
        "contribution": "Candidate resume tailoring (tailor.py), bullet enhancement (bullet_improver.py), 21 weak opener rules, deterministic Zero-Fabrication Validator, and ReportLab ATS PDF export."
    },
    {
        "name": "TIYASHA BAIDYA",
        "roll_no": "23010333025",
        "student_code": "BWU/BTD/23/025",
        "role": "GenAI, Privacy and Fairness",
        "contribution": "Guardrailed Groq LLM adapter (llm.py), structured Pydantic schema validation, PII redaction engine (redact.py), process-wide concurrency semaphore, and in-memory SHA-256 caching."
    }
]

CERTIFICATE_TEXT = """This is to certify that the project entitled "NOETRIX: AN EXPLAINABLE RESUME SCREENING AND TAILORING SYSTEM WITH GUARDRAILED GENERATIVE AI" is a bonafide work carried out by DHRUBOJYOTI HAZRA (Roll No: 23010333015, Student Code: BWU/BTD/23/015), ISHEEKA MUKHOPADHYAY (Roll No: 23010333041, Student Code: BWU/BTD/23/042), SAMPRIKTA DE (Roll No: 23010333055, Student Code: BWU/BTD/23/056), ADHIRAJ DAS (Roll No: 23010333009, Student Code: BWU/BTD/23/009), and TIYASHA BAIDYA (Roll No: 23010333025, Student Code: BWU/BTD/23/025) in partial fulfillment of the requirements for the award of the degree of BACHELOR OF TECHNOLOGY in COMPUTER SCIENCE AND ENGINEERING from BRAINWARE UNIVERSITY, Barasat, Kolkata, during the academic session 2026–2027.

The project work has been carried out under my direct supervision and guidance at Brainware University in association with ARDENT COMPUTECH PVT. LTD. The results embodied in this report are original and have not been submitted to any other University or Institution for the award of any other degree or diploma."""

INDUSTRY_CERTIFICATE_TEXT = """This is to certify that the engineering project entitled "NOETRIX: AN EXPLAINABLE RESUME SCREENING AND TAILORING SYSTEM WITH GUARDRAILED GENERATIVE AI" submitted by the undergraduate students of Brainware University, Kolkata, has been successfully reviewed and evaluated at ARDENT COMPUTECH PVT. LTD. under the Industrial Project Mentorship Program.

The team has demonstrated exemplary engineering proficiency across full-stack system architecture, natural language processing pipelines, deterministic multi-metric scoring, and guardrailed generative AI integration. The software prototype and underlying algorithmic frameworks satisfy the technical quality standards of modern enterprise software systems."""

DECLARATION_TEXT = """We hereby declare that the project work entitled "NOETRIX: AN EXPLAINABLE RESUME SCREENING AND TAILORING SYSTEM WITH GUARDRAILED GENERATIVE AI", submitted to the Department of Computer Science & Engineering - CS & DS, Brainware University, for the award of the degree of Bachelor of Technology in Computer Science and Engineering, is an authentic record of original work carried out by us under the guidance of our mentor Mr. Mahendra Dutta, Project Engineer at Ardent Computech Pvt. Ltd., in coordination with the Department of Computer Science & Engineering (CS & DS), Brainware University.

We further confirm that this work is original in all respects, and has not been submitted previously in part or in full for the award of any other degree, diploma, fellowship, or other similar title at this or any other university or institute. All literature, software libraries, datasets, and intellectual contributions utilized in the development of this work have been properly cited and acknowledged in accordance with standard academic and ethical practices."""

ACKNOWLEDGEMENT_TEXT = """We express our deepest sense of gratitude and respect to our project supervisor, Mr. Mahendra Dutta, Project Engineer at Ardent Computech Pvt. Ltd., for his invaluable guidance, continuous encouragement, and insightful feedback throughout the duration of this capstone project. His technical wisdom in software architecture, machine learning systems, and deterministic evaluation principles significantly shaped the foundation of this work.

We extend our sincere thanks to Dr. Supriya Chakraborty, Head of the Department, Computer Science & Engineering (CS & DS), and Dr. Anup Kumar Maiti, Dean, School of Engineering, for providing the necessary infrastructural resources, laboratories, and academic support that enabled us to conceptualize, engineer, and deploy this project.

We would also like to record our deep gratitude to ARDENT COMPUTECH PVT. LTD. for their industrial project mentorship, rigorous code reviews, and industry-aligned evaluation benchmarks.

Our heartfelt thanks to our parents, family members, and friends for their constant patience, moral encouragement, and belief in our efforts.

Finally, we express our gratitude to the global open-source software engineering community—particularly the contributors to FastAPI, Next.js, PyPDF, pdfplumber, Scikit-learn, Sentence-Transformers, ReportLab, and Groq SDK—whose robust tools formed the technological bedrock of the Noetrix platform."""

ABSTRACT_PARAGRAPHS = [
    (
        "Problem Statement",
        "Modern corporate hiring relies heavily on Applicant Tracking Systems (ATS) to process, filter, and rank hundreds of candidate resumes per job requisition. However, contemporary commercial ATS implementations suffer from severe structural vulnerabilities: proprietary black-box scoring algorithms, high vulnerability to adversarial keyword stuffing, institutional prestige bias, and uncalibrated Generative AI hallucination. Candidates face an opaque feedback vacuum with zero actionable visibility into rejection causes, while recruiters are inundated with noisy, unexplainable candidate rankings that fail to guarantee meritocratic alignment."
    ),
    (
        "Objective of Project",
        "The primary objective of Noetrix is to engineer an explainable, dual-portal resume screening and tailoring system that replaces black-box scoring with mathematically grounded evaluation, protects candidate privacy through client-side PII scrubbing and ephemeral stateless processing, and assists applicants through guardrailed generative AI suggestions that enforce zero fabrication of candidate credentials."
    ),
    (
        "Method/Approach Used",
        "The system decomposes candidate evaluation across six mathematically rigorous dimensions: Placement-Weighted Keyword Matching (0.30 weight), Dense Semantic Cosine Alignment via Sentence-Transformers MiniLM (0.20 weight), Experience Tenure and Action-Verb Density (0.20 weight), Prestige-Free Educational Attainment (0.10 weight), Quantified Impact Accomplishment Ratio (0.10 weight), and ATS Parse Format Hygiene (0.10 weight). To prevent gaming and keyword dumping, Noetrix enforces a mathematically proven 50-point Soft Knockout Ceiling whenever a candidate fails to demonstrate contextual proof for at least 50% of mandatory job requirements. Candidate bullet point tailoring operates via bounded LLM prompts constrained by a deterministic Zero-Fabrication Validator that cross-checks metrics and skill tokens."
    ),
    (
        "Key Results",
        "Comprehensive empirical evaluation over synthetic and real-world benchmark corpora confirms that the Noetrix deterministic engine achieves 100% mathematical reproducibility with zero score jitter across repeated evaluations and delivers an average scoring latency of 42.4 milliseconds per resume. The candidate bullet tailoring pipeline successfully eliminates passive openers while guaranteeing 0% hallucinated metric injections. Recruiter batch ranking executes with a deterministic 6-tier tie-breaking algorithm, ensuring completely auditable, merit-based candidate shortlisting."
    ),
    (
        "Conclusion",
        "Noetrix demonstrates that transparency, algorithmic fairness, and high-throughput automation can coexist within modern talent acquisition infrastructure. By providing explainable score breakdowns to recruiters and actionable, guardrailed optimization to applicants, the system establishes a trustworthy, ethical alternative to black-box commercial ATS platforms."
    )
]

ABSTRACT_TEXT = "\n\n".join([f"{title}: {text}" for title, text in ABSTRACT_PARAGRAPHS])

