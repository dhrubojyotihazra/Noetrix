"""Unit tests for Noetrix MCP Server tools."""

import pytest
from app.mcp_server import (
    score_resume,
    score_resume_file,
    parse_resume,
    parse_resume_file,
    parse_job_description,
    rank_resumes,
    explain_score,
)

SAMPLE_RESUME = """
Alex Chen
alex.chen@example.com | (555) 234-5678 | San Francisco, CA

Professional Summary
Senior Backend Engineer with 5+ years of experience designing and deploying distributed systems and RESTful APIs using Python, FastAPI, Docker, and PostgreSQL.

Technical Skills
Python, FastAPI, Docker, PostgreSQL, Redis, Kubernetes, AWS, Git, CI/CD

Work Experience
Senior Backend Engineer | DataCloud Inc. | 2022 - Present
• Architected and developed FastAPI microservices handling 4,500 RPS with sub-45ms P99 latency.
• Optimized PostgreSQL query performance by 35% through connection pooling and index optimization.
• Containerized services with Docker and deployed onto AWS EKS using Helm charts.

Software Engineer | TechStart Labs | 2019 - 2022
• Developed REST APIs using Python and Flask, improving data ingestion throughput by 50%.
• Implemented Redis caching layer reducing database read load by 40%.

Education
Bachelor of Science in Computer Science | University of California, Berkeley | 2015 - 2019
"""

SAMPLE_JD = """
Senior Python Backend Engineer
Location: San Francisco, CA (Hybrid)

Requirements:
• 4+ years of professional software development experience.
• Must have strong expertise in Python and FastAPI.
• Must have hands-on experience with Docker and PostgreSQL.
• Preferred: experience with Redis, AWS, and Kubernetes.
• Bachelor's degree in Computer Science or related quantitative field.

Responsibilities:
• Build high-performance scalable backend APIs.
• Optimize database schemas and distributed workflows.
"""


def test_score_resume_returns_valid_structure():
    """Verify score_resume returns complete 6-metric scorecard."""
    result = score_resume(SAMPLE_RESUME, SAMPLE_JD)

    assert "overall_score" in result
    assert "match_band" in result
    assert "metrics" in result
    assert len(result["metrics"]) == 6
    assert result["match_band"] in ("strong", "moderate", "weak")
    assert result["overall_score"] >= 0.0 and result["overall_score"] <= 100.0
    assert not result["is_capped"]  # Has all must-haves
    assert "fastapi" in [k.lower() for k in result["matched_keywords"]]
    assert "docker" in [k.lower() for k in result["matched_keywords"]]


def test_score_resume_anti_gaming_knockout():
    """Verify 50% Soft Knockout triggers when must-haves are missing."""
    sales_resume = """
    Bob Johnson
    bob@example.com
    Experience: 10 years in enterprise B2B sales and sales leadership.
    Closed $5M in ARR.
    """
    result = score_resume(sales_resume, SAMPLE_JD)

    assert result["overall_score"] <= 50.0
    assert result["match_band"] == "weak"


def test_parse_resume_extracts_entities():
    """Verify parse_resume extracts contact, skills, and work history."""
    parsed = parse_resume(SAMPLE_RESUME)

    assert parsed["candidate_name"] == "Alex Chen"
    assert parsed["contact"]["email"] == "alex.chen@example.com"
    assert len(parsed["skills"]) >= 5
    assert len(parsed["work_experience"]) >= 1
    assert len(parsed["education"]) >= 1
    assert parsed["parse_confidence"] > 0.5


def test_parse_job_description():
    """Verify parse_job_description extracts must-haves and criteria."""
    jd = parse_job_description(SAMPLE_JD, title="Senior Python Backend Engineer")

    assert jd["title"] == "Senior Python Backend Engineer"
    assert jd["min_experience_years"] >= 3.0
    assert any("python" in s.lower() for s in jd["must_have_skills"])
    assert any("fastapi" in s.lower() for s in jd["must_have_skills"])


def test_rank_resumes_leaderboard():
    """Verify rank_resumes returns correctly sorted candidate rankings."""
    weak_resume = """
    Jane Doe
    jane@example.com
    Junior Graphic Designer with 1 year experience in Adobe Photoshop.
    """
    candidates = [
        {"name": "Jane Designer", "resume_text": weak_resume},
        {"name": "Alex Engineer", "resume_text": SAMPLE_RESUME},
    ]

    leaderboard = rank_resumes(candidates, SAMPLE_JD)

    assert len(leaderboard) == 2
    assert leaderboard[0]["rank"] == 1
    assert leaderboard[0]["candidate_name"] == "Alex Engineer"
    assert leaderboard[0]["overall_score"] > leaderboard[1]["overall_score"]
    assert leaderboard[1]["rank"] == 2


def test_explain_score_dossier():
    """Verify explain_score provides strengths, gaps, and anti-gaming status."""
    explanation = explain_score(SAMPLE_RESUME, SAMPLE_JD)

    assert "strengths" in explanation
    assert "gaps" in explanation
    assert "anti_gaming_analysis" in explanation
    assert "verdict" in explanation
    assert explanation["anti_gaming_analysis"]["is_capped"] is False


def test_empty_input_validation():
    """Verify proper validation errors on empty inputs."""
    with pytest.raises(ValueError):
        score_resume("", SAMPLE_JD)

    with pytest.raises(ValueError):
        score_resume(SAMPLE_RESUME, "")
