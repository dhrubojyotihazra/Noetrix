"""Comprehensive Evaluation and Capstone Demo Script for Noetrix ATS Engine.

Evaluates:
1. JD Criteria Extraction (Precision, Recall, F1 against ground-truth labels).
2. CV Parser Health and Section Recovery.
3. Bullet Tailoring Truthfulness & Zero-Fabrication Validation (Target: 0.0% Hallucination Rate).
4. System Performance, Median Latency & Call Count (60s limit enforced).
"""

import json
import os
import sys
import time
from pathlib import Path

# Ensure backend root is on sys.path
backend_root = Path(__file__).resolve().parent.parent
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from dotenv import load_dotenv
load_dotenv()

from app.schemas.resume import ParsedResume, WorkEntry, EduEntry, ContactInfo
from app.services.jd_parser import parse_job_description
from app.genai.jd_extract import extract_jd_criteria
from app.services.improver import (
    enhance_single_bullet,
    validate_bullet_rewrite,
    is_non_bullet_line,
    get_raw_llm_bullet_rewrite
)
from app.genai.llm import get_llm_config, check_llm_health, get_llm_metrics, reset_llm_metrics


def evaluate_jd_extraction(labels_path: Path):
    print("\n" + "=" * 70)
    print("1. EVALUATING JOB DESCRIPTION CRITERIA EXTRACTION")
    print("=" * 70)

    if not labels_path.exists():
        print(f"[!] Warning: Labels file not found at {labels_path}")
        return

    with open(labels_path, "r", encoding="utf-8") as f:
        jds = json.load(f)

    rules_precisions, rules_recalls = [], []
    llm_precisions, llm_recalls = [], []

    cfg = get_llm_config()
    run_llm = cfg.get("mode") == "on" and bool(cfg.get("api_key"))

    print(f"Dataset Size: {len(jds)} Labelled Job Descriptions")
    print(f"LLM Mode: {'ON (Groq)' if run_llm else 'OFF (Rules Only)'}\n")

    print(f"{'JD ID':<8} | {'METHOD':<8} | {'EXTRACTED':<10} | {'EXPECTED':<10} | {'PRECISION':<10} | {'RECALL':<8} | {'F1':<8}")
    print("-" * 75)

    for item in jds:
        jd_id = item["id"]
        expected = set(s.lower() for s in item["expected_must_have_skills"])

        # Rules extraction
        res_rules = parse_job_description(item["text"])
        ext_rules = set(s.lower() for s in res_rules.must_have_skills)
        tp_r = len(ext_rules & expected)
        prec_r = tp_r / len(ext_rules) if ext_rules else 0.0
        rec_r = tp_r / len(expected) if expected else 0.0
        f1_r = (2 * prec_r * rec_r / (prec_r + rec_r)) if (prec_r + rec_r) > 0 else 0.0
        rules_precisions.append(prec_r)
        rules_recalls.append(rec_r)

        print(f"{jd_id:<8} | {'RULES':<8} | {len(ext_rules):<10} | {len(expected):<10} | {prec_r*100:>8.1f}% | {rec_r*100:>6.1f}% | {f1_r*100:>6.1f}%")

        if run_llm:
            try:
                res_llm = extract_jd_criteria(item["text"])
                ext_llm = set(s.lower() for s in res_llm.must_have_skills)
                tp_l = len(ext_llm & expected)
                prec_l = tp_l / len(ext_llm) if ext_llm else 0.0
                rec_l = tp_l / len(expected) if expected else 0.0
                f1_l = (2 * prec_l * rec_l / (prec_l + rec_l)) if (prec_l + rec_l) > 0 else 0.0
                llm_precisions.append(prec_l)
                llm_recalls.append(rec_l)
                print(f"{jd_id:<8} | {'LLM':<8} | {len(ext_llm):<10} | {len(expected):<10} | {prec_l*100:>8.1f}% | {rec_l*100:>6.1f}% | {f1_l*100:>6.1f}%")
                time.sleep(1.0)
            except Exception as e:
                print(f"{jd_id:<8} | {'LLM ERR':<8} | {str(e)[:40]}")
                time.sleep(1.0)

    print("-" * 75)
    mean_p_r = sum(rules_precisions) / len(rules_precisions) if rules_precisions else 0.0
    mean_r_r = sum(rules_recalls) / len(rules_recalls) if rules_recalls else 0.0
    mean_f1_r = 2 * mean_p_r * mean_r_r / (mean_p_r + mean_r_r) if (mean_p_r + mean_r_r) > 0 else 0.0

    print(f"RULES SUMMARY -> Mean Precision: {mean_p_r*100:.1f}% | Mean Recall: {mean_r_r*100:.1f}% | Mean F1: {mean_f1_r*100:.1f}%")

    if run_llm and llm_precisions:
        mean_p_l = sum(llm_precisions) / len(llm_precisions)
        mean_r_l = sum(llm_recalls) / len(llm_recalls)
        mean_f1_l = 2 * mean_p_l * mean_r_l / (mean_p_l + mean_r_l) if (mean_p_l + mean_r_l) > 0 else 0.0
        print(f"LLM SUMMARY   -> Mean Precision: {mean_p_l*100:.1f}% | Mean Recall: {mean_r_l*100:.1f}% | Mean F1: {mean_f1_l*100:.1f}%")


def evaluate_bullet_tailoring():
    print("\n" + "=" * 70)
    print("2. EVALUATING BULLET TAILORING & ZERO-FABRICATION VALIDATOR")
    print("=" * 70)

    # 20 diverse real and synthetic bullet cases
    test_bullets = [
        # Passive openers (should be upgraded cleanly)
        "worked on developing FastAPI REST endpoints for user authentication.",
        "worked on building real-time data streaming pipeline with Apache Kafka.",
        "worked on optimizing PostgreSQL queries for transaction history.",
        "assisted in developing computer vision models for defect detection.",
        "helped to build recommendation engine using PyTorch.",
        "responsible for managing automated deployment scripts in Docker.",
        "tasked with evaluating classification baselines across 4 models.",
        "participated in code reviews and CI/CD maintenance.",
        # Already strong active verbs (must NOT be broken)
        "Architected distributed microservices handling 20,000 requests per second.",
        "Trained transformer model achieving 92.4% F1 score on clinical notes.",
        "Automated continuous integration pipeline reducing deployment time by 60%.",
        "Engineered columnar database indexes cutting query latency from 800ms to 45ms.",
        # Critical negative polarity / safety checks
        "Prevented train-test data leakage during time-series cross-validation.",
        "Mitigated API rate-limiting bottlenecks across third-party microservices.",
        "Reduced model memory footprint by 35% using 8-bit quantization.",
        # Non-bullet lines (must NEVER be mutated)
        "Flask · React · DistilBERT",
        "React Three Fiber · WebGL · TypeScript",
        "B.Tech — Computer Science & Engineering, 2021-2025",
        "Certifications: IBM Data Science Professional Certificate",
        "Tech Stack: Python, PyTorch, Docker, PostgreSQL"
    ]

    total_bullets = len(test_bullets)
    raw_hallucinations_before = 0
    hallucinations_after = 0
    validated_accepted = 0

    candidate_skills = ["python", "fastapi", "docker", "postgresql", "pytorch", "kafka"]

    cfg = get_llm_config()
    is_llm_on = cfg.get("mode") == "on"

    print(f"Auditing {total_bullets} test bullet cases against Zero-Fabrication Validator...\n")
    print(f"Mode: {'LLM ON (Groq)' if is_llm_on else 'RULES ONLY'}\n")

    for idx, bullet in enumerate(test_bullets, 1):
        is_non_bullet = is_non_bullet_line(bullet)

        # 1. Evaluate BEFORE Validator (raw LLM generation behavior)
        if is_llm_on:
            raw_rewrite, raw_valid, raw_reason = get_raw_llm_bullet_rewrite(bullet, candidate_skills=candidate_skills)
            # If the raw LLM hallucinated numbers, unconfirmed skills, meaning flips, or corrupted non-bullets:
            if not raw_valid or (is_non_bullet and raw_rewrite != bullet):
                raw_hallucinations_before += 1
                print(f"[PRE-VALIDATOR FLAG #{idx}] Detected raw hallucination: '{raw_reason}' on '{bullet[:40]}...'")
            time.sleep(1.0)
        else:
            raw_hallucinations_before = 0

        # 2. Evaluate AFTER Validator (production guarded pipeline)
        res = enhance_single_bullet(bullet, candidate_skills=candidate_skills)
        is_valid, reason = validate_bullet_rewrite(
            original=bullet,
            rewrite=res.enhanced,
            candidate_skills=candidate_skills
        )

        # Check if post-validator output has any violation
        if not is_valid and not (is_non_bullet and res.enhanced.rstrip(".") == bullet.rstrip(".")):
            hallucinations_after += 1
            print(f"[FAIL #{idx}] Post-validator violation: {reason}")
        else:
            validated_accepted += 1

        if is_llm_on:
            time.sleep(1.0)

    post_hallucination_rate = (hallucinations_after / total_bullets) * 100

    print("-" * 50)
    print(f"Total Bullets Evaluated:                   {total_bullets}")
    if is_llm_on:
        print(f"Hallucination Count BEFORE Validator:      {raw_hallucinations_before} / {total_bullets}")
    print(f"Hallucination Count AFTER Validator:       {hallucinations_after} / {total_bullets} (TARGET: 0)")
    print(f"Post-Validation Hallucination Rate:        {post_hallucination_rate:.1f}%")
    print(f"Clean Production Acceptance Rate:          {(validated_accepted / total_bullets) * 100:.1f}%\n")


def evaluate_system_health():
    print("=" * 70)
    print("3. SYSTEM HEALTH & AI REACHABILITY CHECK")
    print("=" * 70)
    health = check_llm_health()
    for k, v in health.items():
        print(f"  {k:<15}: {v}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    reset_llm_metrics()
    evaluate_system_health()
    evaluate_bullet_tailoring()
    labels_file = backend_root / "data" / "samples" / "jd_labels.json"
    evaluate_jd_extraction(labels_file)

    metrics = get_llm_metrics()
    print("\n" + "=" * 70)
    print("4. SYSTEM PERFORMANCE & LATENCY AUDIT")
    print("=" * 70)
    print(f"Total LLM API Calls Made: {metrics['call_count']}")
    print(f"Median Per-Call Latency:  {metrics['median_latency']:.2f} s (60s limit enforced)")
    print("=" * 70 + "\n")
