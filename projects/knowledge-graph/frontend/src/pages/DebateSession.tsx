import { useState, useEffect, useRef, useCallback, type ReactNode } from "react";
import { useTranslation } from "react-i18next";
import i18n from "../i18n";
import { useParams, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import {
  Loader2,
  Play,
  Square,
  ArrowLeft,
  BookOpen,
  Share2,
  FlaskConical,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { api } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import type { Debate, DebateAgent, DebateMessage, DraftBrief, Spark, SparkStats } from "../types";
import PaperChat from "../components/PaperChat/PaperChat";
import ModelSelector from "../components/ModelSelector";

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
  const { user, setShowAuthModal } = useAuth();

  const [debate, setDebate] = useState<Debate | null>(null);
  const [loading, setLoading] = useState(true);
  const [roundLoading, setRoundLoading] = useState(false);
  const [summarizing, setSummarizing] = useState(false);
  const [autoRunning, setAutoRunning] = useState(false);
  const [thinkingAgent, setThinkingAgent] = useState<string | null>(null);
  const [roundProgress, setRoundProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const autoRunRef = useRef(false);


  const [showPaperChat, setShowPaperChat] = useState(false);
  const [existingDrafts, setExistingDrafts] = useState<DraftBrief[]>([]);
  const [sparks, setSparks] = useState<Spark[]>([]);
  const [sparkStats, setSparkStats] = useState<SparkStats | null>(null);

  const [sharedPostId, setSharedPostId] = useState<number | null>(null);
  const [sharing, setSharing] = useState(false);
  const [experimentRequested, setExperimentRequested] = useState<Set<number>>(new Set());

  const [sidebarW, setSidebarW] = useState(220);
  const dragging = useRef(false);
  const startX = useRef(0);
  const startW = useRef(220);

  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      if (!dragging.current) return;
      const delta = e.clientX - startX.current;
      setSidebarW(Math.min(480, Math.max(160, startW.current + delta)));
    };
    const onUp = () => { dragging.current = false; document.body.style.cursor = ""; document.body.style.userSelect = ""; };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => { window.removeEventListener("mousemove", onMove); window.removeEventListener("mouseup", onUp); };
  }, []);

  const STORAGE_KEY = `debate_autorun_${debateId}`;

  const saveAutoRunState = useCallback((targetRounds: number) => {
    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ debateId, targetRounds, ts: Date.now() }));
    } catch {}
  }, [STORAGE_KEY, debateId]);

  const clearAutoRunState = useCallback(() => {
    try { sessionStorage.removeItem(STORAGE_KEY); } catch {}
  }, [STORAGE_KEY]);

  const getSavedAutoRun = useCallback((): { debateId: string; targetRounds: number; ts: number } | null => {
    try {
      const raw = sessionStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      const parsed = JSON.parse(raw);
      if (Date.now() - parsed.ts > 30 * 60 * 1000) {
        sessionStorage.removeItem(STORAGE_KEY);
        return null;
      }
      return parsed;
    } catch { return null; }
  }, [STORAGE_KEY]);

  const load = useCallback(async () => {
    if (!debateId) return;
    setLoading(true);
    setDebate(null);
    setError(null);
    try {
      const d = await api.getDebate(Number(debateId));
      setDebate(d);
      if (d.status === "completed") {
        clearAutoRunState();
        api.listForumPosts({ debate_id: d.id, post_type: "debate_summary", limit: 1 })
          .then((posts) => { if (posts.length > 0) setSharedPostId(posts[0].id); })
          .catch(() => {});
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : t("debateSession.loadFailed"));
    } finally {
      setLoading(false);
    }
  }, [debateId, t, clearAutoRunState]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (!autoRunning) return;
    const handler = (e: BeforeUnloadEvent) => {
      e.preventDefault();
      e.returnValue = "";
    };
    window.addEventListener("beforeunload", handler);
    return () => window.removeEventListener("beforeunload", handler);
  }, [autoRunning]);

  useEffect(() => {
    if (!debate || debate.status !== "active" || autoRunning || roundLoading) return;
    const saved = getSavedAutoRun();
    if (!saved) return;
    const maxRoundSoFar = debate.messages.length > 0
      ? Math.max(...debate.messages.map((m) => m.round_number))
      : 0;
    const remaining = Math.max(0, saved.targetRounds - maxRoundSoFar);
    if (remaining > 0) {
      handleAutoRun(saved.targetRounds);
    } else if (maxRoundSoFar >= saved.targetRounds) {
      clearAutoRunState();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debate?.id, loading]);

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

  const handleAutoRun = async (targetRounds = 3) => {
    if (!debate || autoRunRef.current) return;
    const currentRound = debate.messages.length > 0
      ? Math.max(...debate.messages.map((m) => m.round_number))
      : 0;
    const remaining = Math.max(0, targetRounds - currentRound);
    if (remaining === 0) {
      clearAutoRunState();
      setSummarizing(true);
      try {
        const updated = await api.summarizeDebate(debate.id);
        setDebate(updated);
      } catch (err) {
        setError(err instanceof Error ? err.message : t("debateSession.generateFailed"));
      } finally {
        setSummarizing(false);
      }
      return;
    }
    autoRunRef.current = true;
    setAutoRunning(true);
    setError(null);
    saveAutoRunState(targetRounds);
    try {
      for (let r = 1; r <= remaining; r++) {
        const roundLabel = currentRound + r;
        setRoundProgress(t("debateSession.roundProgress", { current: roundLabel, total: targetRounds }).toUpperCase());
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
      clearAutoRunState();
    } catch (err) {
      setError(err instanceof Error ? err.message : t("debateSession.generateFailed"));
    } finally {
      autoRunRef.current = false;
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

  const handleShareToForum = async () => {
    if (!debate) return;
    if (!user) { setShowAuthModal(true); return; }
    setSharing(true);
    try {
      const res = await api.shareDebateToForum(debate.id);
      setSharedPostId(res.post_id);
    } catch {
      setError("Failed to share to community");
    } finally {
      setSharing(false);
    }
  };

  const handleRequestExperiment = async (sparkId: number) => {
    if (!debate) return;
    if (!user) { setShowAuthModal(true); return; }
    try {
      const res = await api.requestExperiment(debate.id, sparkId);
      setExperimentRequested((prev) => new Set(prev).add(sparkId));
      navigate(`/forum/${res.post_id}`);
    } catch {
      setError("Failed to create experiment request");
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
      <aside style={{ width: sidebarW }} className="shrink-0 border-r-2 border-neutral-800 flex flex-col relative">
        <div className="px-3 py-2.5 border-b border-neutral-800">
          <button
            onClick={() => navigate("/debate")}
            className="flex items-center gap-2 w-full px-2 py-2 font-mono text-xs text-neutral-300 hover:text-white hover:bg-neutral-800 transition-colors mb-2 uppercase tracking-wider border border-neutral-800 hover:border-neutral-600"
          >
            <ArrowLeft size={14} />
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
                    <p className="font-mono text-[9px] text-neutral-600 uppercase tracking-wider pl-1 mt-2 mb-1 break-words">
                      {i18n.language?.startsWith("zh") ? (disc.name_zh || disc.name_en) : disc.name_en}
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

      {/* Resize handle */}
      <div
        onMouseDown={(e) => {
          dragging.current = true;
          startX.current = e.clientX;
          startW.current = sidebarW;
          document.body.style.cursor = "col-resize";
          document.body.style.userSelect = "none";
        }}
        className="w-1 shrink-0 cursor-col-resize hover:bg-cyan-400/30 active:bg-cyan-400/50 transition-colors"
      />

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
          <ModelSelector />
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

          {/* Incomplete debate hint */}
          {debate.status === "active" && debate.messages.length > 0 && !autoRunning && !roundLoading && (
            <div className="mx-4 my-3 px-4 py-3 border border-amber-500/30 bg-amber-500/5">
              <p className="font-mono text-xs text-amber-400">
                {(() => {
                  const cur = Math.max(...debate.messages.map((m) => m.round_number));
                  const rem = Math.max(0, 3 - cur);
                  return i18n.language?.startsWith("zh")
                    ? `辩论进行中 — 已完成 ${cur} 轮${rem > 0 ? `，还剩 ${rem} 轮` : "，可生成总结"}。点击下方按钮继续。`
                    : `Debate in progress — ${cur} round${cur > 1 ? "s" : ""} completed${rem > 0 ? `, ${rem} remaining` : ", ready to summarize"}. Click below to continue.`;
                })()}
              </p>
            </div>
          )}

          {/* Summary */}
          {debate.status === "completed" && debate.summary_consensus && (
            <SummaryBlock debate={debate} />
          )}

          {/* Sparks */}
          {debate.status === "completed" && (sparks.length > 0 || sparkStats) && (
            <SparkBlock
              sparks={sparks}
              stats={sparkStats}
              agents={debate.agents}
              experimentRequested={experimentRequested}
              onRequestExperiment={handleRequestExperiment}
            />
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
          <button
            onClick={() => navigate("/debate")}
            className="flex items-center gap-1.5 px-3 py-2 border border-neutral-700 text-neutral-400 hover:text-white hover:border-neutral-500 font-mono text-xs uppercase tracking-wider transition-colors"
          >
            <ArrowLeft size={12} />
            {t("debateSession.back")}
          </button>
          {error && (
            <p className="font-mono text-[10px] text-red-500 flex-1">{error}</p>
          )}
          <div className="flex-1" />
          {debate.status === "active" && (
            <>
              {debate.messages.length === 0 ? (
                <button
                  onClick={() => handleAutoRun(3)}
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
                <>
                  <button
                    onClick={() => handleAutoRun(3)}
                    disabled={roundLoading || summarizing || autoRunning}
                    className="flex items-center gap-2 px-4 py-2 bg-cyan-400 text-black font-mono text-xs font-bold uppercase tracking-wider hover:bg-cyan-300 disabled:opacity-40 transition-colors"
                  >
                    {autoRunning ? (
                      <Loader2 size={12} className="animate-spin" />
                    ) : (
                      <Play size={12} />
                    )}
                    {(() => {
                      const cur = Math.max(...debate.messages.map((m) => m.round_number));
                      const rem = Math.max(0, 3 - cur);
                      return rem > 0
                        ? (i18n.language?.startsWith("zh") ? `继续 (剩${rem}轮+总结)` : `CONTINUE (${rem} ROUNDS + SUMMARY)`)
                        : (i18n.language?.startsWith("zh") ? "生成总结" : "SUMMARIZE");
                    })()}
                  </button>
                  <button
                    onClick={handleNextRound}
                    disabled={roundLoading || summarizing || autoRunning}
                    className="flex items-center gap-2 px-4 py-2 border border-neutral-700 text-neutral-400 hover:text-white hover:border-cyan-400 font-mono text-xs font-bold uppercase tracking-wider transition-colors disabled:opacity-40"
                  >
                    {roundLoading ? (
                      <Loader2 size={12} className="animate-spin" />
                    ) : (
                      <Play size={12} />
                    )}
                    {t("debateSession.nextRound").toUpperCase()}
                  </button>
                </>
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
          {debate.status === "completed" && (
            <>
              {!showPaperChat && (
                <button
                  onClick={() => setShowPaperChat(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-cyan-400 text-black font-mono text-xs font-bold uppercase tracking-wider hover:bg-cyan-300 transition-colors"
                >
                  {t("debateSession.generateOutline").toUpperCase()}
                </button>
              )}
              {sharedPostId ? (
                <button
                  onClick={() => navigate(`/forum/${sharedPostId}`)}
                  className="flex items-center gap-2 px-4 py-2 border border-green-500/50 text-green-400 font-mono text-xs uppercase tracking-wider hover:border-green-400 transition-colors"
                >
                  <Share2 size={12} />
                  {t("debateSession.viewPost")}
                </button>
              ) : (
                <button
                  onClick={handleShareToForum}
                  disabled={sharing}
                  className="flex items-center gap-2 px-4 py-2 border border-neutral-700 text-neutral-400 font-mono text-xs uppercase tracking-wider hover:border-cyan-400 hover:text-white disabled:opacity-40 transition-colors"
                >
                  {sharing ? <Loader2 size={12} className="animate-spin" /> : <Share2 size={12} />}
                  {t("debateSession.shareToCommunity")}
                </button>
              )}
            </>
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
    <div className={`pl-2 py-1.5 border-l-2 ${borderColor} flex items-start gap-2`}>
      <div className="flex-1 min-w-0">
        <p className="font-mono text-[11px] text-neutral-300 break-words leading-tight">{agent.agent_name}</p>
        <div className="flex items-center gap-1 mt-0.5 flex-wrap">
          {agent.persona !== "moderator" && (
            <span className="font-mono text-[8px] text-neutral-600 uppercase">{rankMeta.label}</span>
          )}
          <span className={`font-mono text-[8px] uppercase ${meta.color}`}>{meta.label}</span>
          {agent.persona !== "moderator" && agent.assigned_model && (
            <span className="font-mono text-[8px] uppercase text-neutral-700">
              {agent.assigned_model.split("/").pop()}
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
          {agent.persona !== "moderator" && agent.assigned_model && (
            <span className="font-mono text-[8px] uppercase text-neutral-700">
              {agent.assigned_model.split("/").pop()}
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

// SummaryBlock 设计语言（2026-04-24 PM cursor v2 → 2026-04-27 Phase 2 实装）
// Ken 拍板：参考 designdotmd.directory 报告/出版物调性，单色 amber + 1px 细线 +
// serif 大标题 + mono micro-label + ReactMarkdown 渲染。
//
// Phase 2 拆分（2026-04-27）：
//   - <FinalAnswerLayer>   Hero Direct Answer + 三段 supporting (Why / Conditions / NextSteps)
//   - <DetailedAnalysis>   原 4 段综述（Consensus / Disagreements / OpenQuestions / Directions），默认折叠
//   - <SummaryBlock>       外层壳：包两个组件 + 折叠状态 + 顶部 / 底部 micro-label
//
// design.md §axl-debate-mode-design > Final Answer Layer 子节是上位约束。
// LLM prompt 在 backend/app/services/final_answer_layer.py。

const SUMMARY_SECTION_META: Record<string, { numLabel: string }> = {
  consensus:     { numLabel: "01" },
  disagreements: { numLabel: "02" },
  openQuestions: { numLabel: "03" },
  directions:    { numLabel: "04" },
};

// Final Answer Layer supporting 元数据（Hero Direct Answer + why 单独处理，不在此列）
// Phase 2.5（2026-04-28）：UI 视觉压成 3 段——
//   段 1: Direct Answer hero + why 作为下方轻量支撑（不单独成段，灰度补充）
//   段 2: Key Conditions（① 圆圈，对应 conditions 字段）
//   段 3: User Takeaway（② 圆圈，对应 next_steps 字段）
// 数据层 4 字段不变（summary_direct_answer / summary_why / summary_conditions / summary_next_steps），
// 仅 UI 渲染压缩。why 字段留给 hero 下方的轻量补充段。
const FINAL_ANSWER_SUPPORTING: Array<{
  id: "conditions" | "next_steps";
  numLabel: string;
  titleZh: string;
  titleEn: string;
}> = [
  { id: "conditions", numLabel: "①", titleZh: "关键条件",  titleEn: "KEY CONDITIONS" },
  { id: "next_steps", numLabel: "②", titleZh: "用户可做", titleEn: "USER TAKEAWAY" },
];

// Markdown 报告排版（debate summary / paper drafts 共用）
// 三层 marker 系统由全局 CSS 控制（见 src/index.css "Markdown report typography"）：
//   一级 ul → amber 实心圆点
//   二级 ul → amber 短破折号 ─
//   三级 ul → amber 中心点 ·
//   一级 ol → mono 数字编号 01. 02.
// JSX 这里只挂语义 class（.md-list / .md-list-ordered），不再 inline before:
const MD_COMPONENTS = {
  p: ({ children }: { children?: ReactNode }) => (
    <p className="text-[15px] leading-[1.75] text-neutral-200 mb-3 last:mb-0">{children}</p>
  ),
  strong: ({ children }: { children?: ReactNode }) => (
    <strong className="font-semibold text-white">{children}</strong>
  ),
  em: ({ children }: { children?: ReactNode }) => (
    <em className="italic text-neutral-100">{children}</em>
  ),
  ul: ({ children }: { children?: ReactNode }) => (
    <ul className="md-list space-y-1.5 mb-3 last:mb-0">{children}</ul>
  ),
  ol: ({ children }: { children?: ReactNode }) => (
    <ol className="md-list md-list-ordered space-y-1.5 mb-3 last:mb-0">{children}</ol>
  ),
  li: ({ children }: { children?: ReactNode }) => (
    <li className="text-[15px] leading-[1.7] text-neutral-200">{children}</li>
  ),
  code: ({ children }: { children?: ReactNode }) => (
    <code className="font-mono text-[13px] text-amber-300 bg-amber-400/10 px-1.5 py-0.5">
      {children}
    </code>
  ),
  h1: ({ children }: { children?: ReactNode }) => (
    <h1 className="font-serif text-xl text-white mb-2 mt-4 first:mt-0">{children}</h1>
  ),
  h2: ({ children }: { children?: ReactNode }) => (
    <h2 className="font-serif text-lg text-white mb-2 mt-4 first:mt-0">{children}</h2>
  ),
  h3: ({ children }: { children?: ReactNode }) => (
    <h3 className="font-mono text-[11px] uppercase tracking-[0.15em] text-amber-400/70 mb-2 mt-3 first:mt-0">
      {children}
    </h3>
  ),
};

// FinalAnswerLayer：3 段 UI（Phase 2.5 视觉压缩，数据层仍是 4 字段）
// 段 1: Hero Direct Answer + why 作为轻量支撑说明（紧贴下方，灰度小字，不单独成段）
// 段 2: ① Key Conditions（对应 conditions 字段）
// 段 3: ② User Takeaway（对应 next_steps 字段）
// 数据源不变：debate.summary_direct_answer / summary_why / summary_conditions / summary_next_steps
function FinalAnswerLayer({ debate }: { debate: Debate }) {
  const isZh = i18n.language?.startsWith("zh");
  const direct = debate.summary_direct_answer?.trim();
  const why = debate.summary_why?.trim();
  const supporting = FINAL_ANSWER_SUPPORTING.map((meta) => ({
    ...meta,
    content: (() => {
      const v = debate[`summary_${meta.id}` as keyof Debate];
      return typeof v === "string" ? v.trim() : "";
    })(),
  })).filter((s) => s.content);

  // 全部字段为空 → 不显示 FinalAnswerLayer（Phase 2 LLM 失败兜底，让 DetailedAnalysis 顶上）
  if (!direct && !why && supporting.length === 0) return null;

  return (
    <div className="px-8 pb-7">
      {direct && (
        <div className="border-l-2 border-amber-400/70 pl-5 -ml-px">
          <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-amber-400/80 mb-2.5">
            {isZh ? "直接回答" : "DIRECT ANSWER"}
          </div>
          <h2 className="font-serif text-[26px] leading-[1.35] text-white tracking-tight">
            {direct}
          </h2>
          {why && (
            // why 紧贴 Direct Answer 作为轻量支撑说明（小字号 / 灰度 / 不抢主标题）
            // Phase 2.5 视觉决策：why 不单独成段，作为 Direct Answer 的"为什么"补充
            <div className="mt-3 pt-3 border-t border-amber-400/15">
              <div className="font-mono text-[9px] uppercase tracking-[0.18em] text-amber-400/55 mb-1.5">
                {isZh ? "为什么" : "WHY"}
              </div>
              <div className="text-[14px] text-neutral-400/90 leading-[1.7]">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>
                  {why}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}

      {supporting.length > 0 && (
        <div className="mt-7 space-y-6">
          {supporting.map((s) => (
            <section key={s.id} className="grid grid-cols-[auto_1fr] gap-x-6">
              <div className="flex flex-col items-end pr-1 min-w-[62px]">
                <div className="font-serif text-[20px] text-amber-400/75 leading-none">
                  {s.numLabel}
                </div>
                <div className="font-mono text-[9px] uppercase tracking-[0.18em] text-amber-400/80 mt-1.5 text-right leading-tight">
                  {(isZh ? s.titleZh : s.titleEn).toUpperCase()}
                </div>
              </div>
              <div className="pt-0.5">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>
                  {s.content}
                </ReactMarkdown>
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}

// DetailedAnalysis：原 4 段综述（Consensus / Disagreements / OpenQuestions / Directions）
// 默认折叠，由父级 SummaryBlock 控制展开状态。
function DetailedAnalysis({ debate, expanded }: { debate: Debate; expanded: boolean }) {
  const { t } = useTranslation();
  const isZh = i18n.language?.startsWith("zh");
  const sections = [
    { id: "consensus",     titleKey: "debateSession.consensus",     content: debate.summary_consensus },
    { id: "disagreements", titleKey: "debateSession.disagreements", content: debate.summary_disagreements },
    { id: "openQuestions", titleKey: "debateSession.openQuestions", content: debate.summary_open_questions },
    { id: "directions",    titleKey: "debateSession.directions",    content: debate.summary_directions },
  ].filter((s) => s.content);

  if (sections.length === 0) return null;
  if (!expanded) return null;

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="overflow-hidden"
    >
      <div className="mx-8 border-t border-neutral-800" />
      <div className="px-8 py-7 space-y-7">
        <div className="font-mono text-[10px] uppercase tracking-[0.22em] text-neutral-500 -mt-1">
          {isZh ? "详细分析 · 四段综述" : "DETAILED ANALYSIS · FOUR-SECTION SUMMARY"}
        </div>
        {sections.map((s) => {
          const meta = SUMMARY_SECTION_META[s.id] || { numLabel: "·" };
          return (
            <section key={s.id} className="grid grid-cols-[auto_1fr] gap-x-6">
              <div className="flex flex-col items-end pr-1 min-w-[62px]">
                <div className="font-mono text-[10px] text-amber-400/60 tracking-wider">
                  {meta.numLabel}
                </div>
                <div className="font-mono text-[9px] uppercase tracking-[0.18em] text-amber-400/80 mt-1 text-right leading-tight">
                  {t(s.titleKey).toUpperCase()}
                </div>
              </div>
              <div className="pt-0.5">
                <ReactMarkdown remarkPlugins={[remarkGfm]} components={MD_COMPONENTS}>
                  {s.content || ""}
                </ReactMarkdown>
              </div>
            </section>
          );
        })}
      </div>
    </motion.div>
  );
}

function SummaryBlock({ debate }: { debate: Debate }) {
  const isZh = i18n.language?.startsWith("zh");
  const [detailedExpanded, setDetailedExpanded] = useState(false);

  // 是否有 Final Answer Layer 数据（Phase 2 字段）
  const hasFinalAnswer = !!(
    debate.summary_direct_answer ||
    debate.summary_why ||
    debate.summary_conditions ||
    debate.summary_next_steps
  );

  // 是否有 4 段综述（任一字段非空）
  const hasDetailed = !!(
    debate.summary_consensus ||
    debate.summary_disagreements ||
    debate.summary_open_questions ||
    debate.summary_directions
  );

  if (!hasFinalAnswer && !hasDetailed) return null;

  // Final Answer 缺席时，DetailedAnalysis 默认展开兜底（用户至少能看到 4 段综述）
  const effectiveExpanded = !hasFinalAnswer ? true : detailedExpanded;

  return (
    <motion.article
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      className="my-10 border border-neutral-700/70 bg-gradient-to-b from-amber-50/[0.02] to-transparent"
    >
      {/* Top label band */}
      <div className="flex items-baseline justify-between px-8 pt-7 pb-2">
        <div className="font-mono text-[10px] uppercase tracking-[0.28em] text-amber-400/80">
          {isZh ? "辩论 · 最终答案" : "DEBATE · FINAL ANSWER"}
        </div>
        <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-neutral-600">
          {isZh ? `Debate #${debate.id}` : `№ ${debate.id}`}
        </div>
      </div>

      {hasFinalAnswer && <FinalAnswerLayer debate={debate} />}

      {hasDetailed && (
        <>
          {/* Toggle button: 仅当 FinalAnswerLayer 存在时才显示折叠控件 */}
          {hasFinalAnswer && (
            <div className="px-8 pt-1 pb-1">
              <button
                type="button"
                onClick={() => setDetailedExpanded((v) => !v)}
                className="group flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.2em] text-neutral-500 hover:text-amber-400/90 transition-colors py-3 w-full border-t border-neutral-800"
              >
                <span>
                  {effectiveExpanded
                    ? (isZh ? "收起详细分析" : "COLLAPSE DETAILED ANALYSIS")
                    : (isZh ? "展开详细分析（共识 / 分歧 / 开放问题 / 研究方向）" : "EXPAND DETAILED ANALYSIS (CONSENSUS / DISAGREEMENTS / OPEN QUESTIONS / DIRECTIONS)")}
                </span>
                <span className="ml-auto">
                  {effectiveExpanded ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                </span>
              </button>
            </div>
          )}
          <AnimatePresence initial={false}>
            {effectiveExpanded && (
              <DetailedAnalysis debate={debate} expanded={effectiveExpanded} />
            )}
          </AnimatePresence>
        </>
      )}

      {/* Footer caption */}
      <div className="px-8 pb-6 pt-2 border-t border-neutral-900">
        <div className="font-mono text-[9px] uppercase tracking-[0.18em] text-neutral-700 text-center">
          {hasFinalAnswer
            ? (isZh ? "FIG · 最终答案 + 详细分析（默认折叠）" : "FIG · FINAL ANSWER + DETAILED ANALYSIS (COLLAPSED BY DEFAULT)")
            : (isZh ? "FIG · 详细分析（最终答案层未生成）" : "FIG · DETAILED ANALYSIS (FINAL ANSWER NOT GENERATED)")}
        </div>
      </div>
    </motion.article>
  );
}

function SparkBlock({
  sparks,
  stats,
  agents,
  experimentRequested,
  onRequestExperiment,
}: {
  sparks: Spark[];
  stats: SparkStats | null;
  agents: DebateAgent[];
  experimentRequested: Set<number>;
  onRequestExperiment: (sparkId: number) => void;
}) {
  const { t } = useTranslation();
  const isZh = i18n.language?.startsWith("zh");
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
            const requested = experimentRequested.has(spark.id);
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
                  <span className="flex-1" />
                  <button
                    onClick={() => onRequestExperiment(spark.id)}
                    disabled={requested}
                    className={`flex items-center gap-1 px-2 py-0.5 font-mono text-[9px] uppercase tracking-wider transition-colors ${
                      requested
                        ? "border border-green-500/40 text-green-500 cursor-default"
                        : "border border-neutral-700 text-neutral-500 hover:border-cyan-400 hover:text-cyan-400"
                    }`}
                  >
                    <FlaskConical size={10} />
                    {requested
                      ? (isZh ? "已发起" : "SENT")
                      : (isZh ? "发起实验" : "REQUEST EXP")}
                  </button>
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
