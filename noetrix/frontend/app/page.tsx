import Link from "next/link";
import { ArrowUpRight, CheckCircle2, ShieldCheck, Sparkles, FileText, Users, ArrowRight } from "lucide-react";
import Ticker from "@/components/ui/Ticker";
import SeamfulOrb from "@/components/ui/SeamfulOrb";
import RecruiterWorkflow from "@/components/landing/RecruiterWorkflow";
import TeamShowcasePro from "@/components/landing/TeamShowcasePro";

export default function HomePage() {
  return (
    <div className="w-full flex flex-col relative overflow-hidden">
      {/* Hero Section */}
      <section className="relative px-6 pt-12 sm:pt-16 pb-12 sm:pb-16 max-w-7xl mx-auto w-full">
        {/* Tier 1: Top Hero Head (Full-Width Display Headline + Parallax Orb) */}
        <div className="w-full relative">
          {/* Plain Text Kicker */}
          <p className="font-sans text-xs sm:text-sm font-bold uppercase tracking-widest text-ink/75 mb-6">
            ATS simulation for candidates and recruiters
          </p>

          <div className="relative w-full">
            {/* Parallax Orb positioned clear of headline period and inside viewport bounds */}
            <div className="absolute right-0 sm:right-2 lg:right-4 -top-10 sm:-top-16 z-0 pointer-events-none hidden sm:block">
              <SeamfulOrb />
            </div>

            {/* Headline with high-contrast second line */}
            <h1 className="relative z-10 font-display text-5xl sm:text-7xl md:text-8xl lg:text-[122px] uppercase tracking-tight text-ink leading-[0.86] select-none">
              SCORE THE CV.<br />
              <span className="text-ink/85">SHOW EVERY REASON.</span>
            </h1>
          </div>
        </div>

        {/* Tier 2: Bottom Hero Foot (Tightened spacing, aligned baselines) */}
        <div className="mt-8 sm:mt-12 flex flex-col lg:flex-row items-start justify-between gap-12 lg:gap-16 relative z-20">
          {/* Left Column: Lead Paragraph & Actions */}
          <div className="max-w-xl space-y-8">
            <p className="font-sans text-lg sm:text-xl text-ink/85 leading-relaxed font-normal">
              Noetrix scores a CV against a job description and shows the evidence behind every point. Candidates use it to find and fix gaps before they apply. Recruiters use it to rank a batch of CVs, with a reason for each rank. Nothing is saved to an account or a database.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-1">
              <Link
                href="/candidate/analyze"
                className="group flex items-center gap-3 bg-ink text-canvas font-sans font-semibold text-base px-8 py-4 rounded-full hover:bg-ink-slate transition-all shadow-md"
              >
                <span>Scan my CV</span>
                <ArrowUpRight className="w-5 h-5 transition-transform group-hover:translate-x-1 group-hover:-translate-y-1" />
              </Link>
              <Link
                href="/recruiter/setup"
                className="group flex items-center gap-3 bg-transparent border-2 border-ink text-ink font-sans font-semibold text-base px-8 py-4 rounded-full hover:bg-ink/5 transition-all"
              >
                <span>Rank candidates</span>
                <ArrowRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
              </Link>
            </div>
          </div>

          {/* Right Column: Featured Engine Protocol Card (top-aligned to left column) */}
          <div className="w-full lg:w-[460px] shrink-0">
            <div className="rounded-[30px] border border-ink/15 bg-[#fdfdfc]/95 backdrop-blur-md p-7 sm:p-8 shadow-[0_24px_80px_rgba(12,15,23,0.08)] space-y-6">
              <div className="flex items-center justify-between border-b border-ink/10 pb-4">
                <span className="text-xs font-bold uppercase tracking-wider text-ink/60">How scoring works</span>
                <span className="bg-accent-yellow text-ink text-xs font-bold px-3 py-1 rounded-full border border-ink shadow-2xs">
                  No sign-up
                </span>
              </div>

              <div className="space-y-4 font-sans text-sm">
                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-accent-emerald shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-ink block font-semibold">Six scored parts</strong>
                    <span className="text-ink/70 text-xs">Keywords, meaning match, experience, education, impact and format. The same CV and job description always give the same score.</span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-accent-emerald shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-ink block font-semibold">Must-have rule</strong>
                    <span className="text-ink/70 text-xs">If a CV covers fewer than half of the must-have skills, the total is capped at 50.</span>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <CheckCircle2 className="w-5 h-5 text-accent-emerald shrink-0 mt-0.5" />
                  <div>
                    <strong className="text-ink block font-semibold">No account, no database</strong>
                    <span className="text-ink/70 text-xs">Files are processed in memory and not saved. AI tailoring sends bullet text to the model provider.</span>
                  </div>
                </div>
              </div>

              <div className="pt-4 border-t border-ink/10 flex items-center justify-between">
                <div>
                  <div className="text-[11px] text-ink/60 uppercase tracking-widest font-bold">
                    Scored parts
                  </div>
                  <div className="font-display text-4xl text-ink">6</div>
                </div>
                <div className="flex items-center gap-2 bg-ink/5 px-3 py-1.5 rounded-full border border-ink/10">
                  <span className="w-2.5 h-2.5 rounded-full bg-accent-emerald animate-pulse" />
                  <span className="text-xs font-bold text-ink">Files not saved</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Marquee Ticker */}
      <Ticker />

      {/* Two Doors Section */}
      <section className="px-6 py-24 max-w-7xl mx-auto w-full">
        {/* Split Section Head (matches Seamful Image 1) */}
        <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-8 mb-14 sm:mb-16">
          <div className="max-w-xl">
            <span className="font-sans text-xs sm:text-sm font-bold uppercase tracking-widest text-ink/60 block mb-3">
              One scoring engine, two uses
            </span>
            <h2 className="font-display text-5xl sm:text-6xl md:text-7xl uppercase tracking-tight text-ink leading-[0.92]">
              APPLYING OR HIRING?
            </h2>
          </div>
          <div className="max-w-md">
            <p className="font-sans text-base sm:text-lg text-ink/75 leading-relaxed">
              Candidates and recruiters use the same scoring engine, so a candidate sees the same six scored parts that a recruiter ranks on.
            </p>
          </div>
        </div>

        {/* Wide Seamful Program Cards (matches Seamful Image 3 in wide aspect ratio) */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Card 01: Candidate Door */}
          <Link
            href="/candidate/analyze"
            className="group flex flex-col justify-between border-2 border-ink rounded-[32px] bg-card-surface p-5 sm:p-6 transition-all hover:-translate-y-1.5 hover:shadow-2xl"
          >
            <div>
              {/* Colored Cover Header (Wide Aspect Ratio, matching Seamful Image 3) */}
              <div className="w-full h-52 sm:h-60 rounded-2xl relative overflow-hidden bg-accent-yellow p-6 flex flex-col justify-between mb-6 shadow-xs border border-ink/10">
                {/* Top: Black Chip */}
                <div className="z-10">
                  <span className="bg-ink text-canvas text-xs font-bold px-3.5 py-1.5 rounded-full uppercase tracking-wider inline-flex items-center gap-1.5 shadow-xs">
                    Candidate
                  </span>
                </div>

                {/* Geometric Wireframe Ring Arc */}
                <div className="absolute -bottom-14 -left-10 w-48 h-48 rounded-full border border-ink/25 pointer-events-none" />

                {/* Giant Watermark Numeral */}
                <span className="font-display text-8xl sm:text-9xl text-ink/25 absolute right-6 -bottom-2 select-none leading-none pointer-events-none transition-transform group-hover:scale-105">
                  01
                </span>
              </div>

              {/* Card Text Content */}
              <div className="px-2">
                <div className="text-xs font-bold uppercase tracking-wider text-ink/50 mb-2 font-sans">
                  One CV, one job description
                </div>
                <h3 className="font-display text-3xl sm:text-4xl uppercase tracking-wide text-ink mb-3 group-hover:text-ink/80 transition-colors">
                  SCORE & TAILOR CV
                </h3>
                <p className="font-sans text-sm sm:text-base text-ink/70 leading-relaxed mb-6">
                  Paste a job description and upload your CV. See what the parser reads, get a score in six parts, then edit weak bullets with AI and re-score to compare before and after.
                </p>
              </div>
            </div>

            {/* Card Foot */}
            <div className="mx-2 pt-5 border-t border-ink/10 flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-widest text-ink/60">
                No account needed
              </span>
              <div className="flex items-center gap-2 font-sans font-bold text-sm text-ink group-hover:translate-x-1 transition-transform">
                <span>Check my CV</span>
                <ArrowRight className="w-4 h-4" />
              </div>
            </div>
          </Link>

          {/* Card 02: Recruiter Door */}
          <Link
            href="/recruiter/setup"
            className="group flex flex-col justify-between border-2 border-ink rounded-[32px] bg-card-surface p-5 sm:p-6 transition-all hover:-translate-y-1.5 hover:shadow-2xl"
          >
            <div>
              {/* Colored Cover Header (Wide Aspect Ratio, matching Seamful Image 3) */}
              <div className="w-full h-52 sm:h-60 rounded-2xl relative overflow-hidden bg-accent-lilac p-6 flex flex-col justify-between mb-6 shadow-xs border border-ink/10">
                {/* Top: Black Chip */}
                <div className="z-10">
                  <span className="bg-ink text-canvas text-xs font-bold px-3.5 py-1.5 rounded-full uppercase tracking-wider inline-flex items-center gap-1.5 shadow-xs">
                    Recruiter
                  </span>
                </div>

                {/* Geometric Wireframe Ring Arc */}
                <div className="absolute -bottom-14 -left-10 w-48 h-48 rounded-full border border-ink/25 pointer-events-none" />

                {/* Giant Watermark Numeral */}
                <span className="font-display text-8xl sm:text-9xl text-ink/25 absolute right-6 -bottom-2 select-none leading-none pointer-events-none transition-transform group-hover:scale-105">
                  02
                </span>
              </div>

              {/* Card Text Content */}
              <div className="px-2">
                <div className="text-xs font-bold uppercase tracking-wider text-ink/50 mb-2 font-sans">
                  Many CVs, one job description
                </div>
                <h3 className="font-display text-3xl sm:text-4xl uppercase tracking-wide text-ink mb-3 group-hover:text-ink/80 transition-colors">
                  RANK AND SHORTLIST CVS
                </h3>
                <p className="font-sans text-sm sm:text-base text-ink/70 leading-relaxed mb-6">
                  Paste a job description, adjust the scoring weights, and upload up to 50 CVs. Open any candidate to see the evidence behind their score, mark them Shortlist, Hold or Reject, and export the ranking as CSV.
                </p>
              </div>
            </div>

            {/* Card Foot */}
            <div className="mx-2 pt-5 border-t border-ink/10 flex items-center justify-between">
              <span className="text-xs font-bold uppercase tracking-widest text-ink/60">
                Re-ranks as you change weights
              </span>
              <div className="flex items-center gap-2 font-sans font-bold text-sm text-ink group-hover:translate-x-1 transition-transform">
                <span>Rank candidates</span>
                <ArrowRight className="w-4 h-4" />
              </div>
            </div>
          </Link>
        </div>
      </section>

      {/* Candidate Flow Section (High Contrast Dark Mode) */}
      <section className="bg-ink text-canvas py-24 sm:py-32 px-6 border-t-2 border-ink relative">
        <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 items-start">
          {/* Left Column: Yellow Kicker + Giant Anton Title */}
          <div className="lg:col-span-5 space-y-4">
            <span className="text-accent-yellow font-sans text-xs font-bold uppercase tracking-widest block">
              How candidate scoring works
            </span>
            <h2 className="font-display text-5xl sm:text-7xl lg:text-[84px] tracking-tight text-canvas uppercase leading-[0.92]">
              FOUR STEPS<br />
              FOR CANDIDATES.
            </h2>
            <div className="pt-4">
              <Link
                href="/candidate/setup"
                className="inline-flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-accent-yellow hover:underline"
              >
                <span>Scan my CV</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
            </div>
          </div>

          {/* Right Column: 4-Row Linear List with High-Contrast Text */}
          <div className="lg:col-span-7 border-t border-canvas/20">
            {/* Step 01 */}
            <div className="border-b border-canvas/20 py-8 sm:py-10 flex items-start gap-6 sm:gap-10">
              <span className="font-sans font-bold text-accent-yellow text-sm sm:text-base tracking-wider pt-0.5 shrink-0">
                01
              </span>
              <div className="space-y-1.5 max-w-xl">
                <h3 className="font-sans font-bold text-lg sm:text-xl text-canvas tracking-tight">
                  Paste the job description
                </h3>
                <p className="font-sans text-xs sm:text-sm text-canvas/90 leading-relaxed font-normal">
                  Noetrix pulls out the must-have skills, the nice-to-haves and the minimum years of experience, then scores your CV against them.
                </p>
              </div>
            </div>

            {/* Step 02 */}
            <div className="border-b border-canvas/20 py-8 sm:py-10 flex items-start gap-6 sm:gap-10">
              <span className="font-sans font-bold text-accent-yellow text-sm sm:text-base tracking-wider pt-0.5 shrink-0">
                02
              </span>
              <div className="space-y-1.5 max-w-xl">
                <h3 className="font-sans font-bold text-lg sm:text-xl text-canvas tracking-tight">
                  See what the parser reads
                </h3>
                <p className="font-sans text-xs sm:text-sm text-canvas/90 leading-relaxed font-normal">
                  We show the text and fields pulled from your CV, so you can catch broken columns, missing tables and lost contact details.
                </p>
              </div>
            </div>

            {/* Step 03 */}
            <div className="border-b border-canvas/20 py-8 sm:py-10 flex items-start gap-6 sm:gap-10">
              <span className="font-sans font-bold text-accent-yellow text-sm sm:text-base tracking-wider pt-0.5 shrink-0">
                03
              </span>
              <div className="space-y-1.5 max-w-xl">
                <h3 className="font-sans font-bold text-lg sm:text-xl text-canvas tracking-tight">
                  Get a score in six parts
                </h3>
                <p className="font-sans text-xs sm:text-sm text-canvas/90 leading-relaxed font-normal">
                  A score out of 100 built from keyword match, meaning match, experience, education level, impact and format. Each part shows the evidence behind it.
                </p>
              </div>
            </div>

            {/* Step 04 */}
            <div className="border-b border-canvas/20 py-8 sm:py-10 flex items-start gap-6 sm:gap-10">
              <span className="font-sans font-bold text-accent-yellow text-sm sm:text-base tracking-wider pt-0.5 shrink-0">
                04
              </span>
              <div className="space-y-1.5 max-w-xl">
                <h3 className="font-sans font-bold text-lg sm:text-xl text-canvas tracking-tight">
                  Rewrite weak bullets and re-score
                </h3>
                <p className="font-sans text-xs sm:text-sm text-canvas/90 leading-relaxed font-normal">
                  AI suggests clearer wording and asks you for real numbers instead of inventing them. Re-score to see what changed.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Recruiter Workflow Section */}
      <RecruiterWorkflow />

      {/* Team Member Section (Framer Team Showcase Pro with same bleed yellow) */}
      <section className="bg-accent-yellow text-ink py-12 px-6 relative overflow-hidden border-t-2 border-ink">
        {/* Giant Watermark NOETRIX Brand Wordmark (Soft 0.04 opacity, moved up clear of dock) */}
        <div className="font-display text-[150px] sm:text-[230px] lg:text-[280px] text-ink/[0.04] absolute -right-6 top-1/2 -translate-y-1/2 select-none pointer-events-none uppercase leading-none tracking-tighter">
          NOETRIX
        </div>

        <div className="max-w-7xl mx-auto relative z-10">
          {/* Section Head: Split Layout */}
          <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-6 mb-6 sm:mb-8">
            <h2 className="font-display text-4xl sm:text-6xl lg:text-7xl uppercase tracking-tight text-ink leading-none">
              WHO BUILT THIS
            </h2>
            <p className="font-sans text-sm sm:text-base text-ink/80 leading-relaxed max-w-sm lg:ml-auto lg:text-right font-medium">
              A five-person team building an auditable resume scorer you can check line by line.
            </p>
          </div>

          <TeamShowcasePro
            eyebrow="The team"
            heading="Say hello to"
            pad={0}
            rule="#0C0F17"
            stageMax={1232}
            portraitShare={0.245}
            radius={24}
            dockSize={46}
            dockGrow={20}
            navSize={42}
          />
        </div>
      </section>
    </div>
  );
}
