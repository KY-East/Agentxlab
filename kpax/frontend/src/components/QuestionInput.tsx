import { useState } from "react";

interface Props {
  onSubmit: (question: string) => void;
  loading: boolean;
}

const EXAMPLES = [
  "Should I buy a house in Shanghai?",
  "Brazil vs Germany — how do I analyze this match?",
  "Should I quit my job and start a business?",
  "Is it worth doing a PhD in AI right now?",
  "Should I invest 500K in Bitcoin at this price?",
];

export default function QuestionInput({ onSubmit, loading }: Props) {
  const [question, setQuestion] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const q = question.trim();
    if (q.length >= 2) onSubmit(q);
  };

  return (
    <div className="space-y-8">
      <div className="text-center space-y-3">
        <h2 className="text-3xl font-semibold text-white tracking-tight">
          What decision are you facing?
        </h2>
        <p className="text-zinc-500 text-sm max-w-lg mx-auto">
          Describe your question in one sentence. KPAX will assemble a team of experts
          to analyze it from multiple angles.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="relative">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g., Should I sell my apartment and move to a smaller city?"
            rows={3}
            className="w-full bg-zinc-900/50 border border-zinc-800 rounded-xl px-5 py-4 text-white placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-kpax-600/50 focus:border-kpax-700 resize-none text-base"
            disabled={loading}
          />
        </div>

        <button
          type="submit"
          disabled={loading || question.trim().length < 2}
          className="w-full bg-kpax-600 hover:bg-kpax-700 disabled:bg-zinc-800 disabled:text-zinc-600 text-white font-medium py-3 px-6 rounded-xl transition-all text-sm"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <Spinner /> Analyzing your question...
            </span>
          ) : (
            "Start Analysis"
          )}
        </button>
      </form>

      <div className="space-y-2">
        <p className="text-xs text-zinc-600 text-center">Try an example:</p>
        <div className="flex flex-wrap gap-2 justify-center">
          {EXAMPLES.map((ex) => (
            <button
              key={ex}
              onClick={() => setQuestion(ex)}
              className="text-xs text-zinc-500 hover:text-kpax-400 bg-zinc-900/50 hover:bg-zinc-800/50 border border-zinc-800/50 hover:border-zinc-700 px-3 py-1.5 rounded-lg transition-all"
            >
              {ex}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

function Spinner() {
  return (
    <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" className="opacity-25" />
      <path
        d="M4 12a8 8 0 018-8"
        stroke="currentColor"
        strokeWidth="3"
        strokeLinecap="round"
        className="opacity-75"
      />
    </svg>
  );
}
