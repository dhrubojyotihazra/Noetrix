import os
import time
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = os.path.abspath("docs/screenshots")
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
SAMPLE_PDF = os.path.abspath("sample_resume_alex_chen.pdf")

def run():
    print("=" * 65)
    print("Capturing Noetrix Full End-to-End Workflow & Screens")
    print(f"Screenshots directory: {SCREENSHOTS_DIR}")
    print("=" * 65)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 960},
            device_scale_factor=2
        )
        page = context.new_page()

        # -------------------------------------------------------------
        # 1. Landing Page
        # -------------------------------------------------------------
        print("\n[1/15] Screen 01: Landing Page Hero & Navigation...")
        page.goto("http://localhost:3000", wait_until="networkidle")
        time.sleep(1.5)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "01_landing_hero.png"), full_page=False)

        # -------------------------------------------------------------
        # 2. How Scoring Works
        # -------------------------------------------------------------
        print("[2/15] Screen 02: Transparent Scoring Methodology...")
        page.goto("http://localhost:3000/how-scoring-works", wait_until="networkidle")
        time.sleep(1.5)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "02_how_scoring_works.png"), full_page=False)

        # -------------------------------------------------------------
        # 3. Candidate Upload: Empty State
        # -------------------------------------------------------------
        print("[3/15] Screen 03: Candidate Door - Scanner Empty State...")
        page.goto("http://localhost:3000/candidate/analyze", wait_until="networkidle")
        time.sleep(1.5)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "03_candidate_upload_empty.png"), full_page=False)

        # -------------------------------------------------------------
        # 4. Candidate Upload: Filled State
        # -------------------------------------------------------------
        print("[4/15] Screen 04: Candidate Door - Uploaded CV & Target JD...")
        page.locator("button:has-text('Preset 1')").click()
        page.set_input_files("#resume-file", SAMPLE_PDF)
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "04_candidate_upload_filled.png"), full_page=False)

        # -------------------------------------------------------------
        # 5. Candidate Report: Score Overview
        # -------------------------------------------------------------
        print("[5/15] Screen 05: Candidate Audit Report - Overall Scorecard...")
        page.locator("button:has-text('Analyze & Generate Report')").click()
        page.wait_for_url("**/candidate/report", timeout=35000)
        time.sleep(2)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "05_candidate_score_overview.png"), full_page=False)

        # -------------------------------------------------------------
        # 6. Candidate Diagnostic: What the ATS Sees
        # -------------------------------------------------------------
        print("[6/15] Screen 06: 'What the ATS Sees' OpenResume Diagnostic View...")
        page.evaluate("window.scrollTo({top: 1150, behavior: 'instant'})")
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "06_candidate_what_the_ats_sees.png"), full_page=False)

        # -------------------------------------------------------------
        # 7. Candidate Report: Skills Gap & Impact Breakdown
        # -------------------------------------------------------------
        print("[7/15] Screen 07: Skills Gap & Action Verb Analysis...")
        page.evaluate("window.scrollTo({top: 600, behavior: 'instant'})")
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "07_candidate_skills_and_impact.png"), full_page=False)

        # -------------------------------------------------------------
        # 8. AI Resume Editor: Overview
        # -------------------------------------------------------------
        print("[8/15] Screen 08: AI Resume Editor & Live Rescoring Canvas...")
        page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
        time.sleep(0.5)
        page.locator("a:has-text('Open AI Resume Editor')").click()
        page.wait_for_url("**/candidate/editor", timeout=15000)
        time.sleep(2)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "08_candidate_editor_overview.png"), full_page=False)

        # -------------------------------------------------------------
        # 9. AI Resume Editor: Bullet Enhancement
        # -------------------------------------------------------------
        print("[9/15] Screen 09: Bullet Enhancement & Missing Skill Pill Addition...")
        skill_input = page.locator("input[placeholder*='Type a skill']")
        if skill_input.count() > 0:
            skill_input.fill("distributed systems")
            page.locator("button:has-text('Add Skill')").click()
            time.sleep(0.5)

        # Click the first bullet sparkle enhance button
        sparkle_btn = page.locator("button[title*='Strengthen action verb']").first
        if sparkle_btn.count() > 0:
            sparkle_btn.click()
            time.sleep(2)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "09_candidate_editor_bullet_enhanced.png"), full_page=False)

        # -------------------------------------------------------------
        # 10. AI Tailoring: Side-by-Side Diff Preview Modal
        # -------------------------------------------------------------
        print("[10/15] Screen 10: AI Tailoring Side-by-Side Diff Preview Modal...")
        tailor_btn = page.locator("button:has-text('Tailor Experience')")
        if tailor_btn.count() > 0:
            tailor_btn.click()
            time.sleep(2.5)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "10_candidate_tailor_diff_modal.png"), full_page=False)

        # Select all diffs and apply
        print("Selecting all diffs and applying...")
        page.get_by_role("button", name="Select All", exact=True).click()
        time.sleep(0.5)

        apply_btn = page.locator("button:has-text('Apply Selected')")
        if apply_btn.count() > 0:
            apply_btn.click()
            time.sleep(2)

        # -------------------------------------------------------------
        # 11. Rescored Editor & Template Selection
        # -------------------------------------------------------------
        print("[11/15] Screen 11: Rescored Resume Canvas & ATS-Safe Template...")
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "11_candidate_editor_rescored.png"), full_page=False)

        # -------------------------------------------------------------
        # 12. Recruiter Door: Requisition Setup
        # -------------------------------------------------------------
        print("[12/15] Screen 12: Recruiter Door - Requisition Setup...")
        page.goto("http://localhost:3000/recruiter/setup", wait_until="networkidle")
        time.sleep(1.5)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "12_recruiter_requisition_setup.png"), full_page=False)

        # -------------------------------------------------------------
        # 13. Recruiter Door: Bulk Ingestion Queue
        # -------------------------------------------------------------
        print("[13/15] Screen 13: Recruiter Door - Bulk Ingestion Queue...")
        page.locator("button:has-text('Save Requisition & Proceed to Upload')").click()
        page.wait_for_url("**/recruiter/upload", timeout=15000)
        time.sleep(1)
        page.locator("button:has-text('Load 5 Demo Candidate Resumes')").click()
        time.sleep(1.5)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "13_recruiter_upload_batch.png"), full_page=False)

        # -------------------------------------------------------------
        # 14. Recruiter Door: Explainable Leaderboard
        # -------------------------------------------------------------
        print("[14/15] Screen 14: Recruiter Door - Explainable Leaderboard...")
        page.locator("button:has-text('Score & Rank')").click()
        page.wait_for_url("**/recruiter/results", timeout=45000)
        time.sleep(2.5)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "14_recruiter_leaderboard.png"), full_page=False)

        # -------------------------------------------------------------
        # 15. Recruiter Door: Candidate Dossier Drawer
        # -------------------------------------------------------------
        print("[15/15] Screen 15: Recruiter Door - Candidate Dossier Inspection Drawer...")
        inspect_span = page.locator("span:has-text('Inspect')").first
        if inspect_span.count() > 0:
            inspect_span.click()
            time.sleep(1.5)
        page.screenshot(path=os.path.join(SCREENSHOTS_DIR, "15_recruiter_candidate_dossier_drawer.png"), full_page=False)

        print("\n" + "=" * 65)
        print("SUCCESS! ALL 15 PRODUCTION-QUALITY SCREENSHOTS CAPTURED!")
        print(f"Files saved in: {SCREENSHOTS_DIR}")
        print("=" * 65)
        browser.close()

if __name__ == "__main__":
    run()
