# Noetrix — Design System & Candidate AI Editing Suite Specification

## 1. Editorial Visual Design System (Inspired by Seamful / Woblo)

### Color Palette
- **Canvas / Background**: Warm Parchment `#F6EFE3`, Card Surface `#FDFAF4`
- **Ink / Typography**: Deep Charcoal / Ink `#0C0F17`, Secondary Slate `#1D2230`, Muted `#0C0F1773`
- **Borders**: Crisp Ink Borders `rgba(12, 15, 23, 0.15)` and `2px solid #0C0F17`
- **Accent 1 (Electric Yellow)**: `#FAE425` — used for primary highlights, candidate badges, ticker banner
- **Accent 2 (Pastel Lilac / Lavender)**: `#DBACF0` — used for recruiter door, AI enhancement badges
- **Accent 3 (Coral / Tangerine)**: `#FF8465` — used for warnings, missing keywords, priority fixes
- **Success / Emerald**: `#10B981` — used for matched keywords, passing scores

### Typography
- **Display & Section Headings**: `Anton` / `Anton Placeholder`, uppercase, tight line-height, bold editorial punch
- **Body, UI & Numbers**: `DM Sans`, weights 400, 500, 600, 700
- **Code & Tech Snippets**: `Inter` / `JetBrains Mono`

### Components & Micro-Interactions
- **Pill Buttons**: 100px rounded pill (`rounded-full`), deep ink background `#0C0F17` with light text `#F6EFE3` and SVG arrow, or outlined with 2px ink border.
- **Numbered Cards**: Large editorial numbers `01`, `02`, `03` in accent colors.
- **Ticker Ribbon**: Angled or horizontal running marquee ribbon with `·` separators.
- **Split Views**: Clean 2-pane comparative layouts with distinct border dividers.

---

## 2. Candidate AI Editing & Tailoring Suite (from Resume-Matcher)

### Features
1. **Interactive Resume Editor (`/candidate/editor`)**:
   - Structured editor allowing candidates to refine their Summary, Work Experience bullets, and Skills.
   - Live keyword highlighting: JD keywords matching resume text are highlighted in real-time.
2. **AI Bullet Enhancer**:
   - Single-click "Enhance Bullet" button on any experience bullet.
   - Uses the Google/Laszlo Bock XYZ formula: *"Accomplished [X] as measured by [Y], by doing [Z]"* + naturally incorporates relevant target JD keywords and action verbs.
   - Dual-engine: Calls LLM if configured, with a built-in intelligent rule-based template transformer fallback that works instantly offline/without API keys!
3. **AI Keyword Refiner & Injector**:
   - Analyzes gap between JD requirements and resume.
   - Categorizes keywords into **Matched**, **Missing**, and **Suggested Placements** (e.g. recommending which specific bullet or skills group to add it to).
4. **Diff Preview Modal**:
   - Side-by-side or unified diff preview before accepting edits.
   - Displays statistics: `+X Keywords added`, `Y Bullets enhanced`, `Estimated score delta: +Z pts`.
5. **Live Re-scoring Engine**:
   - "Re-score" button triggers immediate re-evaluation against the target JD.
   - Shows before & after comparison bars (e.g., `64` → `82`, `+18 pts`).
6. **Export Clean PDF/Text**:
   - Download the optimized resume in ATS-friendly format.
