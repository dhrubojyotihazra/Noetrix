import Link from "next/link";
import { ArrowLeft, CheckCircle2, ShieldAlert, Sparkles, Scale, Cpu, Lock } from "lucide-react";

export default function HowScoringWorksPage() {
  return (
    <div className="max-w-4xl mx-auto px-6 py-16 space-y-12">
      {/* Back button */}
      <div>
        <Link
          href="/"
          className="inline-flex items-center gap-1.5 text-xs font-bold uppercase tracking-wider text-ink/60 hover:text-ink mb-4"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Return Home</span>
        </Link>
        <h1 className="font-display text-5xl sm:text-6xl uppercase tracking-tight text-ink">
          HOW NOETRIX ATS SCORING WORKS
        </h1>
        <p className="font-sans text-sm sm:text-base text-ink/70 max-w-2xl mt-2 leading-relaxed">
          Full algorithmic transparency. We reject black-box LLM scoring in favor of deterministic heuristics, placement weighting, and mathematically reproducible rules.
        </p>
      </div>

      {/* The 6 Metrics Table */}
      <div className="border-2 border-ink rounded-3xl bg-card-surface p-8 shadow-sm space-y-6">
        <h2 className="font-display text-2xl uppercase tracking-wide text-ink">
          THE 6 EVALUATION DIMENSIONS
        </h2>

        <div className="space-y-6 text-xs font-sans">
          <div className="border-b border-ink/10 pb-4 space-y-1.5">
            <div className="flex justify-between items-center">
              <strong className="text-sm text-ink font-bold">1. Hard-Skill Keyword Match (30% Default Weight)</strong>
              <span className="bg-accent-yellow border border-ink text-ink font-bold px-2.5 py-0.5 rounded-full text-[10px]">
                TF-IDF + Taxonomy
              </span>
            </div>
            <p className="text-ink/80 leading-relaxed">
              Extracts target technologies and domain terms from the job description and matches them using whole-word regex boundaries and canonical synonym graphs (e.g. K8s = Kubernetes).
            </p>
            <div className="bg-canvas p-3 rounded-xl border border-ink/10 text-[11px] text-ink/70">
              <strong>Placement Weighting:</strong> Mentioned in experience bullets (1.0x weight) &gt; Skills section cloud (0.8x weight) &gt; General text/footer (0.5x weight). This mathematically penalizes keyword stuffing.
            </div>
          </div>

          <div className="border-b border-ink/10 pb-4 space-y-1.5">
            <div className="flex justify-between items-center">
              <strong className="text-sm text-ink font-bold">2. Semantic Narrative Fit (20% Default Weight)</strong>
              <span className="bg-accent-lilac border border-ink text-ink font-bold px-2.5 py-0.5 rounded-full text-[10px]">
                MiniLM Cosine Similarity
              </span>
            </div>
            <p className="text-ink/80 leading-relaxed">
              Encodes job responsibilities and resume work experience into 384-dimensional dense embeddings using <code className="bg-ink/5 px-1 rounded">all-MiniLM-L6-v2</code>. Evaluates overall narrative alignment even when different vocabulary is used.
            </p>
          </div>

          <div className="border-b border-ink/10 pb-4 space-y-1.5">
            <div className="flex justify-between items-center">
              <strong className="text-sm text-ink font-bold">3. Experience Tenure & Action Verbs (20% Default Weight)</strong>
              <span className="bg-card-surface border border-ink text-ink font-bold px-2.5 py-0.5 rounded-full text-[10px]">
                Tenure Ratio + Verbs
              </span>
            </div>
            <p className="text-ink/80 leading-relaxed">
              Compares candidate career tenure against the job description&apos;s minimum required years. Combines tenure alignment with a density scan of 63 verified high-impact action verbs.
            </p>
          </div>

          <div className="border-b border-ink/10 pb-4 space-y-1.5">
            <div className="flex justify-between items-center">
              <strong className="text-sm text-ink font-bold">4. Education & Certifications (10% Default Weight)</strong>
              <span className="bg-accent-emerald/20 border border-accent-emerald text-accent-emerald font-bold px-2.5 py-0.5 rounded-full text-[10px]">
                Prestige-Free
              </span>
            </div>
            <p className="text-ink/80 leading-relaxed">
              Evaluates degree hierarchy level (PhD, Master&apos;s, Bachelor&apos;s) and field of study alignment. Institution prestige is strictly ignored to eliminate socioeconomic bias.
            </p>
          </div>

          <div className="border-b border-ink/10 pb-4 space-y-1.5">
            <div className="flex justify-between items-center">
              <strong className="text-sm text-ink font-bold">5. Impact & Quantified Metrics (10% Default Weight)</strong>
              <span className="bg-accent-coral/20 border border-accent-coral text-accent-coral font-bold px-2.5 py-0.5 rounded-full text-[10px]">
                Strict 10-Pattern Regex
              </span>
            </div>
            <p className="text-ink/80 leading-relaxed">
              Scans bullet points for verifiable performance impact using 10 regex filters: percentages, dollar values, multipliers (3x), time savings, and user/request scale indicators.
            </p>
          </div>

          <div className="space-y-1.5">
            <div className="flex justify-between items-center">
              <strong className="text-sm text-ink font-bold">6. Format & ATS Readability (10% Default Weight)</strong>
              <span className="bg-canvas border border-ink text-ink font-bold px-2.5 py-0.5 rounded-full text-[10px]">
                Parse Health
              </span>
            </div>
            <p className="text-ink/80 leading-relaxed">
              Checks for single-column linear layout, standard headings, valid email/phone contact information, and word length bounds (150 - 1500 words). Deducts points for formatting hazards like multi-columns and non-text tables.
            </p>
          </div>
        </div>
      </div>

      {/* Special Rules */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="border-2 border-ink rounded-3xl bg-card-surface p-8 shadow-sm space-y-4">
          <div className="w-10 h-10 rounded-full bg-accent-coral/20 border border-accent-coral flex items-center justify-center">
            <ShieldAlert className="w-5 h-5 text-accent-coral" />
          </div>
          <h3 className="font-display text-2xl uppercase tracking-wide text-ink">
            THE MUST-HAVE KNOCKOUT CAP
          </h3>
          <p className="font-sans text-xs text-ink/70 leading-relaxed">
            If a recruiter marks specific technical requirements as mandatory must-haves, matching fewer than half (&lt;50%) of them automatically caps the candidate&apos;s overall score at 50 points and classifies them in the &apos;weak&apos; match band. This soft knockout ensures candidates lacking core qualifications never reach the top ranks while preserving their record for human review.
          </p>
        </div>

        <div className="border-2 border-ink rounded-3xl bg-card-surface p-8 shadow-sm space-y-4">
          <div className="w-10 h-10 rounded-full bg-accent-emerald/20 border border-accent-emerald flex items-center justify-center">
            <Scale className="w-5 h-5 text-accent-emerald" />
          </div>
          <h3 className="font-display text-2xl uppercase tracking-wide text-ink">
            FAIRNESS & ADVISORY CHARTER
          </h3>
          <p className="font-sans text-xs text-ink/70 leading-relaxed">
            All candidate PII (gender, age, photo, marital status, nationality) is stripped before scoring. Education does not favor Ivy League or elite institutions. Ranking is always strictly advisory; human recruiters maintain final hiring authority.
          </p>
        </div>
      </div>
    </div>
  );
}
