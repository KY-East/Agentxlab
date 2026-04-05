import { useState, useEffect, useRef, useCallback } from "react";
import { useTranslation } from "react-i18next";
import i18n from "../i18n";
import { useParams, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import { Loader2, Play, Square, ArrowLeft, BookOpen } from "lucide-react";
import { api } from "../api/client";
import type { Debate, DebateAgent, DebateMessage, DraftBrief, Spark, SparkStats } from "../types";
import PaperChat from "../components/PaperChat/PaperChat";

const PERSONA_META: Record<string, { label: string; color: string }> = {
  pioneer: { label: "PIONEER", color: "text-amber-400" },
  rigorous: { label: "RIGOROUS", color: "text-blue-400" },
  pragmatic: { label: "PRAGMATIC", color: "text-emerald-400" },
  skeptic: { label: "SKEPTIC", color: "text-red-400" },
  moderator: { label: "MOD", color: "text-cyan-400" },
};

const RANK_META: Record<string, { label: string }> = {
  professor: { label: "Prof." },
  associate: { label: "Assoc." },
  assistant: { label: "Asst." },
};

const AGENT_BORDER_COLORS = [
  "border-l-amber-500",
  "border-l-blue-500",
  "border-l-emerald-500",
  "border-l-red-500",
  "border-l-cyan-500",
  "border-l-pink-500",
];

const NOVELTY_TYPE_META: Record<string, { label: string; color: string }> = {
  analogy: { label: "ANALOGY", color: "text-amber-400" },
  transfer: { label: "TRANSFER", color: "text-blue-400" },
  fusion: { label: "FUSION", color: "text-emerald-400" },
  inversion: { label: "INVERSION", color: "text-pink-400" },
};

export default function DebateSession() {
  const { t } = useTranslation();
  const { debateId } = useParams<{ debateId: string }>();
  const navigate = useNavigate();

  const [debate, setDebate] = useState<Debate | null>(null);
  const [loading, setLoading] = useState(true);
  const [roundLoading, setRoundLoading] = useState(false);
  const [summarizing, setSummarizing] = useState(false);
  const [autoRunning, setAutoRunning] = useState(false);
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);
  const [roundProgress, setRoundProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);


  const [showPaperChat, setShowPaperChat] = useState(false);
  const [existingDrafts, setExistingDrafts] = useState<DraftBrief[]>([]);
  const [sparks, setSparks] = useState<Spark[]>([]);
  const [sparkStats, setSparkStats] = useState<SparkStats | null>(null);

  const load = useCallback(async () => {
    if (!debateId) return;
    setLoading(true);
    setDebate(null);
    setError(null);
    try {
      const d = await api.getDebate(Number(debateId));
      setDebate(d);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("debateSession.loadFailed"));
    } finally {
      setLoading(false);
    }
  }, [debateId, t]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [debate?.messages.length]);

  useEffect(() => {
    if (debate?.status !== "completed") {
      setExistingDrafts([]);
      setSparks([]);
      setSparkStats(null);
      return;
    }
    let stale = false;
    api.listDrafts(debate.id).then((drafts) => {
      if (!stale) setExistingDrafts(drafts);
    }).catch(() => {});
    api.listSparks({ debate_id: debate.id, limit: 20 }).then((s) => {
      if (!stale) setSparks(s);
    }).catch(() => {});
    api.getSparkStats(debate.id).then((s) => {
      if (!stale) setSparkStats(s);
    }).catch(() => {});
    return () => { stale = true; };
  }, [debate?.id, debate?.status]);

  const runOneRoundSSE = async (dId: number): Promise<boolean> => {
    const resp = await api.runRoundStream(dId);
    if (!resp.ok) {
      const text = await resp.text();
      throw new Error(text || `HTTP ${resp.status}`);
    }
    const reader = resp.body?.getReader();
    if (!reader) throw new Error("No stream");
    const decoder = new TextDecoder();
    let buffer = "";
    let gotMessages = false;

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n\n");
      buffer = lines.pop() || "";

      for (const chunk of lines) {
        const line = chunk.replace(/^data:\s*/, "").trim();
        if (!line) continue;
        try {
          const data = JSON.parse(line);
          if (data.error) throw new Error(data.error);
          if (data.done) {
            setThinkingAgent(null);
            return true;
          }
          gotMessages = true;
          setThinkingAgent(null);
          const msg: DebateMessage = {
            id: data.id,
            agent_id: data.agent_id,
            role: data.role,
            content: data.content,
            round_number: data.round_number,
            created_at: data.created_at || new Date().toISOString(),
          };
          setDebate((prev) =>
            prev ? { ...prev, messages: [...prev.messages, msg] } : prev
          );
          const nextIdx = (data.index || 0) + 1;
          const total = data.total || 0;
          if (nextIdx <= total) {
            setThinkingAgent(`Agent ${nextIdx}/${total}`);
          }
          setTimeout(() => {
            scrollRef.current?.scrollTo({ top: scrollRef.current!.scrollHeight, behavior: "smooth" });
          }, 50);
        } catch {}
      }
    }
    return gotMessages;
  };

  const handleNextRound = async () => {
    if (!debate) return;
    setRoundLoading(true);
    setError(null);
    setThinkingAgent("...");
    try {
      await runOneRoundSSE(debate.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("debateSession.generateFailed"));
    } finally {
      setRoundLoading(false);
      setThinkingAgent(null);
    }
  };

  const handleAutoRun = async () => {
    if (!debate) return;
    const totalRounds = 3;
    setAutoRunning(true);
    setError(null);
    try {
      for (let r = 1; r <= totalRounds; r++) {
        setRoundProgress(t("debateSession.roundProgress", { current: r, total: totalRounds }).toUpperCase());
        setRoundLoading(true);
        setThinkingAgent("...");
        const ok = await runOneRoundSSE(debate.id);
        setRoundLoading(false);
        if (!ok) break;
      }
      setRoundProgress(null);
      setSummarizing(true);
      const updated = await api.summarizeDebate(debate.id);
      setDebate(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("debateSession.generateFailed"));
    } finally {
      setAutoRunning(false);
      setRoundLoading(false);
      setSummarizing(false);
      setThinkingAgent(null);
      setRoundProgress(null);
    }
  };

  const handleSummarize = async () => {
    if (!debate) return;
    setSummarizing(true);
    try {
      const updated = await api.summarizeDebate(debate.id);
      setError(null);
      setDebate(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("debateSession.summaryFailed"));
    } finally {
      setSummarizing(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <span className="font-mono text-xs text-neutral-600 animate-blink">[LOADING...]</span>
      </div>
    );
  }

  if (error && !debate) {
    return (
      <div className="flex items-center justify-center h-full text-center p-8">
        <div>
          <p className="font-mono text-xs text-red-500 mb-2">{error}</p>
          <button
            onClick={() => navigate("/debate")}
            className="font-mono text-xs text-neutral-500 hover:text-white underline transition-colors"
          >
            {t("debateSession.back").toUpperCase()}
          </button>
        </div>
      </div>
    );
  }

  if (!debate) return null;

  const agentMap = new Map(debate.agents.map((a) => [a.id, a]));
  const maxRound = debate.messages.length > 0
    ? Math.max(...debate.messages.map((m) => m.round_number))
    : 0;

  const messagesByRound = new Map<number, DebateMessage[]>();
  for (const m of debate.messages) {
    const arr = messagesByRound.get(m.round_number) || [];
    arr.push(m);
    messagesByRound.set(m.round_number, arr);
  }

  return (
    <div className="flex h-full">
      {/* Agent sidebar */}
      <aside className="w-52 shrink-0 border-r-2 border-neutral-800 flex flex-col">
        <div className="px-3 py-2.5 border-b border-neutral-800">
          <button
            onClick={() => navigate("/debate")}
            className="flex items-center gap-1 font-mono text-[10px] text-neutral-600 hover:text-white transition-colors mb-2 uppercase tracking-wider"
          >
            <ArrowLeft size={10} />
            {t("debateSession.back")}
          </button>
          <div className="font-mono text-[10px] uppercase tracking-wider text-neutral-500">
            {debate.mode === "free"
              ? t("debateSession.freeDiscussion").toUpperCase()
              : t("debateSession.structuredDebate").toUpperCase()}
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-0.5">
          <p className="font-mono text-[9px] text-neutral-700 uppercase tracking-[0.15em] mb-2">
            {t("debateSession.agentRoster")}
          </p>
          {(() => {
            const groups = new Map<number | null, typeof debate.agents>();
            for (const a of debate.agents) {
              const key = a.discipline_id;
              if (!groups.has(key)) groups.set(key, []);
              groups.get(key)!.push(a);
            }
            return [...groups.entries()].map(([discId, members]) => {
              const disc = discId != null
                ? debate.disciplines.find((d) => d.id === discId)
                : null;
              return (
                <div key={discId ?? "mod"}>
                  {disc && (
                    <p className="font-mono text-[9px] text-neutral-600 uppercase tracking-wider pl-1 mt-2 mb-1 truncate">
                      {disc.name_en}
                    </p>
                  )}
                  {members.map((agent) => (
                    <AgentRow key={agent.id} agent={agent} colorIdx={debate.agents.indexOf(agent)} />
                  ))}
                </div>
              );
            });
          })()}
        </div>

        {debate.proposition && (
          <div className="p-3 border-t border-neutral-800">
            <p className="font-mono text-[9px] text-neutral-700 uppercase tracking-[0.15em] mb-1">
              {t("debateSession.proposition")}
            </p>
            <p className="text-xs text-neutral-400 leading-relaxed">
              {debate.proposition}
            </p>
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <div className="px-5 py-2.5 border-b-2 border-neutral-800 flex items-center gap-3">
          <h1 className="font-mono text-sm font-bold text-white truncate flex-1 uppercase tracking-wide">
            {debate.title}
          </h1>
          <div className="flex items-center gap-1.5">
            {debate.disciplines.map((d) => (
              <span
                key={d.id}
                className="font-mono text-[9px] px-2 py-0.5 bg-neutral-900 text-neutral-400 border border-neutral-800 uppercase tracking-wider"
              >
                {i18n.language?.startsWith("zh") ? (d.name_zh || d.name_en) : d.name_en}
              </span>
            ))}
          </div>
          <span
            className={`font-mono text-[9px] px-2 py-0.5 uppercase tracking-wider ${
              debate.status === "completed"
                ? "text-green-400 border border-green-400/30"
                : "text-cyan-400 border border-cyan-400/30"
            }`}
          >
            {debate.status === "completed"
              ? t("debate.statusCompleted")
              : `R${maxRound}`}
          </span>
        </div>

        {/* Messages */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-5 py-4 space-y-0">
          {debate.messages.length === 0 && !roundLoading && !autoRunning && (
            <div className="text-center py-20">
              <p className="font-mono text-xs text-neutral-600">
                {t("debateSession.emptyHint")}
              </p>
            </div>
          )}

          <AnimatePresence mode="popLayout">
            {[...messagesByRound.entries()].map(([round, msgs]) => (
              <div key={round}>
                <div className="flex items-center gap-3 py-3">
                  <div className="h-[2px] flex-1 bg-neutral-800" />
                  <span className="font-mono text-[10px] text-neutral-600 uppercase tracking-[0.2em]">
                    {t("debateSession.roundLabel", { n: round }).toUpperCase()}
                  </span>
                  <div className="h-[2px] flex-1 bg-neutral-800" />
                </div>
                <div className="space-y-0">
                  {msgs.map((msg) => (
                    <MessageBlock
                      key={msg.id}
                      message={msg}
                      agent={msg.agent_id ? agentMap.get(msg.agent_id) : undefined}
                      agentIndex={msg.agent_id ? debate.agents.findIndex((a) => a.id === msg.agent_id) : -1}
                    />
                  ))}
                </div>
              </div>
            ))}
          </AnimatePresence>

          {(roundLoading || autoRunning) && (
            <div className="py-3 px-1">
              <span className="font-mono text-xs text-cyan-400 animate-blink">
                {roundProgress && <span className="text-neutral-500 mr-2">{roundProgress}</span>}
                {summarizing
                  ? `[${t("debateSession.thinking")}]`
                  : thinkingAgent
                    ? `[${thinkingAgent} SPEAKING...]`
                    : "[THINKING...]"}
              </span>
            </div>
          )}

          {/* Summary */}
          {debate.status === "completed" && debate.summary_consensus && (
            <SummaryBlock debate={debate} />
          )}

          {/* Sparks */}
          {debate.status === "completed" && (sparks.length > 0 || sparkStats) && (
            <SparkBlock sparks={sparks} stats={sparkStats} agents={debate.agents} />
          )}

          {/* Existing drafts */}
          {existingDrafts.length > 0 && (
            <div className="pt-4 space-y-1">
              <p className="font-mono text-[9px] text-neutral-700 uppercase tracking-[0.15em] flex items-center gap-1">
                <BookOpen size={10} />
                {t("debateSession.existingPapers")}
              </p>
              {existingDrafts.map((d) => (
                <button
                  key={d.id}
                  onClick={() => navigate(`/paper/${d.id}`)}
                  className="w-full text-left py-2 px-3 border-l-2 border-neutral-800 hover:border-cyan-400 hover:bg-neutral-900/50 transition-colors"
                >
                  <p className="text-xs text-neutral-300 truncate">{d.title}</p>
                  <p className="font-mono text-[9px] text-neutral-600 mt-0.5">
                    {d.direction ? d.direction : ""} -- {d.status}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Action bar */}
        <div className="px-5 py-3 border-t-2 border-neutral-800 flex items-center gap-3">
          {error && (
            <p className="font-mono text-[10px] text-red-500 flex-1">{error}</p>
          )}
          <div className="flex-1" />
          {debate.status === "active" && (
            <>
              {debate.messages.length === 0 ? (
                <button
                  onClick={handleAutoRun}
                  disabled={autoRunning}
                  className="flex items-center gap-2 px-5 py-2 bg-cyan-400 text-black font-mono text-xs font-bold uppercase tracking-wider hover:bg-cyan-300 disabled:opacity-40 transition-colors"
                >
                  {autoRunning ? (
                    <Loader2 size={12} className="animate-spin" />
                  ) : (
                    <Play size={12} />
                  )}
                  {t("debateSession.startDebateThreeRounds").toUpperCase()}
                </button>
              ) : (
                <button
                  onClick={handleNextRound}
                  disabled={roundLoading || summarizing || autoRunning}
                  className="flex items-center gap-2 px-4 py-2 bg-cyan-400 text-black font-mono text-xs font-bold uppercase tracking-wider hover:bg-cyan-300 disabled:opacity-40 transition-colors"
                >
                  {roundLoading ? (
                    <Loader2 size={12} className="animate-spin" />
                  ) : (
                    <Play size={12} />
                  )}
                  {t("debateSession.nextRound").toUpperCase()}
                </button>
              )}
              {debate.messages.length > 0 && !autoRunning && (
                <button
                  onClick={handleSummarize}
                  disabled={roundLoading || summarizing || autoRunning}
                  className="flex items-center gap-2 px-4 py-2 border border-neutral-700 text-neutral-300 font-mono text-xs uppercase tracking-wider hover:border-white hover:text-white disabled:opacity-40 transition-colors"
                >
                  {summarizing ? (
                    <Loader2 size={12} className="animate-spin" />
                  ) : (
                    <Square size={12} />
                  )}
                  {t("debateSession.endDebate").toUpperCase()}
                </button>
              )}
            </>
          )}
          {debate.status === "completed" && !showPaperChat && (
            <button
              onClick={() => setShowPaperChat(true)}
              className="flex items-center gap-2 px-4 py-2 bg-cyan-400 text-black font-mono text-xs font-bold uppercase tracking-wider hover:bg-cyan-300 transition-colors"
            >
              {t("debateSession.generateOutline").toUpperCase()}
            </button>
          )}
        </div>
      </main>

      {showPaperChat && debate.status === "completed" && (
        <div className="h-[45vh] border-t-2 border-cyan-400/30">
          <PaperChat debateId={debate.id} />
        </div>
      )}
    </div>
  );
}

function AgentRow({ agent, colorIdx }: { agent: DebateAgent; colorIdx: number }) {
  const { t } = useTranslation();
  const meta = PERSONA_META[agent.persona] || PERSONA_META.moderator;
  const rank = agent.rank || "professor";
  const rankMeta = RANK_META[rank] || RANK_META.professor;
  const borderColor = AGENT_BORDER_COLORS[colorIdx % AGENT_BORDER_COLORS.length];

  return (
    <div className={`pl-2 py-1.5 border-l-2 ${borderColor} flex items-center gap-2`}>
      <div className="flex-1 min-w-0">
        <p className="font-mono text-[11px] text-neutral-300 truncate">{agent.agent_name}</p>
        <div className="flex items-center gap-1 mt-0.5 flex-wrap">
          {agent.persona !== "moderator" && (
            <span className="font-mono text-[8px] text-neutral-600 uppercase">{rankMeta.label}</span>
          )}
          <span className={`font-mono text-[8px] uppercase ${meta.color}`}>{meta.label}</span>
          {agent.stance && agent.stance !== "moderator" && (
            <span
              className={`font-mono text-[8px] uppercase ${
                agent.stance === "advocate" ? "text-green-400" : "text-red-400"
              }`}
            >
              {agent.stance === "advocate" ? t("debateSession.advocate") : t("debateSession.challenger")}
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

function MessageBlock({
  message,
  agent,
  agentIndex,
}: {
  message: DebateMessage;
  agent?: DebateAgent;
  agentIndex: number;
}) {
  const { t } = useTranslation();
  const meta = agent
    ? PERSONA_META[agent.persona] || PERSONA_META.moderator
    : PERSONA_META.moderator;
  const borderColor = agentIndex >= 0
    ? AGENT_BORDER_COLORS[agentIndex % AGENT_BORDER_COLORS.length]
    : "border-l-neutral-800";

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2 }}
      className={`py-3 pl-3 border-l-2 ${borderColor}`}
    >
      {agent && (
        <div className="flex items-center gap-2 mb-1.5">
          <span className="font-mono text-[11px] font-bold text-neutral-300">
            {agent.agent_name}
          </span>
          <span className={`font-mono text-[9px] uppercase ${meta.color}`}>{meta.label}</span>
          {agent.stance && agent.stance !== "moderator" && (
            <span
              className={`font-mono text-[9px] uppercase ${
                agent.stance === "advocate" ? "text-green-400" : "text-red-400"
              }`}
            >
              {agent.stance === "advocate" ? t("debateSession.advocate") : t("debateSession.challenger")}
            </span>
          )}
        </div>
      )}
      <div className="text-sm text-neutral-400 leading-relaxed whitespace-pre-wrap">
        {message.content}
      </div>
    </motion.div>
  );
}

function SummaryBlock({ debate }: { debate: Debate }) {
  const { t } = useTranslation();
  const sections = [
    { id: "consensus", titleKey: "debateSession.consensus", color: "border-green-500", content: debate.summary_consensus },
    { id: "disagreements", titleKey: "debateSession.disagreements", color: "border-red-500", content: debate.summary_disagreements },
    { id: "openQuestions", titleKey: "debateSession.openQuestions", color: "border-yellow-500", content: debate.summary_open_questions },
    { id: "directions", titleKey: "debateSession.directions", color: "border-cyan-400", content: debate.summary_directions },
  ].filter((s) => s.content);

  return (
    <div className="mt-6 space-y-3">
      <div className="flex items-center gap-3 py-2">
        <div className="h-[2px] flex-1 bg-cyan-400/30" />
        <span className="font-mono text-[10px] text-cyan-400 uppercase tracking-[0.2em]">
          {t("debateSession.summary").toUpperCase()}
        </span>
        <div className="h-[2px] flex-1 bg-cyan-400/30" />
      </div>
      {sections.map((s) => (
        <div key={s.id} className={`pl-3 border-l-2 ${s.color}`}>
          <h4 className="font-mono text-[10px] font-bold text-neutral-500 uppercase tracking-wider mb-1">
            {t(s.titleKey).toUpperCase()}
          </h4>
          <p className="text-sm text-neutral-400 leading-relaxed whitespace-pre-wrap">
            {s.content}
          </p>
        </div>
      ))}
    </div>
  );
}

function SparkBlock({
  sparks,
  stats,
  agents,
}: {
  sparks: Spark[];
  stats: SparkStats | null;
  agents: DebateAgent[];
}) {
  const { t } = useTranslation();
  const agentMap = new Map(agents.map((a) => [a.id, a]));

  return (
    <div className="mt-4 space-y-2">
      <div className="flex items-center gap-3 py-2">
        <div className="h-[2px] flex-1 bg-yellow-500/30" />
        <span className="font-mono text-[10px] text-yellow-500 uppercase tracking-[0.2em]">
          {t("debateSession.sparks").toUpperCase()}
        </span>
        <div className="h-[2px] flex-1 bg-yellow-500/30" />
      </div>

      {stats && (
        <div className="flex items-center gap-3 font-mono text-[10px] text-neutral-600">
          <span>{t("debateSession.sparkCount", { count: stats.total })}</span>
          <span>{t("debateSession.avgNovelty", { score: (stats.avg_score * 100).toFixed(0) })}</span>
          {stats.total > 0 && Object.entries(stats.by_type).map(([type, count]) => {
            const meta = NOVELTY_TYPE_META[type] || { label: type.toUpperCase(), color: "text-neutral-500" };
            return (
              <span key={type} className={meta.color}>{meta.label} {count}</span>
            );
          })}
        </div>
      )}

      {sparks.length > 0 && (
        <div className="space-y-0">
          {sparks.map((spark) => {
            const agent = spark.agent_id ? agentMap.get(spark.agent_id) : undefined;
            const typeMeta = NOVELTY_TYPE_META[spark.novelty_type] || { label: "SPARK", color: "text-neutral-500" };
            return (
              <div
                key={spark.id}
                className="py-2 pl-3 border-l-2 border-yellow-500/30"
              >
                <div className="flex items-center gap-2 mb-1">
                  <span className={`font-mono text-[9px] uppercase ${typeMeta.color}`}>
                    {typeMeta.label}
                  </span>
                  <span className="font-mono text-[9px] text-yellow-500/60">
                    {(spark.novelty_score * 100).toFixed(0)}%
                  </span>
                  {agent && (
                    <span className="font-mono text-[9px] text-neutral-700">
                      {agent.agent_name}
                    </span>
                  )}
                </div>
                <p className="text-xs text-neutral-400 leading-relaxed">
                  {spark.content}
                </p>
                {spark.reasoning && (
                  <p className="font-mono text-[10px] text-neutral-600 mt-1">
                    {spark.reasoning}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      {sparks.length === 0 && (
        <p className="font-mono text-[10px] text-neutral-700">{t("debateSession.noSparks")}</p>
      )}
    </div>
  );
}
