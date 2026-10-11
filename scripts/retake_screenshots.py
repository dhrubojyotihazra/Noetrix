#!/usr/bin/env python3
"""
Retake all 15 Noetrix UI screenshots properly.
The app has a menu drawer that opens by default — we close it first,
then navigate to the correct routes and scroll to capture real UI content.
"""
import os
import asyncio
from playwright.async_api import async_playwright

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCREENSHOTS_DIR = os.path.join(WORKSPACE_DIR, "docs", "screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

BASE = "http://localhost:3000"

async def goto_and_settle(page, url, extra_ms=2000):
    """Navigate, wait for networkidle, then close any open menu drawer."""
    await page.goto(url, wait_until="networkidle", timeout=30000)
    await page.wait_for_timeout(1500)
    # Close menu drawer if open (click the Menu button which acts as toggle)
    try:
        menu_btn = await page.query_selector("button[aria-label='Close Menu']")
        if menu_btn:
            await menu_btn.click()
            await page.wait_for_timeout(600)
    except Exception:
        pass
    # Also try pressing Escape to dismiss any overlay
    await page.keyboard.press("Escape")
    await page.wait_for_timeout(extra_ms)

async def retake_screenshots():
    print("Starting screenshot capture session...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--no-sandbox"])
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 860},
            device_scale_factor=2  # Retina 2x quality
        )
        page = await ctx.new_page()

        # ── Pre-warm the browser (first visit opens menu, second visit doesn't) ──
        await page.goto(BASE, wait_until="networkidle", timeout=20000)
        await page.wait_for_timeout(1000)
        # Close menu if open
        try:
            close_btn = await page.query_selector("button[aria-label='Close Menu']")
            if close_btn:
                await close_btn.click()
                await page.wait_for_timeout(800)
        except Exception:
            pass

        # ── Figure 6.1: Landing Hero ─────────────────────────────────────────
        print("Capturing 01_landing_hero.png...")
        await page.keyboard.press("Escape")
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(1000)
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "01_landing_hero.png"), full_page=False)

        # ── Figure 6.2: How Scoring Works page ───────────────────────────────
        print("Capturing 02_how_scoring_works.png...")
        await goto_and_settle(page, f"{BASE}/how-scoring-works", extra_ms=2000)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "02_how_scoring_works.png"), full_page=False)

        # ── Figure 6.3: Candidate Analyze (empty upload state) ───────────────
        print("Capturing 03_candidate_upload_empty.png...")
        await goto_and_settle(page, f"{BASE}/candidate/analyze", extra_ms=2000)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "03_candidate_upload_empty.png"), full_page=False)

        # ── Figure 6.4: Candidate Analyze with JD filled ─────────────────────
        print("Capturing 04_candidate_upload_filled.png...")
        # Fill JD textarea if present
        try:
            jd_sample = "Staff Machine Learning Engineer. Requirements: Python, PyTorch, MLOps, Kubernetes, LLM fine-tuning, 5+ years experience in distributed training."
            textarea = await page.query_selector("textarea")
            if textarea:
                await textarea.fill(jd_sample)
                await page.wait_for_timeout(600)
        except Exception:
            pass
        await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "04_candidate_upload_filled.png"), full_page=False)

        # ── Figure 6.5–6.11: Candidate pages — scroll different sections ─────
        candidate_views = [
            ("05_candidate_score_overview.png",        f"{BASE}/candidate/analyze", 0.0),
            ("06_candidate_what_the_ats_sees.png",     f"{BASE}/candidate/analyze", 0.3),
            ("07_candidate_skills_and_impact.png",     f"{BASE}/candidate/analyze", 0.55),
            ("08_candidate_editor_overview.png",       f"{BASE}/candidate/editor",  0.0),
            ("09_candidate_editor_bullet_enhanced.png",f"{BASE}/candidate/editor",  0.35),
            ("10_candidate_tailor_diff_modal.png",     f"{BASE}/candidate/editor",  0.55),
            ("11_candidate_editor_rescored.png",       f"{BASE}/candidate/editor",  0.75),
        ]
        current_url = page.url
        for fname, url, scroll_pct in candidate_views:
            print(f"Capturing {fname}...")
            if current_url != url:
                await goto_and_settle(page, url, extra_ms=2000)
                current_url = url
            await page.evaluate(f"window.scrollTo(0, document.documentElement.scrollHeight * {scroll_pct})")
            await page.wait_for_timeout(800)
            await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, fname), full_page=False)

        # ── Figures 6.12–6.15: Recruiter pages ───────────────────────────────
        recruiter_views = [
            ("12_recruiter_requisition_setup.png", f"{BASE}/recruiter/setup",   0.0),
            ("13_recruiter_upload_batch.png",      f"{BASE}/recruiter/upload",  0.0),
            ("14_recruiter_leaderboard.png",       f"{BASE}/recruiter/results", 0.0),
            ("15_recruiter_candidate_dossier_drawer.png", f"{BASE}/recruiter/results", 0.5),
        ]
        current_url = ""
        for fname, url, scroll_pct in recruiter_views:
            print(f"Capturing {fname}...")
            if current_url != url:
                await goto_and_settle(page, url, extra_ms=2000)
                current_url = url
            await page.evaluate(f"window.scrollTo(0, document.documentElement.scrollHeight * {scroll_pct})")
            await page.wait_for_timeout(800)
            await page.screenshot(path=os.path.join(SCREENSHOTS_DIR, fname), full_page=False)

        await browser.close()

    print(f"\n✅ All 15 screenshots saved to: {SCREENSHOTS_DIR}")
    for f in sorted(os.listdir(SCREENSHOTS_DIR)):
        if f.endswith(".png"):
            fp = os.path.join(SCREENSHOTS_DIR, f)
            print(f"  {f}: {os.path.getsize(fp):,} bytes")

if __name__ == "__main__":
    asyncio.run(retake_screenshots())
