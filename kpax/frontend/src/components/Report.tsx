import { useState } from "react";
import type { ReportData } from "../api/client";
import api from "../api/client";

interface Props {
  report: ReportData;
  sessionId: string;
  onReset: () => void;
}

export default function Report({ report, sessionId, onReset }: Props) {
  const [followUp, setFollowUp] = useState("");
  const [followUpResult, setFollowUpResult] = useState<{
    answer: string;
    additional_insights: string[];
    revised_action_items: { action: string; rationale: string; urgency: string }[];
  } | null>(null);
  const [followUpLoading, setFollowUpLoading] = useState(false);

  const handleFollowUp = async () => {
    if (!followUp.trim()) return;
    setFollowUpLoading(true);
    try {
      const res = await api.followUp(sessionId, followUp.trim());
      setFollowUpResult(res.result);
      setFollowUp("");
    } catch {
      /* ignore */
    } finally {
      setFollowUpLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Executive summary */}
      <section>
        <SectionTitle>Executive Summary</SectionTitle>
        <div className="bg-kpax-600/5 border border-kpax-600/20 rounded-xl p-5">
          <p className="text-white text-sm leading-relaxed">{report.executive_summary}</p>
        </div>
      </section>

      {/* Question reframe */}
      {report.question_reframe && (
        <section>
          <SectionTitle>A Different Way to Think About It</SectionTitle>
          <p className="text-zinc-300 text-sm">{report.question_reframe}</p>
        </section>
      )}

      {/* Pro & Con */}
      <div className="grid sm:grid-cols-2 gap-4">
        <section>
          <SectionTitle className="text-emerald-400">Supporting Arguments</SectionTitle>
          <div className="space-y-3">
            {report.pro_arguments?.map((arg, i) => (
              <ArgumentCard key={i} arg={arg} variant="pro" />
            ))}
            {(!report.pro_arguments || report.pro_arguments.length === 0) && (
              <p className="text-xs text-zinc-600">No supporting arguments found.</p>
            )}
          </div>
        </section>
        <section>
          <SectionTitle className="text-rose-400">Risks & Concerns</SectionTitle>
          <div className="space-y-3">
            {report.con_arguments?.map((arg, i) => (
              <ArgumentCard key={i} arg={arg} variant="con" />
            ))}
            {(!report.con_arguments || report.con_arguments.length === 0) && (
              <p className="text-xs text-zinc-600">No counter-arguments found.</p>
            )}
          </div>
        </section>
      </div>

      {/* Key disagreements */}
      {report.key_disagreements && report.key_disagreements.length > 0 && (
        <section>
          <SectionTitle>Where Experts Disagree</SectionTitle>
          <div className="space-y-3">
            {report.key_disagreements.map((d, i) => (
              <div
                key={i}
                className="bg-zinc-900/40 border border-zinc-800/50 rounded-xl p-4"
              >
                <p className="text-white text-sm font-medium mb-2">{d.topic}</p>
                {Array.isArray(d.positions) ? (
                  <ul className="space-y-1">
                    {d.positions.map((p, j) => (
                      <li key={j} className="text-xs text-zinc-400">
                        {p}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <div className="space-y-1">
                    {Object.entries(d.positions as Record<string, string>).map(
                      ([expert, position]) => (
                        <p key={expert} className="text-xs text-zinc-400">
                          <span className="text-zinc-500">{expert}:</span> {position}
                        </p>
                      )
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Action items */}
      {report.action_items && report.action_items.length > 0 && (
        <section>
          <SectionTitle>Recommended Actions</SectionTitle>
          <div className="space-y-2">
            {report.action_items.map((item, i) => (
              <div
                key={i}
                className="flex gap-3 bg-zinc-900/40 border border-zinc-800/50 rounded-xl p-4"
              >
                <UrgencyBadge urgency={item.urgency} />
                <div className="flex-1 space-y-1">
                  <p className="text-white text-sm">{item.action}</p>
                  <p className="text-xs text-zinc-500">{item.rationale}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Blind spots */}
      {report.blind_spots && report.blind_spots.length > 0 && (
        <section>
          <SectionTitle>Potential Blind Spots</SectionTitle>
          <ul className="space-y-1">
            {report.blind_spots.map((s, i) => (
              <li key={i} className="text-sm text-zinc-400 flex items-start gap-2">
                <span className="text-amber-500 mt-0.5 text-xs">!</span>
                {s}
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Follow-up questions */}
      {report.follow_up_questions && report.follow_up_questions.length > 0 && (
        <section>
          <SectionTitle>Questions Worth Exploring</SectionTitle>
          <div className="space-y-1.5">
            {report.follow_up_questions.map((q, i) => (
              <button
                key={i}
                onClick={() => setFollowUp(q)}
                className="block text-left text-sm text-kpax-400 hover:text-kpax-300 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </section>
      )}

      {/* Follow-up input */}
      <section className="bg-zinc-900/30 border border-zinc-800/50 rounded-xl p-5 space-y-3">
        <p className="text-sm text-zinc-400">
          Want to dig deeper? Ask a follow-up question.
        </p>
        <div className="flex gap-2">
          <input
            value={followUp}
            onChange={(e) => setFollowUp(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleFollowUp()}
            placeholder="Ask anything about this analysis..."
            className="flex-1 bg-zinc-900/50 border border-zinc-800 rounded-lg px-4 py-2.5 text-white text-sm placeholder-zinc-600 focus:outline-none focus:ring-2 focus:ring-kpax-600/50"
          />
          <button
            onClick={handleFollowUp}
            disabled={followUpLoading || !followUp.trim()}
            className="px-5 py-2.5 bg-kpax-600 hover:bg-kpax-700 disabled:bg-zinc-800 disabled:text-zinc-600 text-white text-sm rounded-lg transition-all"
          >
            {followUpLoading ? "..." : "Ask"}
          </button>
        </div>

        {followUpResult && (
          <div className="mt-4 space-y-3 bg-zinc-900/50 border border-zinc-800/30 rounded-xl p-4">
            <p className="text-sm text-zinc-300 whitespace-pre-wrap leading-relaxed">
              {followUpResult.answer}
            </p>
            {followUpResult.additional_insights?.length > 0 && (
              <div>
                <p className="text-xs text-zinc-500 mb-1">Additional insights:</p>
                <ul className="space-y-1">
                  {followUpResult.additional_insights.map((ins, i) => (
                    <li key={i} className="text-xs text-zinc-400">
                      {ins}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
      </section>

      {/* Actions */}
      <div className="flex gap-3 pt-4">
        <button
          onClick={onReset}
          className="flex-1 bg-zinc-800 hover:bg-zinc-700 text-zinc-300 font-medium py-3 px-6 rounded-xl transition-all text-sm"
        >
          New Analysis
        </button>
      </div>
    </div>
  );
}

function SectionTitle({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <h3
      className={`text-xs font-mono uppercase tracking-wider mb-3 ${className || "text-zinc-500"}`}
    >
      {children}
    </h3>
  );
}

function ArgumentCard({
  arg,
  variant,
}: {
  arg: { point: string; evidence: string; expert: string };
  variant: "pro" | "con";
}) {
  const borderCls =
    variant === "pro" ? "border-emerald-500/20" : "border-rose-500/20";
  return (
    <div
      className={`bg-zinc-900/40 border ${borderCls} rounded-xl p-4 space-y-1.5`}
    >
      <p className="text-white text-sm">{arg.point}</p>
      {arg.evidence && (
        <p className="text-xs text-zinc-500">{arg.evidence}</p>
      )}
      {arg.expert && (
        <p className="text-[10px] text-zinc-600 font-mono">
          — {arg.expert}
        </p>
      )}
    </div>
  );
}

function UrgencyBadge({ urgency }: { urgency: string }) {
  const cls =
    urgency === "high"
      ? "bg-rose-500/10 text-rose-400 border-rose-500/30"
      : urgency === "medium"
      ? "bg-amber-500/10 text-amber-400 border-amber-500/30"
      : "bg-zinc-500/10 text-zinc-400 border-zinc-500/30";

  return (
    <span
      className={`text-[10px] px-2 py-0.5 rounded-full border self-start ${cls}`}
    >
      {urgency}
    </span>
  );
}
