"use client";

import { useState, useEffect } from "react";
import { X, Check, ArrowRight, Sparkles, CheckSquare, Square } from "lucide-react";
import { DiffItem } from "@/lib/types";

interface DiffPreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAccept: (selectedDiffs?: DiffItem[]) => void;
  diffs: DiffItem[];
  scoreBefore: number;
  scoreAfter: number;
  gain: number;
  addedKeywords: string[];
}

// Word-level diff highlighter comparing original and modified phrases
function renderWordLevelDiff(original: string, modified: string) {
  if (!original) {
    return <span className="text-accent-emerald font-medium">{modified}</span>;
  }

  const origWords = original.split(/\s+/);
  const modWords = modified.split(/\s+/);

  // Find prefix differences
  let startCommon = 0;
  while (
    startCommon < origWords.length &&
    startCommon < modWords.length &&
    origWords[startCommon] === modWords[startCommon]
  ) {
    startCommon++;
  }

  let endCommon = 0;
  while (
    endCommon < origWords.length - startCommon &&
    endCommon < modWords.length - startCommon &&
    origWords[origWords.length - 1 - endCommon] === modWords[modWords.length - 1 - endCommon]
  ) {
    endCommon++;
  }

  const removedPart = origWords.slice(startCommon, origWords.length - endCommon).join(" ");
  const addedPart = modWords.slice(startCommon, modWords.length - endCommon).join(" ");
  const suffixPart = modWords.slice(modWords.length - endCommon).join(" ");
  const prefixPart = modWords.slice(0, startCommon).join(" ");

  return (
    <span className="font-sans text-xs leading-relaxed">
      {prefixPart && <span className="text-ink/80">{prefixPart} </span>}
      {removedPart && (
        <span className="bg-accent-coral/20 text-accent-coral line-through decoration-accent-coral px-1 py-0.5 rounded mr-1">
          {removedPart}
        </span>
      )}
      {addedPart && (
        <span className="bg-accent-emerald/25 text-ink font-semibold px-1 py-0.5 rounded border border-accent-emerald/40 mr-1">
          {addedPart}
        </span>
      )}
      {suffixPart && <span className="text-ink/80"> {suffixPart}</span>}
    </span>
  );
}

export default function DiffPreviewModal({
  isOpen,
  onClose,
  onAccept,
  diffs,
  scoreBefore,
  scoreAfter,
  gain,
  addedKeywords,
}: DiffPreviewModalProps) {
  const [selectedIndices, setSelectedIndices] = useState<Set<number>>(
    () => new Set(diffs.map((_, i) => i))
  );

  // Re-initialize selectedIndices whenever modal opens or diffs change
  useEffect(() => {
    if (isOpen) {
      setSelectedIndices(new Set(diffs.map((_, i) => i)));
    }
  }, [isOpen, diffs]);

  if (!isOpen) return null;

  // Calculate dynamic gain based on currently selected diffs
  const totalDiffs = diffs.length;
  const selectedCount = selectedIndices.size;
  const maxPossibleGain = gain > 0 ? gain : Math.max(0, Math.round((scoreAfter - scoreBefore) * 10) / 10);
  const activeGain = totalDiffs > 0 ? Math.round((maxPossibleGain * (selectedCount / totalDiffs)) * 10) / 10 : 0;
  const currentTailoredScore = Math.min(100, Math.round((scoreBefore + activeGain) * 10) / 10);

  const toggleIndex = (idx: number) => {
    const next = new Set(selectedIndices);
    if (next.has(idx)) {
      next.delete(idx);
    } else {
      next.add(idx);
    }
    setSelectedIndices(next);
  };

  const selectAll = () => setSelectedIndices(new Set(diffs.map((_, i) => i)));
  const deselectAll = () => setSelectedIndices(new Set());

  const handleApply = () => {
    const chosen = diffs.filter((_, i) => selectedIndices.has(i));
    onAccept(chosen);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-ink/70 backdrop-blur-sm">
      <div className="bg-card-surface border-2 border-ink rounded-3xl max-w-3xl w-full max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="p-6 border-b-2 border-ink bg-canvas flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-accent-yellow border-2 border-ink flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-ink" />
            </div>
            <div>
              <h3 className="font-display text-2xl uppercase tracking-wide text-ink">
                Tailoring Diff & Per-Change Review
              </h3>
              <p className="font-sans text-xs text-ink/70">
                Accept or reject each specific change. Zero fabricated facts or hallucinated metrics.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-9 h-9 rounded-full border border-ink/20 hover:bg-ink/5 flex items-center justify-center transition-colors"
          >
            <X className="w-5 h-5 text-ink" />
          </button>
        </div>

        {/* Score Gain Banner */}
        <div className="bg-accent-lilac/30 border-b border-ink/15 p-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-ink/60">Current Score</span>
              <div className="font-display text-xl text-ink">{scoreBefore}%</div>
            </div>
            <ArrowRight className="w-4 h-4 text-ink/50" />
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-ink/60">Tailored Score</span>
              <div className="font-display text-xl text-accent-emerald font-bold">{currentTailoredScore}%</div>
            </div>
          </div>
          <div className="bg-accent-emerald text-canvas font-sans text-xs font-bold px-3 py-1.5 rounded-full">
            +{activeGain} pts Estimated Gain
          </div>
        </div>

        {/* Diff Content List */}
        <div className="p-6 overflow-y-auto space-y-6 flex-1">
          {addedKeywords.length > 0 && (
            <div>
              <h4 className="text-xs font-bold uppercase tracking-widest text-ink mb-2">
                Grounded Skills Detected From Experience ({addedKeywords.length})
              </h4>
              <div className="flex flex-wrap gap-2">
                {addedKeywords.map((kw, i) => (
                  <span
                    key={i}
                    className="bg-accent-yellow/40 text-ink border border-ink text-xs font-semibold px-2.5 py-1 rounded-full"
                  >
                    ✓ {kw}
                  </span>
                ))}
              </div>
            </div>
          )}

          <div>
            <div className="flex items-center justify-between mb-3">
              <h4 className="text-xs font-bold uppercase tracking-widest text-ink">
                Suggested Enhancements ({diffs.length})
              </h4>
              <div className="flex gap-3 text-xs">
                <button
                  onClick={selectAll}
                  className="text-ink/60 hover:text-ink font-semibold underline underline-offset-2"
                >
                  Select All
                </button>
                <button
                  onClick={deselectAll}
                  className="text-ink/60 hover:text-ink font-semibold underline underline-offset-2"
                >
                  Deselect All
                </button>
              </div>
            </div>

            {diffs.length === 0 ? (
              <p className="text-sm text-ink/60 italic">No field differences detected.</p>
            ) : (
              <div className="space-y-3">
                {diffs.map((d, idx) => {
                  const isChecked = selectedIndices.has(idx);

                  return (
                    <div
                      key={idx}
                      onClick={() => toggleIndex(idx)}
                      className={`border-2 rounded-2xl p-4 cursor-pointer transition-all ${
                        isChecked
                          ? "border-ink bg-card-surface shadow-2xs"
                          : "border-ink/15 bg-canvas/40 opacity-60"
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <button
                          type="button"
                          className="mt-0.5 shrink-0 text-ink"
                          aria-label={isChecked ? "Deselect change" : "Select change"}
                        >
                          {isChecked ? (
                            <CheckSquare className="w-5 h-5 text-accent-emerald" />
                          ) : (
                            <Square className="w-5 h-5 text-ink/40" />
                          )}
                        </button>

                        <div className="space-y-1.5 flex-1">
                          <div className="flex items-center justify-between text-[11px]">
                            <span className="font-bold uppercase tracking-wider text-ink/70">
                              {d.section} · {d.change_type}
                            </span>
                            <span className="text-[10px] font-semibold text-ink/50">
                              {isChecked ? "Accepted" : "Rejected"}
                            </span>
                          </div>

                          <div className="pt-1">
                            {renderWordLevelDiff(d.original, d.modified)}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Actions Footer */}
        <div className="p-5 border-t-2 border-ink bg-canvas flex items-center justify-between">
          <span className="text-xs font-semibold text-ink/70">
            {selectedIndices.size} of {diffs.length} changes selected
          </span>

          <div className="flex gap-3">
            <button
              onClick={onClose}
              className="px-5 py-2.5 rounded-full border border-ink text-sm font-semibold hover:bg-ink/5 transition-colors"
            >
              Discard
            </button>
            <button
              onClick={handleApply}
              disabled={selectedIndices.size === 0}
              className="flex items-center gap-2 bg-ink text-canvas px-6 py-2.5 rounded-full text-sm font-semibold hover:bg-ink-slate transition-all shadow-md disabled:opacity-40"
            >
              <Check className="w-4 h-4 text-accent-yellow" />
              <span>Apply Selected ({selectedIndices.size})</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
