export default function Ticker() {
  const items = [
    "EXPLAINABLE RANKINGS",
    "NO STORED DATA",
    "SIX-PART SCORING",
    "NO SCHOOL PRESTIGE BIAS",
    "AI BULLET FIXES",
    "30-CV BATCH SCREENING",
    "IDENTICAL REPEATABLE SCORES",
  ];

  return (
    <div className="w-full overflow-hidden py-10 sm:py-14 select-none">
      <div className="w-[115%] -ml-[7.5%] -rotate-[1.8deg] bg-ink text-canvas py-5 sm:py-6 border-y-2 border-ink shadow-xl">
        <div className="flex w-max animate-marquee space-x-12 whitespace-nowrap">
          {[...items, ...items, ...items].map((text, idx) => (
            <div
              key={idx}
              className="flex items-center gap-10 font-display text-2xl sm:text-3xl uppercase tracking-wider"
            >
              <span>{text}</span>
              <span className="text-accent-yellow text-xl">✦</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
