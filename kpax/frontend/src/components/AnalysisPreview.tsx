import { useState } from "react";
import type { Expert } from "../api/client";

interface Props {
  experts: Expert[];
  analysisAngles: string[];
  coreTension: string;
  onSupplement: (text: string) => Promise<void>;
  onStart: () => void;
}

const STANCE_COLORS: Record<string, string> = {
  cautious: "text-amber-400 bg-amber-500/10 border-amber-500/30",
  optimistic: "text-emerald-400 bg-emerald-500/10 border-emerald-500/30",
  neutral: "text-zinc-400 bg-zinc-500/10 border-zinc-500/30",
  contrarian: "text-rose-400 bg-rose-500/10 border-rose-500/30",
};

const STANCE_LABELS: Record<string, string> = {
  cautious: "Cautious",
  optimistic: "Optimistic",
  neutral: "Neutral",
  contrarian: "Contrarian",
};

export default function AnalysisPreview({
  experts,
  analysisAngles,
  coreTension,
  onSupplement,
  onStart,
}: Props) {
  const [supplement, setSupplement] = useState("");
  const [supplementSent, setSupplementSent] = useState(false);

  const handleSupplement = async () => {
    if (supplement.trim()) {
      await onSupplement(supplement.trim());
      setSupplementSent(true);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <p className="text-xs text-kpax-500 font-mono uppercase tracking-wider mb-2">
          Analysis Framework
        </p>
        <p className="text-zinc-400 text-sm mb-4">
          Based on your question and context, here is the analysis plan:
        </p>
      </div>

      {/* Core tension */}
      <div className="bg-zinc-900/30 border border-zinc-800/50 rounded-xl p-4">
        <p className="text-xs text-zinc-500 mb-1">Core Tension</p>
        <p className="text-white text-sm">{coreTension}</p>
      </div>

      {/* Expert cards */}
      <div className="space-y-3">
        <p className="text-xs text-zinc-500 font-mono uppercase tracking-wider">
          Expert Panel ({experts.length})
        </p>
        <div className="grid gap-3 sm:grid-cols-2">
          {experts.map((expert, i) => {
            const stanceCls = STANCE_COLORS[expert.stance_hint] || STANCE_COLORS.neutral;
            return (
              <div
                key={i}
                className="bg-zinc-900/40 border border-zinc-800/50 rounded-xl p-4 space-y-2"
              >
                <div className="flex items-start justify-between gap-2">
                  <h3 className="text-white text-sm font-medium">{expert.name}</h3>
                  <span
                    className={`text-[10px] px-2 py-0.5 rounded-full border ${stanceCls}`}
                  >
                    {STANCE_LABELS[expert.stance_hint] || expert.stance_hint}
                  </span>
                </div>
                <p className="text-xs text-zinc-500">{expert.role}</p>
                <p className="text-xs text-zinc-600">{expert.perspective}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Analysis angles */}
      <div className="flex flex-wrap gap-2">
        <span className="text-xs text-zinc-500 mr-1 self-center">Angles:</span>
        {analysisAngles.map((angle) => (
          <span
            key={angle}
            className="text-xs text-kpax-400 bg-kpax-600/10 border border-kpax-600/20 px-2.5 py-1 rounded-full"
          >
            {angle}
          </span>
        ))}
      </div>

      {/* Supplement area */}
      <div className="bg-zinc-900/20 border border-zinc-800/30 rounded-xl p-4 space-y-3">
        <p className="text-sm text-zinc-400">
          Anything else I should know? The more context you provide, the better the analysis.
        </p>
        {!supplementSent ? (
          <div className="flex gap-2">
            <textarea
              value={supplement}
              onChange={(e) => setSupplement(e.target.value)}
              placeholder="Optional — add anything you think is relevant..."
              rows={2}
              className="flex-1 bg-zinc-900/50 border border-zinc-800 rounded-lg px-4 py-2.5 text-white text-sm placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-kpax-600/50 resize-none"
            />
            <button
              onClick={handleSupplement}
              disabled={!supplement.trim()}
              className="self-end px-4 py-2.5 bg-zinc-800 hover:bg-zinc-700 disabled:opacity-30 text-zinc-300 text-xs rounded-lg transition-all"
            >
              Add
            </button>
          </div>
        ) : (
          <p className="text-xs text-kpax-500">Context added.</p>
        )}
      </div>

      {/* Start button */}
      <button
        onClick={onStart}
        className="w-full bg-kpax-600 hover:bg-kpax-700 text-white font-medium py-3.5 px-6 rounded-xl transition-all text-sm"
      >
        Start Expert Analysis
      </button>
    </div>
  );
}
