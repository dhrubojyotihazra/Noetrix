#!/usr/bin/env python3
"""
Master Project Report Generator for Noetrix ATS
Generates:
1. docs/Noetrix_Project_Master_Report.html (Self-contained HTML with base64 images & print-CSS)
2. docs/Noetrix_Project_Master_Report.pdf (Compiled publication-grade PDF via Playwright)
3. docs/Noetrix_Project_Master_Report.docx (Word Document conforming to Times New Roman, 1.5 spacing, 1-inch margins, justified)
"""

import os
import sys
import base64
import asyncio
from datetime import datetime

import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

from playwright.async_api import async_playwright

# Import report data modules
from report_data.front_matter import (
    PROJECT_METADATA, TEAM_MEMBERS, CERTIFICATE_TEXT,
    INDUSTRY_CERTIFICATE_TEXT, DECLARATION_TEXT,
    ACKNOWLEDGEMENT_TEXT, ABSTRACT_TEXT
)
from report_data.chapters_1_to_3 import CHAPTER_1_CONTENT, CHAPTER_2_CONTENT, CHAPTER_3_CONTENT
from report_data.chapters_4_to_5 import CHAPTER_4_CONTENT, CHAPTER_5_CONTENT
from report_data.chapters_6_to_7 import CHAPTER_6_CONTENT, CHAPTER_7_CONTENT
from report_data.chapters_8_to_10_and_appendix import (
    CHAPTER_8_CONTENT, CHAPTER_9_CONTENT, CHAPTER_10_CONTENT,
    REFERENCES_LIST, APPENDICES_CONTENT
)

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_DIR = os.path.join(WORKSPACE_DIR, "docs")
ASSETS_DIR = os.path.join(DOCS_DIR, "assets")
SCREENSHOTS_DIR = os.path.join(DOCS_DIR, "screenshots")
DIAGRAMS_DIR = os.path.join(DOCS_DIR, "diagrams")
BACKEND_DIR = os.path.join(WORKSPACE_DIR, "noetrix", "backend")

def img_to_base64(path):
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    ext = os.path.splitext(path)[1].lower().replace(".", "")
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64,{b64}"

def get_code_snippet(rel_path, max_lines=85):
    clean_rel = rel_path.replace("\\", "/")
    if clean_rel.startswith("noetrix/backend/"):
        clean_rel = clean_rel[len("noetrix/backend/"):]
    elif clean_rel.startswith("backend/"):
        clean_rel = clean_rel[len("backend/"):]
    full_path = os.path.join(BACKEND_DIR, clean_rel)
    if not os.path.exists(full_path):
        ws_path = os.path.join(WORKSPACE_DIR, rel_path)
        if os.path.exists(ws_path):
            full_path = ws_path
        else:
            return f"# File not found: {rel_path}"
    with open(full_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return "".join(lines[:max_lines])

def get_image_file_path(fname):
    diag_path = os.path.join(DIAGRAMS_DIR, fname)
    if os.path.exists(diag_path):
        return diag_path
    scr_path = os.path.join(SCREENSHOTS_DIR, fname)
    if os.path.exists(scr_path):
        return scr_path
    return ""

print("Preparing report assets, diagrams, and code snippets...")
brainware_b64 = img_to_base64(os.path.join(ASSETS_DIR, "brainware_logo.png"))
ardent_b64 = img_to_base64(os.path.join(ASSETS_DIR, "ardent_logo.png"))

ALL_CHAPTERS = [
    CHAPTER_1_CONTENT, CHAPTER_2_CONTENT, CHAPTER_3_CONTENT,
    CHAPTER_4_CONTENT, CHAPTER_5_CONTENT, CHAPTER_6_CONTENT,
    CHAPTER_7_CONTENT, CHAPTER_8_CONTENT, CHAPTER_9_CONTENT, CHAPTER_10_CONTENT
]

all_figures = []
all_tables = []
for ch in ALL_CHAPTERS:
    for sec in ch.get("sections", []):
        for fig in sec.get("figures", []):
            all_figures.append(fig)
        if "table" in sec:
            all_tables.append(sec["table"])

img_b64_map = {}
for fig in all_figures:
    fname = fig["filename"]
    fpath = get_image_file_path(fname)
    if fpath:
        img_b64_map[fname] = img_to_base64(fpath)

print(f"Loaded {len(img_b64_map)} of {len(all_figures)} figures (diagrams & screenshots) in base64.")
print(f"Discovered {len(all_tables)} structured data tables.")

TOC_ITEMS = [
    ("Front Matter (Certificate, Declaration, Acknowledgements, Abstract)", "i – vi"),
    ("List of Figures", "vii"),
    ("List of Tables", "viii"),
    ("Chapter 1: Introduction", "1"),
    ("  1.1 Background and Problem Landscape", "1"),
    ("  1.2 Evolution of Resume Screening Technologies", "3"),
    ("  1.3 The Black-Box Dilemma and Problem Statement", "5"),
    ("  1.4 Research and Engineering Objectives", "7"),
    ("  1.5 Industrial and Academic Significance", "8"),
    ("  1.6 Scope and Delimitations of the System", "9"),
    ("  1.7 Organization of the Report", "10"),
    ("Chapter 2: Literature Review", "11"),
    ("  2.1 Historical Foundations of Algorithmic Candidate Screening", "11"),
    ("  2.2 Contemporary Neural Natural Language Processing in Recruitment", "12"),
    ("  2.3 In-Depth Analysis of Foundational Research Papers", "14"),
    ("  2.4 Comparative Analysis of State-of-the-Art Approaches", "17"),
    ("  2.5 Research Gap Identification and Justification of Hybrid Paradigm", "19"),
    ("Chapter 3: System Analysis", "21"),
    ("  3.1 Analysis of Contemporary Commercial ATS Platforms", "21"),
    ("  3.2 Deep Architectural Limitations of Existing Systems", "22"),
    ("  3.3 Proposed System Architecture: The Noetrix Solution", "24"),
    ("  3.4 Multidimensional Feasibility Study", "26"),
    ("Chapter 4: System Design", "29"),
    ("  4.1 High-Level Architectural Overview", "29"),
    ("  4.2 C4 Architectural Model", "31"),
    ("  4.3 Data Flow Modeling (DFD Levels 0, 1, and 2)", "33"),
    ("  4.4 System Behavioral Modeling and Flowcharts", "35"),
    ("  4.5 Subsystem Decomposition and Module Architecture", "37"),
    ("  4.6 Ephemeral Stateless Session Architecture", "39"),
    ("Chapter 5: Methodology and Mathematical Modeling", "41"),
    ("  5.1 End-to-End Hybrid Processing Pipeline", "41"),
    ("  5.2 Mathematical Formulation of the Six Scoring Dimensions", "42"),
    ("  5.3 Composite Scoring and the 50% Soft Knockout Ceiling", "48"),
    ("  5.4 Multi-Tier Deterministic Tie-Breaking Algorithm", "50"),
    ("  5.5 Guardrailed Generative AI and Zero-Fabrication Validator", "52"),
    ("Chapter 6: Implementation and Visual Showcase", "55"),
    ("  6.1 Hardware and Software Environment Specifications", "55"),
    ("  6.2 Exhaustive Technology Stack Breakdown", "56"),
    ("  6.3 Core Code Architecture and Module Walkthrough", "58"),
    ("  6.4 Visual Implementation Showcase (Figures 6.1 – 6.15)", "60"),
    ("Chapter 7: Results and Discussion", "72"),
    ("  7.1 Experimental Evaluation Methodology and Benchmark Corpus", "72"),
    ("  7.2 Deterministic Consistency and Reproducibility Verification", "73"),
    ("  7.3 Latency and Computational Throughput Telemetry", "74"),
    ("  7.4 Comparative Accuracy and Anti-Gaming Robustness", "75"),
    ("  7.5 Comprehensive Verification and Test Execution Matrix", "76"),
    ("  7.6 Critical Analysis and Discussion of Findings", "78"),
    ("Chapter 8: Advantages and Limitations", "80"),
    ("  8.1 Key Advantages of the Noetrix System", "80"),
    ("  8.2 System Limitations and Boundary Conditions", "82"),
    ("  8.3 Security, Privacy, and Ethical AI Alignment", "83"),
    ("Chapter 9: Conclusion", "85"),
    ("  9.1 Synthesis of Completed Work", "85"),
    ("  9.2 Fulfillment of Capstone Objectives", "86"),
    ("  9.3 Practical Impact and Concluding Remarks", "87"),
    ("Chapter 10: Future Scope and Roadmap", "88"),
    ("  10.1 Multi-Lingual and Cross-Cultural Natural Language Processing", "88"),
    ("  10.2 Audio and Video Interview Screening Integration", "89"),
    ("  10.3 Enterprise RBAC and HRIS Integration Ecosystem", "90"),
    ("  10.4 Continuous Autonomous Bias Auditing and Calibration", "91"),
    ("References", "92"),
    ("Appendix A: Core Scoring Engine Source Code (engine.py)", "94"),
    ("Appendix B: Zero-Fabrication Validator Source Code (improver.py)", "97"),
    ("Appendix C: Central Pydantic Data Contracts (scoring.py)", "100"),
    ("Appendix D: Automated Test Suite Telemetry Logs", "102"),
    ("Appendix E: Declarative Mermaid Architecture Specifications", "104")
]

def detect_all_page_numbers(doc):
    fig_map = {}
    tbl_map = {}
    
    # 1. Detect Figures
    for fig in all_figures:
        fid = fig['id']
        for p in range(10, len(doc)):
            txt = doc[p].get_text()
            if fid + ':' in txt or fid + ' :' in txt or fid.upper() + ':' in txt:
                fig_map[fid] = str(p + 1)
                break
                
    # 2. Detect Tables
    for tbl in all_tables:
        tid = tbl['id']
        for p in range(10, len(doc)):
            txt = doc[p].get_text()
            if tid + ':' in txt or tid + ' :' in txt or tid.upper() + ':' in txt:
                tbl_map[tid] = str(p + 1)
                break

    # 3. Detect TOC Items
    toc_results = []
    toc_results.append(('Front Matter (Certificate, Declaration, Acknowledgements, Abstract)', 'i – vi'))
    toc_results.append(('List of Figures', 'vii'))
    toc_results.append(('List of Tables', 'viii'))
    
    curr_ch_p = 10
    for ch in ALL_CHAPTERS:
        ch_title = re.sub(r'\s+', ' ', ch['title']).upper()
        ch_found = None
        for p in range(curr_ch_p, len(doc)):
            norm = re.sub(r'\s+', ' ', doc[p].get_text()).upper()
            if ch_title in norm:
                ch_found = p + 1
                curr_ch_p = p
                break
        
        parts = ch['title'].split(':', 1)
        if len(parts) == 2:
            ch_name = f"{parts[0].title()}: {parts[1].strip().title()}"
        else:
            ch_name = ch['title'].title()
        toc_results.append((ch_name, str(ch_found or curr_ch_p + 1)))
        
        for sec in ch['sections']:
            sec_h = re.sub(r'\s+', ' ', sec['heading']).strip()
            sec_found = None
            search_start = max(10, (ch_found or 11) - 1)
            search_end = min(len(doc), search_start + 12)
            for p in range(search_start, search_end):
                norm = re.sub(r'\s+', ' ', doc[p].get_text())
                if sec_h in norm:
                    sec_found = p + 1
                    break
            toc_results.append(('  ' + sec['heading'], str(sec_found or ch_found or 11)))
            
    ref_found = None
    for p in range(50, len(doc)):
        norm = re.sub(r'\s+', ' ', doc[p].get_text()).upper()
        if 'REFERENCES' in norm:
            ref_found = p + 1
            break
    toc_results.append(('References', str(ref_found or 55)))
    
    for app_key, app_data in APPENDICES_CONTENT.items():
        title = app_data['title']
        prefix = title.split(':')[0].strip().upper()
        app_found = None
        for p in range(54, len(doc)):
            norm = re.sub(r'\s+', ' ', doc[p].get_text()).upper()
            if prefix in norm:
                app_found = p + 1
                break
        
        parts = title.split(':', 1)
        if len(parts) == 2:
            toc_title = f"{parts[0].title()}: {parts[1].strip().title()}"
        else:
            toc_title = title.title()
        toc_title = (toc_title
                     .replace("(Engine.Py)", "(engine.py)")
                     .replace("(Improver.Py)", "(improver.py)")
                     .replace("(Scoring.Py & Resume.Py)", "(scoring.py & resume.py)"))
        toc_results.append((toc_title, str(app_found or 57)))
        
    return toc_results, fig_map, tbl_map

def build_html_report(toc_items=None, fig_map=None, tbl_map=None):
    print("Building standalone publication-grade HTML report...")
    
    html = []
    html.append("""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Noetrix - Project Report</title>
<script>
window.MathJax = {
  tex: {
    inlineMath: [['$', '$'], ['\\\\(', '\\\\)']],
    displayMath: [['$$', '$$'], ['\\\\[', '\\\\]']],
    processEscapes: true
  },
  options: {
    enableMenu: false
  }
};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>
@page {
  size: A4 portrait;
  margin: 1in;
  @bottom-center {
    content: "Page " counter(page);
    font-family: 'Times New Roman', serif;
    font-size: 11pt;
    color: #333333;
  }
}

body {
  font-family: 'Times New Roman', Times, serif;
  font-size: 12pt;
  line-height: 1.5;
  color: #111111;
  text-align: justify;
  margin: 0;
  padding: 0;
  background-color: #ffffff;
}

.page-break {
  page-break-before: always;
  break-before: page;
}

.title-page {
  text-align: center;
  padding-top: 0px;
  line-height: 1.25;
  page-break-after: always;
  break-after: page;
}

.logo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 0 10px;
}

.logo-header img.univ-logo {
  height: 75px;
  width: auto;
}

.logo-header img.ardent-logo {
  height: 46px;
  width: auto;
}

.univ-name {
  font-size: 16pt;
  font-weight: bold;
  letter-spacing: 0.5px;
  color: #0d233a;
  margin-top: 2px;
}

.dept-name {
  font-size: 11pt;
  font-weight: bold;
  color: #333333;
  margin-bottom: 8px;
}

.report-title {
  font-size: 13.5pt;
  font-weight: bold;
  text-transform: uppercase;
  color: #0b1c2d;
  margin: 8px 0 3px 0;
  line-height: 1.25;
}

.report-subtitle {
  font-size: 10.5pt;
  font-weight: bold;
  font-style: italic;
  margin-bottom: 6px;
}

.degree-block {
  font-size: 9.5pt;
  margin: 6px 0 10px 0;
  line-height: 1.2;
}

.team-table {
  width: 100%;
  border-collapse: collapse;
  margin: 6px auto;
  font-size: 8.5pt;
  text-align: left;
}

.team-table th {
  background-color: #f1f5f9;
  border: 1px solid #94a3b8;
  padding: 3px 6px;
  font-weight: bold;
}

.team-table td {
  border: 1px solid #cbd5e1;
  padding: 3px 6px;
}

.links-box {
  background-color: #f8fafc;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  padding: 5px 10px;
  margin: 8px auto;
  font-size: 8.5pt;
  text-align: left;
  width: 95%;
  line-height: 1.35;
}

.links-box strong {
  color: #0d233a;
}

.guide-block {
  margin-top: 8px;
  font-size: 9.5pt;
  line-height: 1.25;
}

.session-block {
  margin-top: 10px;
  font-size: 9.5pt;
  font-weight: bold;
}

/* Chapter Headings */
h1.chapter-title {
  font-size: 15pt;
  font-weight: bold;
  text-align: center;
  text-transform: uppercase;
  margin-top: 14px;
  margin-bottom: 12px;
  color: #0b1c2d;
  border-bottom: 2px solid #0b1c2d;
  padding-bottom: 6px;
  page-break-after: avoid;
  break-after: avoid;
}

h2.section-heading {
  font-size: 13pt;
  font-weight: bold;
  margin-top: 16px;
  margin-bottom: 8px;
  color: #1e293b;
}

h3.sub-heading {
  font-size: 11.5pt;
  font-weight: bold;
  margin-top: 12px;
  margin-bottom: 4px;
  color: #334155;
}

p {
  margin-top: 0;
  margin-bottom: 8px;
  text-indent: 0;
}

/* Tables */
table.report-table {
  width: 100%;
  border-collapse: collapse;
  margin: 12px 0;
  font-size: 9.5pt;
}

table.report-table th {
  background-color: #f1f5f9;
  border: 1px solid #475569;
  padding: 6px 8px;
  font-weight: bold;
  text-align: left;
}

table.report-table td {
  border: 1px solid #64748b;
  padding: 5px 8px;
  vertical-align: top;
}

.table-caption {
  font-weight: bold;
  margin-bottom: 4px;
  font-size: 10.5pt;
  color: #0f172a;
}

/* Figures - Minimized spacing between screenshots and text */
.figure-container {
  margin: 8px auto 12px auto;
  text-align: center;
  page-break-inside: avoid;
  break-inside: avoid;
}

.figure-container img {
  max-width: 80%;
  max-height: 330px;
  width: auto;
  height: auto;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
}

/* Technical Mermaid & Data Flow Architecture Diagrams - Enlarged by 50% */
.figure-container.diagram-figure {
  margin: 12px auto 14px auto;
}

.figure-container.diagram-figure img {
  max-width: 98% !important;
  max-height: 495px !important; /* 50% larger than 330px (330 * 1.5 = 495px) */
  width: auto;
  height: auto;
  border: 1.5px solid #94a3b8;
  border-radius: 6px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.figure-caption {
  margin-top: 3px;
  margin-bottom: 6px;
  font-size: 9.5pt;
  font-style: italic;
  text-align: center;
  line-height: 1.25;
  color: #1e293b;
}

.figure-caption strong {
  font-style: normal;
  color: #0b1c2d;
}

/* Code Blocks */
pre.code-block {
  background-color: #f8fafc;
  border: 1px solid #cbd5e1;
  border-left: 4px solid #0284c7;
  padding: 8px 10px;
  font-family: 'Consolas', 'Courier New', monospace;
  font-size: 8.5pt;
  line-height: 1.28;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
  page-break-inside: auto;
  break-inside: auto;
  margin-top: 6px;
}

p.appendix-desc {
  font-style: italic;
  font-size: 9.5pt;
  color: #1e406b;
  margin-top: 2px;
  margin-bottom: 6px;
  page-break-after: avoid;
  break-after: avoid;
}

.callout-box {
  background-color: #f0fdf4;
  border-left: 4px solid #16a34a;
  padding: 12px 16px;
  margin: 15px 0;
  font-size: 11pt;
}

.signature-grid {
  display: flex;
  justify-content: space-between;
  margin-top: 70px;
  font-size: 11pt;
  text-align: center;
}

.signature-line {
  border-top: 1px solid #333;
  width: 180px;
  padding-top: 5px;
}

.toc-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 11pt;
}

.toc-leader {
  flex-grow: 1;
  border-bottom: 1px dotted #888;
  margin: 0 6px;
  height: 14px;
}
</style>
</head>
<body>
""")

    # 1. Title Page
    html.append(f"""
<div class="title-page">
  <div class="logo-header">
    <img src="{brainware_b64}" class="univ-logo" alt="Brainware University Logo">
    <img src="{ardent_b64}" class="ardent-logo" alt="Ardent Computech Logo">
  </div>
  <div class="univ-name">{PROJECT_METADATA["university"]}</div>
  <div class="dept-name">{PROJECT_METADATA["department"]}</div>
  <hr style="border: 0; border-top: 1.5px solid #0d233a; margin: 15px 0 20px 0;">
  
  <div class="report-title">{PROJECT_METADATA["title"]}</div>
  <div class="report-subtitle">A CAPSTONE ENGINEERING PROJECT REPORT</div>
  
  <div class="degree-block">
    In partial fulfillment of the requirements for the award of the degree of<br>
    <strong>{PROJECT_METADATA["degree"]}</strong>
  </div>
  
  <p style="font-weight: bold; margin-bottom: 5px;">Submitted by:</p>
  <table class="team-table">
    <thead>
      <tr>
        <th>Candidate Name</th>
        <th>Roll No.</th>
        <th>Student Code</th>
        <th>Project Role</th>
      </tr>
    </thead>
    <tbody>
""")
    for tm in TEAM_MEMBERS:
        html.append(f"""
      <tr>
        <td><strong>{tm["name"]}</strong></td>
        <td>{tm["roll_no"]}</td>
        <td>{tm["student_code"]}</td>
        <td>{tm["role"]}</td>
      </tr>
""")
    html.append(f"""
    </tbody>
  </table>
  
  <div class="links-box">
    <strong>Project Repository (GitHub):</strong> <a href="{PROJECT_METADATA["github_link"]}">{PROJECT_METADATA["github_link"]}</a><br>
    <strong>Live Interactive Deployment:</strong> <a href="{PROJECT_METADATA["live_demo_link"]}">{PROJECT_METADATA["live_demo_link"]}</a><br>
    <strong>FastAPI Interactive Swagger Docs:</strong> <a href="{PROJECT_METADATA["api_docs_link"]}">{PROJECT_METADATA["api_docs_link"]}</a>
  </div>

  <div class="guide-block">
    Under the Guidance of:<br>
    <strong>{PROJECT_METADATA["guide_name"]}</strong><br>
    {PROJECT_METADATA["guide_designation"]}<br>
    In Association with: <strong>{PROJECT_METADATA["industry_partner"]}</strong>
  </div>

  <div class="session-block">
    {PROJECT_METADATA["address"]}<br>
    Academic Session: {PROJECT_METADATA["academic_session"]} ({PROJECT_METADATA["submission_date"]})
  </div>
</div>
""")

    # 2. Certificate
    html.append(f"""
<div class="page-break"></div>
<h1 class="chapter-title">CERTIFICATE OF RECOMMENDATION</h1>
<p style="margin-top: 35px; line-height: 1.8;">{CERTIFICATE_TEXT}</p>

<div class="signature-grid" style="margin-top: 120px;">
  <div>
    <div class="signature-line"><strong>{PROJECT_METADATA["guide_name"]}</strong></div>
    Project Mentor & Engineer<br>Ardent Computech Pvt. Ltd.
  </div>
  <div>
    <div class="signature-line"><strong>{PROJECT_METADATA["hod_name"]}</strong></div>
    Head of Department, CSE (CS & DS)<br>Brainware University
  </div>
  <div>
    <div class="signature-line"><strong>{PROJECT_METADATA["dean_name"]}</strong></div>
    Dean, School of Engineering<br>Brainware University
  </div>
</div>
""")

    # 3. Industry Certificate
    html.append(f"""
<div class="page-break"></div>
<h1 class="chapter-title">INDUSTRIAL PROJECT CERTIFICATE</h1>
<div style="text-align: center; margin: 25px 0;">
  <img src="{ardent_b64}" style="height: 70px;" alt="Ardent Computech">
  <div style="font-weight: bold; font-size: 13pt; margin-top: 5px;">{PROJECT_METADATA["industry_partner"]}</div>
  <div style="font-size: 10.5pt; font-style: italic;">{PROJECT_METADATA["industry_tagline"]}</div>
</div>
<hr style="margin: 20px 0;">
<p style="margin-top: 30px; line-height: 1.8;">{INDUSTRY_CERTIFICATE_TEXT}</p>

<div class="signature-grid" style="margin-top: 120px;">
  <div>
    <div class="signature-line"><strong>Project Engineer</strong></div>
    Ardent Computech Pvt. Ltd.
  </div>
  <div>
    <div class="signature-line"><strong>Technical Director</strong></div>
    Ardent Computech Pvt. Ltd.
  </div>
  <div>
    <div class="signature-line"><strong>External Reviewer</strong></div>
    Evaluation Committee
  </div>
</div>
""")

    # 4. Declaration
    html.append(f"""
<div class="page-break"></div>
<h1 class="chapter-title">DECLARATION OF ORIGINALITY</h1>
<p style="margin-top: 35px; line-height: 1.8;">{DECLARATION_TEXT}</p>

<p style="margin-top: 50px; font-weight: bold;">Candidate Signatures:</p>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 35px; margin-top: 40px; font-size: 11pt;">
  <div>
    <div class="signature-line" style="width: 220px;"><strong>Dhrubojyoti Hazra</strong></div>
    Roll No: 23010333015 | Student Code: BWU/BTD/23/015
  </div>
  <div>
    <div class="signature-line" style="width: 220px;"><strong>Isheeka Mukhopadhyay</strong></div>
    Roll No: 23010333041 | Student Code: BWU/BTD/23/042
  </div>
  <div>
    <div class="signature-line" style="width: 220px;"><strong>Samprikta De</strong></div>
    Roll No: 23010333055 | Student Code: BWU/BTD/23/056
  </div>
  <div>
    <div class="signature-line" style="width: 220px;"><strong>Adhiraj Das</strong></div>
    Roll No: 23010333009 | Student Code: BWU/BTD/23/009
  </div>
  <div>
    <div class="signature-line" style="width: 220px;"><strong>Tiyasha Baidya</strong></div>
    Roll No: 23010333025 | Student Code: BWU/BTD/23/025
  </div>
</div>
""")

    # 5. Acknowledgement
    html.append(f"""
<div class="page-break"></div>
<h1 class="chapter-title">ACKNOWLEDGEMENTS</h1>
<p style="margin-top: 30px; line-height: 1.75;">{ACKNOWLEDGEMENT_TEXT}</p>
""")

    # 6. Abstract
    html.append(f"""
<div class="page-break"></div>
<h1 class="chapter-title">ABSTRACT</h1>
<p style="margin-top: 30px; line-height: 1.75;">{ABSTRACT_TEXT}</p>
""")

    # 7. Table of Contents
    html.append("""
<div class="page-break"></div>
<h1 class="chapter-title">TABLE OF CONTENTS</h1>
<div style="margin-top: 25px; line-height: 1.6;">
""")
    active_toc = toc_items or TOC_ITEMS
    for title, pg in active_toc:
        indent = "padding-left: 20px;" if title.startswith("  ") else "font-weight: bold; margin-top: 6px;"
        clean_title = title.strip()
        html.append(f"""
  <div class="toc-item" style="{indent}">
    <span>{clean_title}</span>
    <span class="toc-leader"></span>
    <span>{pg}</span>
  </div>
""")
    html.append("</div>")

    # 8. List of Figures
    html.append("""
<div class="page-break"></div>
<h1 class="chapter-title">LIST OF FIGURES</h1>
<div style="margin-top: 25px; line-height: 1.6;">
""")
    for fig in all_figures:
        pg_num = fig_map.get(fig["id"], "Figure") if fig_map else "Figure"
        html.append(f"""
  <div class="toc-item">
    <span><strong>{fig["id"]}:</strong> {fig["title"]}</span>
    <span class="toc-leader"></span>
    <span>{pg_num}</span>
  </div>
""")
    html.append("</div>")

    # 9. List of Tables
    html.append("""
<div class="page-break"></div>
<h1 class="chapter-title">LIST OF TABLES</h1>
<div style="margin-top: 25px; line-height: 1.6;">
""")
    for t in all_tables:
        pg_num = tbl_map.get(t["id"], "Table") if tbl_map else "Table"
        html.append(f"""
  <div class="toc-item">
    <span><strong>{t["id"]}:</strong> {t["caption"]}</span>
    <span class="toc-leader"></span>
    <span>{pg_num}</span>
  </div>
""")
    html.append("</div>")

    # Function to render chapter sections
    def render_chapter(ch_data):
        html.append(f"""
<div class="page-break"></div>
<h1 class="chapter-title">{ch_data["title"]}</h1>
""")
        for sec in ch_data["sections"]:
            if sec.get("page_break_before"):
                html.append('<div class="page-break"></div>\n')
            html.append(f"""
<h2 class="section-heading">{sec["heading"]}</h2>
""")
            for p in sec["paragraphs"]:
                html.append(f"<p>{p}</p>\n")
            
            if "table" in sec:
                t = sec["table"]
                html.append(f"""
<div class="table-caption">{t["id"]}: {t["caption"]}</div>
<table class="report-table">
  <thead>
    <tr>
""")
                for h in t["headers"]:
                    html.append(f"      <th>{h}</th>\n")
                html.append("""    </tr>
  </thead>
  <tbody>
""")
                for row in t["rows"]:
                    html.append("    <tr>\n")
                    for cell in row:
                        html.append(f"      <td>{cell}</td>\n")
                    html.append("    </tr>\n")
                html.append("""  </tbody>
</table>
""")

            if "figures" in sec:
                for fig in sec["figures"]:
                    fname = fig["filename"]
                    b64_src = img_b64_map.get(fname, "")
                    if b64_src:
                        is_diag = fname.startswith("fig_")
                        diag_cls = " diagram-figure" if is_diag else ""
                        html.append(f"""
<div class="figure-container{diag_cls}">
  <img src="{b64_src}" alt="{fig["title"]}">
  <div class="figure-caption">
    <strong>{fig["id"]}:</strong> {fig["title"]} — {fig["description"]}
  </div>
</div>
""")

    # Render Chapters 1 to 10
    render_chapter(CHAPTER_1_CONTENT)
    render_chapter(CHAPTER_2_CONTENT)
    render_chapter(CHAPTER_3_CONTENT)
    render_chapter(CHAPTER_4_CONTENT)
    render_chapter(CHAPTER_5_CONTENT)
    render_chapter(CHAPTER_6_CONTENT)
    render_chapter(CHAPTER_7_CONTENT)
    render_chapter(CHAPTER_8_CONTENT)
    render_chapter(CHAPTER_9_CONTENT)
    render_chapter(CHAPTER_10_CONTENT)

    # References
    html.append("""
<div class="page-break"></div>
<h1 class="chapter-title">REFERENCES</h1>
<div style="margin-top: 14px; line-height: 1.30; font-size: 9.0pt;">
""")
    for ref in REFERENCES_LIST:
        html.append(f"""
  <p style="padding-left: 28px; text-indent: -28px; margin-bottom: 5px;">
    <strong>{ref["id"]}</strong> {ref["citation"]}
  </p>
""")
    html.append("</div>")

    # Appendices
    app = APPENDICES_CONTENT
    # Appendix A
    html.append(f"""
<div class="page-break"></div>
<h1 class="chapter-title">{app["appendix_a"]["title"]}</h1>
<p class="appendix-desc">{app["appendix_a"]["description"]}</p>
<pre class="code-block">{get_code_snippet(app["appendix_a"]["file_path"], 52)}</pre>
""")

    # Appendix B
    html.append(f"""
<div class="page-break"></div>
<h1 class="chapter-title">{app["appendix_b"]["title"]}</h1>
<p class="appendix-desc">{app["appendix_b"]["description"]}</p>
<pre class="code-block">{get_code_snippet(app["appendix_b"]["file_path"], 52)}</pre>
""")

    # Appendix C
    html.append(f"""
<div class="page-break"></div>
<h1 class="chapter-title">{app["appendix_c"]["title"]}</h1>
<p class="appendix-desc">{app["appendix_c"]["description"]}</p>
<pre class="code-block">{get_code_snippet(app["appendix_c"]["file_path"], 50)}</pre>
""")

    # Appendix D
    html.append(f"""
<div class="page-break"></div>
<h1 class="chapter-title">{app["appendix_d"]["title"]}</h1>
<p class="appendix-desc">{app["appendix_d"]["description"]}</p>
<pre class="code-block">{app["appendix_d"]["log_summary"]}</pre>
""")

    # Appendix E - Part 1
    html.append(f"""
<div class="page-break"></div>
<h1 class="chapter-title">{app["appendix_e"]["title"]} (PART 1)</h1>
<p class="appendix-desc">{app["appendix_e"]["description_part_1"]}</p>
<pre class="code-block">{app["appendix_e"]["mermaid_sources_part_1"]}</pre>
""")

    # Appendix E - Part 2
    html.append(f"""
<div class="page-break"></div>
<h1 class="chapter-title">{app["appendix_e"]["title"]} (PART 2)</h1>
<p class="appendix-desc">{app["appendix_e"]["description_part_2"]}</p>
<pre class="code-block">{app["appendix_e"]["mermaid_sources_part_2"]}</pre>
""")

    html.append("""
</body>
</html>
""")

    html_content = "".join(html)
    out_html_path = os.path.join(DOCS_DIR, "Noetrix_Project_Master_Report.html")
    with open(out_html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML report saved successfully ({len(html_content)} characters) at: {out_html_path}")
    return out_html_path

def build_docx_report(toc_items=None, fig_map=None, tbl_map=None):
    print("Building beautified institutional Word Document (.docx)...")
    import re
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    doc = docx.Document()

    # ── Colour palette ────────────────────────────────────────────────────────
    NAVY        = RGBColor(0x0b, 0x1c, 0x2d)   # Chapter title background / accents
    DARK_BLUE   = RGBColor(0x1e, 0x40, 0x6b)   # Section headings
    MID_BLUE    = RGBColor(0x1e, 0x52, 0x88)   # Sub-headings
    SLATE       = RGBColor(0x33, 0x41, 0x55)   # Body text
    LIGHT_BLUE  = RGBColor(0xdb, 0xe9, 0xf8)   # Alternate table row shading
    HEADER_BG   = RGBColor(0x0b, 0x1c, 0x2d)   # Table header bg
    WHITE       = RGBColor(0xff, 0xff, 0xff)
    GOLD        = RGBColor(0xc8, 0x9b, 0x2a)   # Accent line under chapter title

    def clean_xml_text(s):
        if not isinstance(s, str):
            return s
        return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x84\x86-\x9f]', '', s)

    # ── Page / section setup ─────────────────────────────────────────────────
    for sec in doc.sections:
        sec.top_margin    = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin   = Inches(1.25)
        sec.right_margin  = Inches(1.0)

        # Header — running title
        header = sec.header
        hdr_p = header.paragraphs[0]
        hdr_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hdr_p.paragraph_format.space_after = Pt(0)
        hdr_run = hdr_p.add_run("Noetrix: Explainable Resume Screening & Tailoring System")
        hdr_run.font.name = "Times New Roman"
        hdr_run.font.size = Pt(8.5)
        hdr_run.font.color.rgb = RGBColor(0x64, 0x74, 0x8b)
        hdr_run.font.italic = True

        # Footer — "Page X of Y"
        footer = sec.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fp.paragraph_format.space_before = Pt(0)
        for txt, is_field in [("Page ", False), ("PAGE", True), (" of ", False), ("NUMPAGES", True)]:
            if is_field:
                fld = OxmlElement('w:fldChar')
                fld.set(qn('w:fldCharType'), 'begin')
                r = OxmlElement('w:r')
                r.append(fld)
                fp._p.append(r)
                instr = OxmlElement('w:instrText')
                instr.set(qn('xml:space'), 'preserve')
                instr.text = f" {txt} "
                r2 = OxmlElement('w:r')
                r2.append(instr)
                fp._p.append(r2)
                fld2 = OxmlElement('w:fldChar')
                fld2.set(qn('w:fldCharType'), 'end')
                r3 = OxmlElement('w:r')
                r3.append(fld2)
                fp._p.append(r3)
            else:
                fr = fp.add_run(txt)
                fr.font.name = "Times New Roman"
                fr.font.size = Pt(9.5)
                fr.font.color.rgb = RGBColor(0x33, 0x41, 0x55)

    # ── Default style ────────────────────────────────────────────────────────
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    style.font.color.rgb = SLATE
    style.paragraph_format.line_spacing = 1.5
    style.paragraph_format.space_after = Pt(6)

    # ── Helper: color to hex string ───────────────────────────────────────────
    def to_hex(c) -> str:
        if isinstance(c, str):
            return c.lstrip('#')
        return f"{c[0]:02X}{c[1]:02X}{c[2]:02X}"

    # ── Helper: set paragraph shading ────────────────────────────────────────
    def set_para_shading(para, fill_rgb):
        fill_hex = to_hex(fill_rgb)
        pPr = para._p.get_or_add_pPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), fill_hex)
        pPr.append(shd)

    # ── Helper: set cell shading ─────────────────────────────────────────────
    def shade_cell(cell, fill_rgb):
        fill_hex = to_hex(fill_rgb)
        tc = cell._tc
        tcPr = tc.get_or_add_tcPr()
        shd = OxmlElement('w:shd')
        shd.set(qn('w:val'), 'clear')
        shd.set(qn('w:color'), 'auto')
        shd.set(qn('w:fill'), fill_hex)
        tcPr.append(shd)

    # ── Helper: add bottom border to paragraph ────────────────────────────────
    def add_para_bottom_border(para, color_hex="C8A02A", size=6):
        pPr = para._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), str(size))
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), color_hex)
        pBdr.append(bottom)
        pPr.append(pBdr)

    # ── add_p: standard body paragraph ───────────────────────────────────────
    def add_p(text, bold=False, italic=False, size=12,
              align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6, color=None):
        text = clean_xml_text(text)
        p = doc.add_paragraph()
        p.alignment = align
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.space_before = Pt(0)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(size)
        run.bold = bold
        run.italic = italic
        if color:
            run.font.color.rgb = color
        return p

    # ── Chapter title: navy banner with gold underline ────────────────────────
    def add_chapter_title(title):
        title = clean_xml_text(title)
        doc.add_page_break()
        # Spacer
        sp = doc.add_paragraph()
        sp.paragraph_format.space_before = Pt(0)
        sp.paragraph_format.space_after = Pt(4)

        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(6)
        p.paragraph_format.space_after = Pt(2)
        set_para_shading(p, NAVY)
        add_para_bottom_border(p, "C8A02A", size=8)
        run = p.add_run(f"  {title}  ")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(15)
        run.bold = True
        run.font.color.rgb = WHITE
        # Spacer after
        sp2 = doc.add_paragraph()
        sp2.paragraph_format.space_before = Pt(0)
        sp2.paragraph_format.space_after = Pt(8)

    # ── Section heading: dark blue with left accent bar ───────────────────────
    def add_heading2(text):
        text = clean_xml_text(text)
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after  = Pt(5)
        # Left border accent
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        left = OxmlElement('w:left')
        left.set(qn('w:val'), 'single')
        left.set(qn('w:sz'), '18')
        left.set(qn('w:space'), '4')
        left.set(qn('w:color'), '1E406B')
        pBdr.append(left)
        pPr.append(pBdr)
        run = p.add_run(f"  {text}")
        run.font.name = 'Times New Roman'
        run.font.size = Pt(13.5)
        run.bold = True
        run.font.color.rgb = DARK_BLUE

    # ── Sub-section heading ───────────────────────────────────────────────────
    def add_heading3(text):
        text = clean_xml_text(text)
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after  = Pt(3)
        run = p.add_run(text)
        run.font.name = 'Times New Roman'
        run.font.size = Pt(12)
        run.bold = True
        run.font.color.rgb = MID_BLUE

    # ── Decorative horizontal divider ────────────────────────────────────────
    def add_divider():
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after  = Pt(2)
        pPr = p._p.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '4')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), 'CBD5E1')
        pBdr.append(bottom)
        pPr.append(pBdr)

    # ── Styled data table ────────────────────────────────────────────────────
    def add_styled_table(headers, rows, caption_text=""):
        if caption_text:
            add_p(caption_text, bold=True, size=10.5, color=NAVY, space_after=3)
        t_obj = doc.add_table(rows=1, cols=len(headers))
        t_obj.alignment = WD_TABLE_ALIGNMENT.CENTER
        t_obj.style = 'Table Grid'
        # Header row
        h_cells = t_obj.rows[0].cells
        for idx, h_text in enumerate(headers):
            shade_cell(h_cells[idx], HEADER_BG)
            h_cells[idx].paragraphs[0].clear()
            hr = h_cells[idx].paragraphs[0].add_run(clean_xml_text(h_text))
            hr.font.bold = True
            hr.font.name = "Times New Roman"
            hr.font.size = Pt(9.5)
            hr.font.color.rgb = WHITE
            h_cells[idx].paragraphs[0].paragraph_format.space_after = Pt(1)
            h_cells[idx].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        # Data rows
        for r_idx, row_data in enumerate(rows):
            r_cells = t_obj.add_row().cells
            for idx, cell_text in enumerate(row_data):
                if r_idx % 2 == 1:
                    shade_cell(r_cells[idx], LIGHT_BLUE)
                r_cells[idx].paragraphs[0].clear()
                cr = r_cells[idx].paragraphs[0].add_run(clean_xml_text(cell_text))
                cr.font.name = "Times New Roman"
                cr.font.size = Pt(9.0)
                r_cells[idx].paragraphs[0].paragraph_format.space_after = Pt(1)
                r_cells[idx].paragraphs[0].paragraph_format.line_spacing = 1.15
        # Space after table
        sp = doc.add_paragraph()
        sp.paragraph_format.space_after = Pt(8)

    # ════════════════════════════════════════════════════════════════════════
    # 1. TITLE PAGE
    # ════════════════════════════════════════════════════════════════════════
    # Top navy banner
    banner = doc.add_paragraph()
    banner.alignment = WD_ALIGN_PARAGRAPH.CENTER
    banner.paragraph_format.space_before = Pt(0)
    banner.paragraph_format.space_after = Pt(6)
    set_para_shading(banner, NAVY)
    br = banner.add_run("  BRAINWARE UNIVERSITY  ")
    br.font.name = "Times New Roman"
    br.font.size = Pt(18)
    br.font.bold = True
    br.font.color.rgb = WHITE

    # Logo row
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_after = Pt(4)
    if os.path.exists(os.path.join(ASSETS_DIR, "brainware_logo.png")):
        p_logo.add_run().add_picture(os.path.join(ASSETS_DIR, "brainware_logo.png"), width=Inches(1.2))
        p_logo.add_run("          ")
    if os.path.exists(os.path.join(ASSETS_DIR, "ardent_logo.png")):
        p_logo.add_run().add_picture(os.path.join(ASSETS_DIR, "ardent_logo.png"), width=Inches(2.2))

    add_p(PROJECT_METADATA["university"], bold=True, size=15, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=1, color=NAVY)
    add_p(PROJECT_METADATA["department"], bold=True, size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)

    add_divider()

    # Project title in gold-bordered box
    title_p = doc.add_paragraph()
    title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_p.paragraph_format.space_before = Pt(10)
    title_p.paragraph_format.space_after = Pt(4)
    add_para_bottom_border(title_p, "C8A02A", size=6)
    pPr = title_p._p.get_or_add_pPr()
    pBdr = title_p._p.pPr.find(qn('w:pBdr'))
    if pBdr is None:
        pBdr = OxmlElement('w:pBdr')
        pPr.append(pBdr)
    for side in ['top', 'left', 'right']:
        el = OxmlElement(f'w:{side}')
        el.set(qn('w:val'), 'single')
        el.set(qn('w:sz'), '6')
        el.set(qn('w:space'), '4')
        el.set(qn('w:color'), 'C8A02A')
        pBdr.append(el)
    tr = title_p.add_run(PROJECT_METADATA["title"])
    tr.font.name = "Times New Roman"
    tr.font.size = Pt(13)
    tr.font.bold = True
    tr.font.color.rgb = NAVY

    add_p("A CAPSTONE ENGINEERING PROJECT REPORT", italic=True, bold=True, size=10,
          align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    add_p(f"In partial fulfillment of the requirements for the award of the degree of\n{PROJECT_METADATA['degree']}",
          size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=10)

    add_divider()

    add_p("Submitted by:", bold=True, size=10.5, align=WD_ALIGN_PARAGRAPH.CENTER,
          space_after=3, color=DARK_BLUE)

    # Team table
    add_styled_table(
        headers=["Candidate Name", "Roll No.", "Student Code", "Project Role"],
        rows=[[tm["name"], tm["roll_no"], tm["student_code"], tm["role"]] for tm in TEAM_MEMBERS]
    )

    # Links box
    links_p = doc.add_paragraph()
    links_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    links_p.paragraph_format.space_before = Pt(2)
    links_p.paragraph_format.space_after = Pt(6)
    set_para_shading(links_p, RGBColor(0xf8, 0xfa, 0xfc))
    lr = links_p.add_run(
        f"GitHub: {PROJECT_METADATA['github_link']}   |   Live Demo: {PROJECT_METADATA['live_demo_link']}"
    )
    lr.font.name = "Times New Roman"
    lr.font.size = Pt(8.5)
    lr.font.color.rgb = DARK_BLUE

    add_divider()
    add_p(
        f"Under the Guidance of: {PROJECT_METADATA['guide_name']}, {PROJECT_METADATA['guide_designation']}\n"
        f"In Association with: {PROJECT_METADATA['industry_partner']}\n"
        f"Academic Session: {PROJECT_METADATA['academic_session']}",
        size=9.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0
    )

    # ════════════════════════════════════════════════════════════════════════
    # 2. CERTIFICATE
    # ════════════════════════════════════════════════════════════════════════
    add_chapter_title("CERTIFICATE OF RECOMMENDATION")
    add_p(CERTIFICATE_TEXT, space_after=30)
    add_divider()
    sig_text = (
        f"\n{PROJECT_METADATA['guide_name']}\n"
        f"Project Engineer & Industry Mentor\nArdent Computech Pvt. Ltd.\n(In Association with Brainware University)\n\n"
        f"Countersigned by:\n\n"
        f"{PROJECT_METADATA['hod_name']}\nHead of the Department, Department of CSE (CS & DS)\nBrainware University\n\n"
        f"{PROJECT_METADATA['dean_name']}\nDean, School of Engineering\nBrainware University"
    )
    add_p(sig_text, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=0)

    # ════════════════════════════════════════════════════════════════════════
    # 3. INDUSTRY CERTIFICATE
    # ════════════════════════════════════════════════════════════════════════
    add_chapter_title("INDUSTRIAL PROJECT CERTIFICATE")
    add_p(f"{PROJECT_METADATA['industry_partner']}\n{PROJECT_METADATA['industry_tagline']}",
          bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=16)
    add_p(INDUSTRY_CERTIFICATE_TEXT, space_after=30)
    add_divider()
    add_p("\n\nProject Engineer & Technical Director\nArdent Computech Pvt. Ltd., Kolkata",
          bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT)

    # ════════════════════════════════════════════════════════════════════════
    # 4. DECLARATION
    # ════════════════════════════════════════════════════════════════════════
    add_chapter_title("DECLARATION OF ORIGINALITY")
    add_p(DECLARATION_TEXT, space_after=20)
    add_divider()
    add_p(
        "Candidate Signatures:\n"
        "1. Dhrubojyoti Hazra (Roll No: 23010333015, Student Code: BWU/BTD/23/015)\n"
        "2. Isheeka Mukhopadhyay (Roll No: 23010333041, Student Code: BWU/BTD/23/042)\n"
        "3. Samprikta De (Roll No: 23010333055, Student Code: BWU/BTD/23/056)\n"
        "4. Adhiraj Das (Roll No: 23010333009, Student Code: BWU/BTD/23/009)\n"
        "5. Tiyasha Baidya (Roll No: 23010333025, Student Code: BWU/BTD/23/025)",
        bold=True, space_after=10
    )

    # ════════════════════════════════════════════════════════════════════════
    # 5. ACKNOWLEDGEMENTS & ABSTRACT
    # ════════════════════════════════════════════════════════════════════════
    add_chapter_title("ACKNOWLEDGEMENTS")
    add_p(ACKNOWLEDGEMENT_TEXT)

    add_chapter_title("ABSTRACT")
    add_p(ABSTRACT_TEXT)

    # ════════════════════════════════════════════════════════════════════════
    # 6. TABLE OF CONTENTS
    # ════════════════════════════════════════════════════════════════════════
    add_chapter_title("TABLE OF CONTENTS")
    for title, pg in (toc_items or TOC_ITEMS):
        clean_title = title.strip()
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.space_after = Pt(2)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(6.25), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        is_sub = title.startswith("  ")
        if is_sub:
            p.paragraph_format.left_indent = Inches(0.3)
            run = p.add_run(clean_title)
            run.font.name = "Times New Roman"
            run.font.size = Pt(10.0)
        else:
            run = p.add_run(clean_title)
            run.font.name = "Times New Roman"
            run.font.size = Pt(11.0)
            run.bold = True
            run.font.color.rgb = DARK_BLUE
        # Dotted leader + page number
        tab_run = p.add_run(f"\t{pg}")
        tab_run.font.name = "Times New Roman"
        tab_run.font.size = Pt(10.0 if is_sub else 11.0)

    # ════════════════════════════════════════════════════════════════════════
    # 7. LIST OF FIGURES & TABLES
    # ════════════════════════════════════════════════════════════════════════
    add_chapter_title("LIST OF FIGURES")
    for fig in all_figures:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(6.25), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        run_id = p.add_run(f"{fig['id']}: ")
        run_id.bold = True
        run_id.font.name = "Times New Roman"
        run_id.font.size = Pt(10.0)
        run_id.font.color.rgb = DARK_BLUE
        run_t = p.add_run(fig["title"])
        run_t.font.name = "Times New Roman"
        run_t.font.size = Pt(10.0)
        pg_num = fig_map.get(fig["id"], "") if fig_map else ""
        tab_run = p.add_run(f"\t{pg_num}")
        tab_run.font.name = "Times New Roman"
        tab_run.font.size = Pt(10.0)

    add_chapter_title("LIST OF TABLES")
    for t in all_tables:
        p = doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.25
        p.paragraph_format.space_after = Pt(3)
        p.paragraph_format.tab_stops.add_tab_stop(Inches(6.25), WD_TAB_ALIGNMENT.RIGHT, WD_TAB_LEADER.DOTS)
        run_id = p.add_run(f"{t['id']}: ")
        run_id.bold = True
        run_id.font.name = "Times New Roman"
        run_id.font.size = Pt(10.0)
        run_id.font.color.rgb = DARK_BLUE
        run_t = p.add_run(t["caption"])
        run_t.font.name = "Times New Roman"
        run_t.font.size = Pt(10.0)
        pg_num = tbl_map.get(t["id"], "") if tbl_map else ""
        tab_run = p.add_run(f"\t{pg_num}")
        tab_run.font.name = "Times New Roman"
        tab_run.font.size = Pt(10.0)

    # ════════════════════════════════════════════════════════════════════════
    # 8. CHAPTERS
    # ════════════════════════════════════════════════════════════════════════
    def write_docx_chapter(ch_data):
        add_chapter_title(ch_data["title"])
        for sec in ch_data["sections"]:
            if sec.get("page_break_before"):
                doc.add_page_break()
            add_heading2(sec["heading"])
            for p_text in sec["paragraphs"]:
                add_p(p_text)

            if "table" in sec:
                t = sec["table"]
                add_styled_table(
                    headers=t["headers"],
                    rows=t["rows"],
                    caption_text=f"{t['id']}: {t['caption']}"
                )

            if "figures" in sec:
                for fig in sec["figures"]:
                    fname = fig["filename"]
                    fpath = get_image_file_path(fname)
                    if fpath and os.path.exists(fpath):
                        diag_w = Inches(6.2) if fname.startswith("fig_") else Inches(5.5)
                        # Figure container
                        p_fig = doc.add_paragraph()
                        p_fig.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        p_fig.paragraph_format.space_before = Pt(10)
                        p_fig.paragraph_format.space_after  = Pt(3)
                        set_para_shading(p_fig, RGBColor(0xf8, 0xfa, 0xfc))
                        p_fig.add_run().add_picture(fpath, width=diag_w)
                        # Caption
                        cap_p = doc.add_paragraph()
                        cap_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        cap_p.paragraph_format.space_before = Pt(2)
                        cap_p.paragraph_format.space_after  = Pt(10)
                        cap_id = cap_p.add_run(f"{fig['id']}: ")
                        cap_id.font.name = "Times New Roman"
                        cap_id.font.size = Pt(10)
                        cap_id.font.bold = True
                        cap_id.font.color.rgb = DARK_BLUE
                        cap_desc = cap_p.add_run(f"{fig['title']} — {fig['description']}")
                        cap_desc.font.name = "Times New Roman"
                        cap_desc.font.size = Pt(10)
                        cap_desc.font.italic = True
                        cap_desc.font.color.rgb = SLATE

    for ch in [CHAPTER_1_CONTENT, CHAPTER_2_CONTENT, CHAPTER_3_CONTENT,
               CHAPTER_4_CONTENT, CHAPTER_5_CONTENT, CHAPTER_6_CONTENT,
               CHAPTER_7_CONTENT, CHAPTER_8_CONTENT, CHAPTER_9_CONTENT,
               CHAPTER_10_CONTENT]:
        write_docx_chapter(ch)

    # ════════════════════════════════════════════════════════════════════════
    # 9. REFERENCES
    # ════════════════════════════════════════════════════════════════════════
    add_chapter_title("REFERENCES")
    for ref in REFERENCES_LIST:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent   = Inches(0.35)
        p.paragraph_format.first_line_indent = Inches(-0.35)
        p.paragraph_format.space_after   = Pt(7)
        p.paragraph_format.line_spacing  = 1.4
        rid = p.add_run(f"{ref['id']} ")
        rid.font.name = "Times New Roman"
        rid.font.size = Pt(10.5)
        rid.font.bold = True
        rid.font.color.rgb = DARK_BLUE
        rcite = p.add_run(ref["citation"])
        rcite.font.name = "Times New Roman"
        rcite.font.size = Pt(10.5)

    # ════════════════════════════════════════════════════════════════════════
    # 10. APPENDICES
    # ════════════════════════════════════════════════════════════════════════
    app = APPENDICES_CONTENT
    for app_key in ["appendix_a", "appendix_b", "appendix_c"]:
        add_chapter_title(app[app_key]["title"])
        add_p(app[app_key]["description"], italic=True, color=DARK_BLUE)
        # Code in Courier/Consolas mono style
        code_p = doc.add_paragraph()
        code_p.paragraph_format.space_before = Pt(4)
        code_p.paragraph_format.space_after  = Pt(4)
        set_para_shading(code_p, RGBColor(0xf1, 0xf5, 0xf9))
        code_run = code_p.add_run(get_code_snippet(app[app_key]["file_path"], 52))
        code_run.font.name = "Courier New"
        code_run.font.size = Pt(8.5)

    add_chapter_title(app["appendix_d"]["title"])
    add_p(app["appendix_d"]["description"], italic=True, color=DARK_BLUE)
    log_p = doc.add_paragraph()
    set_para_shading(log_p, RGBColor(0xf1, 0xf5, 0xf9))
    log_run = log_p.add_run(app["appendix_d"]["log_summary"])
    log_run.font.name = "Courier New"
    log_run.font.size = Pt(8.5)

    add_chapter_title(app["appendix_e"]["title"] + " (PART 1)")
    add_p(app["appendix_e"]["description_part_1"], italic=True, color=DARK_BLUE)
    me_p1 = doc.add_paragraph()
    set_para_shading(me_p1, RGBColor(0xf1, 0xf5, 0xf9))
    me_run1 = me_p1.add_run(app["appendix_e"]["mermaid_sources_part_1"])
    me_run1.font.name = "Courier New"
    me_run1.font.size = Pt(8.0)

    add_chapter_title(app["appendix_e"]["title"] + " (PART 2)")
    add_p(app["appendix_e"]["description_part_2"], italic=True, color=DARK_BLUE)
    me_p2 = doc.add_paragraph()
    set_para_shading(me_p2, RGBColor(0xf1, 0xf5, 0xf9))
    me_run2 = me_p2.add_run(app["appendix_e"]["mermaid_sources_part_2"])
    me_run2.font.name = "Courier New"
    me_run2.font.size = Pt(8.0)

    out_docx_path = os.path.join(DOCS_DIR, "Noetrix_Project_Master_Report.docx")
    try:
        doc.save(out_docx_path)
        print(f"Word document saved successfully at: {out_docx_path}")
    except PermissionError:
        out_docx_path = os.path.join(DOCS_DIR, "Noetrix_Project_Master_Report_v2.docx")
        doc.save(out_docx_path)
        print(f"Word document saved to alternate path (original locked in Word): {out_docx_path}")
    return out_docx_path

async def compile_pdf(html_path):
    out_pdf_path = os.path.join(DOCS_DIR, "Noetrix_Project_Master_Report.pdf")
    print(f"Compiling publication-grade PDF via Playwright Chromium...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        # Load local HTML file
        await page.goto(f"file://{html_path}", wait_until="networkidle")
        try:
            await page.wait_for_selector("mjx-container", timeout=15000)
            await page.wait_for_timeout(3000)
            print("MathJax formulas rendered successfully into typographical equations!")
        except Exception as e:
            print(f"MathJax rendering wait note: {e}")
        
        pdf_kwargs = dict(
            format="A4",
            print_background=True,
            margin={"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"},
            display_header_footer=True,
            header_template='<div style="font-size:8.5pt;font-family:\'Times New Roman\',serif;color:#64748b;width:100%;text-align:right;padding-right:1in;">Noetrix: Explainable Resume Screening & Tailoring System</div>',
            footer_template='<div style="font-size:9.5pt;font-family:\'Times New Roman\',serif;color:#334155;width:100%;text-align:center;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>'
        )
        try:
            await page.pdf(path=out_pdf_path, **pdf_kwargs)
        except Exception:
            out_pdf_path = os.path.join(DOCS_DIR, "Noetrix_Project_Master_Report_v2.pdf")
            await page.pdf(path=out_pdf_path, **pdf_kwargs)
        await browser.close()
    
    print(f"PDF compilation complete at: {out_pdf_path}")
    import pymupdf
    pdf_doc = pymupdf.open(out_pdf_path)
    print(f"=== TOTAL PAGES GENERATED: {len(pdf_doc)} PAGES ===")
    return out_pdf_path, len(pdf_doc)

async def main():
    print("\n" + "="*70)
    print("NOETRIX MASTER PROJECT REPORT COMPILER — TWO-PASS OPTIMIZATION")
    print("="*70)
    
    # PASS 1: Build baseline documents with complete content
    print("\n[PASS 1] Generating baseline documents with all code snippets and tables...")
    html_path = build_html_report()
    pdf_path, pass1_pages = await compile_pdf(html_path)
    
    # PASS 2: Detect exact physical page numbers
    print("\n[PASS 2] Scanning compiled PDF to extract exact physical page numbers...")
    import pymupdf
    pdf_doc = pymupdf.open(pdf_path)
    toc_items, fig_map, tbl_map = detect_all_page_numbers(pdf_doc)
    pdf_doc.close()
    
    print(f"Extracted {len(toc_items)} TOC items, {len(fig_map)} figures, {len(tbl_map)} tables.")
    
    # Re-render HTML, PDF, and DOCX with exact synchronized page numbers
    print("\n[PASS 2] Re-compiling final synchronized HTML, PDF, and Word documents...")
    html_path = build_html_report(toc_items=toc_items, fig_map=fig_map, tbl_map=tbl_map)
    pdf_path, final_pages = await compile_pdf(html_path)
    docx_path = build_docx_report(toc_items=toc_items, fig_map=fig_map, tbl_map=tbl_map)
    
    print("\n" + "="*70)
    print("NOETRIX MASTER PROJECT REPORT GENERATION COMPLETE & FULLY SYNCHRONIZED!")
    print(f"1. Standalone HTML:  {html_path}")
    print(f"2. Polished DOCX:    {docx_path}")
    print(f"3. Publication PDF:  {pdf_path} ({final_pages} pages)")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(main())
