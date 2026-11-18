# Noetrix ATS — Model Context Protocol (MCP) Server

Connect your ATS screening and scoring engine directly into **Claude Desktop**, **Cursor**, **Antigravity**, **Windsurf**, or any MCP-compatible AI environment.

With this MCP server running, Claude (or any AI client) can natively call Noetrix's explainable 6-metric ATS engine:
- `score_resume(resume_text, job_description)`
- `score_resume_file(file_path, job_description)`
- `parse_resume(resume_text)`
- `parse_resume_file(file_path)`
- `parse_job_description(job_description, title)`
- `rank_resumes(resumes, job_description)`
- `explain_score(resume_text, job_description)`

---

## 🚀 Quick Setup

### 1. Claude Desktop Setup

Open your Claude Desktop configuration file:
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

Add the `noetrix-ats` server:

```json
{
  "mcpServers": {
    "noetrix-ats": {
      "command": "python",
      "args": [
        "c:\\Users\\HP\\Desktop\\dhruv\\Noetrix\\noetrix\\backend\\mcp_server.py"
      ]
    }
  }
}
```

Restart Claude Desktop. You will see a 🔌 icon or hammer icon confirming `noetrix-ats` is active with 7 tools.

---

### 2. Cursor IDE Setup

In your project root, add or update `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "noetrix-ats": {
      "command": "python",
      "args": [
        "c:\\Users\\HP\\Desktop\\dhruv\\Noetrix\\noetrix\\backend\\mcp_server.py"
      ]
    }
  }
}
```

---

### 3. Testing Locally via CLI

Run the server directly via standard I/O:

```bash
cd c:\Users\HP\Desktop\dhruv\Noetrix\noetrix\backend
python mcp_server.py
```

Or using the Python module:

```bash
python -m app.mcp_server
```

---

## 🛠️ Available MCP Tools

### 1. `score_resume`
Runs Noetrix's full 6-metric ATS evaluation against candidate text.
- **Parameters**:
  - `resume_text` (string, required): Raw text or markdown of the resume.
  - `job_description` (string, required): Full text of the job description.
  - `weights` (dict, optional): Custom metric weights (default: `{"keyword_match": 0.30, "semantic_fit": 0.20, "experience": 0.20, "education": 0.10, "impact": 0.10, "format": 0.10}`).
  - `must_have_cap` (float, optional): Anti-stuffing ceiling (default: `50.0`).
- **Returns**:
  - `overall_score` (0-100)
  - `match_band` (`"strong"`, `"moderate"`, or `"weak"`)
  - `is_capped` (bool: whether candidate triggered the 50% Soft Knockout rule)
  - `metrics` (breakdown of each metric with score, evidence quotes, missing items, and rationale)
  - `matched_keywords` & `missing_keywords`
  - `priority_fixes` (Top 5 prioritized action items)
  - `risk_flags` (Tenure deficit, multi-column risks, metric scarcity)

### 2. `score_resume_file`
Evaluates a local file directly (`.pdf`, `.docx`, `.txt`, `.md`).
- **Parameters**:
  - `file_path` (string, required): Path to the candidate's document on disk.
  - `job_description` (string, required): Target job description text.

### 3. `parse_resume` / `parse_resume_file`
Extracts structured data from resume text or documents without scoring:
- Name, email, phone, location, LinkedIn/GitHub links
- Detected sections (`summary`, `experience`, `education`, `skills`, `projects`, `certifications`)
- Bullet-level work history and project entries
- Skills matched against Noetrix's 350+ technology taxonomy
- Parse confidence score (0.0 to 1.0) and layout health (columns, tables)

### 4. `parse_job_description`
Extracts recruiting criteria from a job description:
- Inferred role title
- Mandatory must-have skills
- Preferred nice-to-have skills
- Minimum experience requirements (years)
- Education credentials
- Responsibilities

### 5. `rank_resumes`
Batch ranks multiple candidates against a single JD:
- **Parameters**:
  - `resumes` (list of objects): Each item has `{"name": "...", "resume_text": "..."}` or `{"name": "...", "file_path": "..."}`.
  - `job_description` (string, required).
- **Returns**:
  - Sorted leaderboard with ranks (1, 2, 3...), candidate names, scores, match bands, experience years, and risk flags.

### 6. `explain_score`
Generates an in-depth candidate dossier:
- Strengths with exact resume citations
- Gaps with missing qualifications
- Anti-gaming analysis (soft knockout status)
- Prioritized bullet improvements using Google's XYZ formula

---

## 💡 Example Prompts to Ask Claude / Cursor

Once connected, you can say:

> "Score this resume text against this job posting using Noetrix ATS."

> "Audit my resume file at `C:\Users\HP\Desktop\dhruv\Noetrix\sample_resume_alex_chen.pdf` against the Senior Backend role requirements."

> "Rank these 3 candidate resumes against our DevOps job description and give me the leaderboard."

> "Why did this resume get a moderate score? Run an explainability breakdown."
