import { useEffect, useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import i18n from "../../i18n";
import {
  X,
  Loader2,
  Sparkles,
  BookOpen,
  User,
  AlertCircle,
  Send,
  Check,
  Terminal,
  FileText,
  Swords,
} from "lucide-react";
import { api } from "../../api/client";
import type { Intersection, ChatHypothesisResponse } from "../../types";

interface ChatMessage {
  role: "system" | "user" | "assistant" | "action";
  content: string;
  suggestions?: string[];
  hypothesis?: string | null;
  actionType?: string;
}

export interface AgentAction {
  type: "remove_discipline" | "add_discipline" | "start_debate" | "clear_all" | "explore";
  payload?: Record<string, unknown>;
}

interface Props {
  intersectionId: number | null;
  onClose: () => void;
  onAgentAction?: (action: AgentAction) => void;
  selectedDisciplineNames?: string[];
  selectedNodeIds?: number[];
}

export default function DetailPanel({
  intersectionId,
  onClose,
  onAgentAction,
  selectedDisciplineNames = [],
  selectedNodeIds = [],
}: Props) {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [data, setData] = useState<Intersection | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatHistory, setChatHistory] = useState<{ role: string; content: string }[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [confirmedHypothesis, setConfirmedHypothesis] = useState<string | null>(null);
  const [lastUserDirection, setLastUserDirection] = useState<string | null>(null);
  const [chatHeight, setChatHeight] = useState(200);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const dragRef = useRef<{ startY: number; startH: number } | null>(null);

  useEffect(() => {
    if (intersectionId === null) {
      setData(null);
      setError(null);
      setChatMessages([]);
      setChatHistory([]);
      setConfirmedHypothesis(null);
      setLastUserDirection(null);
      return;
    }
    setLoading(true);
    setError(null);
    setChatMessages([]);
    setChatHistory([]);
    setConfirmedHypothesis(null);
    api
      .getIntersection(intersectionId)
      .then(setData)
      .catch((err) => {
        setData(null);
        setError(err instanceof Error ? err.message : t("detailChat.loadFailed"));
      })
      .finally(() => setLoading(false));
  }, [intersectionId, t]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, chatLoading]);

  const lang = useCallback(() => (i18n.language?.startsWith("zh") ? "zh" : "en"), []);

  const handleChatDragStart = useCallback(
    (e: React.MouseEvent) => {
      e.preventDefault();
      dragRef.current = { startY: e.clientY, startH: chatHeight };
      const onMove = (ev: MouseEvent) => {
        if (!dragRef.current) return;
        const delta = dragRef.current.startY - ev.clientY;
        setChatHeight(Math.max(120, Math.min(600, dragRef.current.startH + delta)));
      };
      const onUp = () => {
        dragRef.current = null;
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("mouseup", onUp);
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
      };
      document.addEventListener("mousemove", onMove);
      document.addEventListener("mouseup", onUp);
      document.body.style.cursor = "row-resize";
      document.body.style.userSelect = "none";
    },
    [chatHeight],
  );

  const parseAgentIntent = useCallback(
    (text: string): AgentAction | null => {
      const lower = text.toLowerCase().trim();
      const zhLower = text.trim();

      const removePatterns = [
        /^(?:remove|delete|drop|去掉|删除|移除|去除)\s*(.+)$/i,
      ];
      for (const p of removePatterns) {
        const m = (lower.match(p) || zhLower.match(p));
        if (m) return { type: "remove_discipline", payload: { name: m[1].trim() } };
      }

      const addPatterns = [
        /^(?:add|include|加上|添加|增加)\s*(.+)$/i,
      ];
      for (const p of addPatterns) {
        const m = (lower.match(p) || zhLower.match(p));
        if (m) return { type: "add_discipline", payload: { name: m[1].trim() } };
      }

      if (/^(?:start debate|发起辩论|开始辩论|辩论)$/i.test(lower) || /^(?:start debate|发起辩论|开始辩论|辩论)$/i.test(zhLower)) {
        return { type: "start_debate" };
      }

      if (/^(?:clear|清除|清空|reset)$/i.test(lower)) {
        return { type: "clear_all" };
      }

      return null;
    },
    [],
  );

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim()) return;
      const userMsg: ChatMessage = { role: "user", content: text };
      setChatMessages((prev) => [...prev, userMsg]);
      setChatInput("");
      if (textareaRef.current) textareaRef.current.style.height = "auto";

      const action = parseAgentIntent(text);
      if (action && onAgentAction) {
        onAgentAction(action);
        const actionLabels: Record<string, string> = {
          remove_discipline: lang() === "zh" ? "已执行：移除学科" : "Executed: remove discipline",
          add_discipline: lang() === "zh" ? "已执行：添加学科" : "Executed: add discipline",
          start_debate: lang() === "zh" ? "已执行：发起辩论" : "Executed: start debate",
          clear_all: lang() === "zh" ? "已执行：清除画布" : "Executed: clear canvas",
        };
        setChatMessages((prev) => [
          ...prev,
          { role: "action", content: actionLabels[action.type] || "OK", actionType: action.type },
        ]);
        return;
      }

      setLastUserDirection(text.trim());

      if (!intersectionId && selectedNodeIds.length === 0) {
        setChatMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: lang() === "zh"
              ? "画布上还没有选中学科。你可以用自然语言操作画布：\n- \"加上 XX\" 添加学科\n- \"清除\" 清空画布"
              : "No disciplines on canvas. Use natural language:\n- \"add XX\" to select\n- \"clear\" to reset",
          },
        ]);
        return;
      }

      setChatLoading(true);

      try {
        let res: ChatHypothesisResponse;

        if (intersectionId) {
          res = await api.chatHypothesis({
            intersection_id: intersectionId,
            message: text,
            history: [...chatHistory, { role: "user" as const, content: text }],
            language: lang(),
          });
        } else {
          res = await api.canvasChat({
            discipline_ids: selectedNodeIds,
            message: text,
            history: chatHistory,
            language: lang(),
          });
        }
        const assistantMsg: ChatMessage = {
          role: "assistant",
          content: res.reply,
          suggestions: res.suggestions,
          hypothesis: res.hypothesis,
        };
        setChatMessages((prev) => [...prev, assistantMsg]);
        setChatHistory((prev) => [
          ...prev,
          { role: "user", content: text },
          { role: "assistant", content: JSON.stringify(res) },
        ]);

        if (res.hypothesis) {
          setConfirmedHypothesis(res.hypothesis);
        }
      } catch (err) {
        setChatMessages((prev) => [
          ...prev,
          {
            role: "system",
            content: err instanceof Error ? err.message : t("detailChat.error"),
          },
        ]);
      } finally {
        setChatLoading(false);
      }
    },
    [intersectionId, selectedNodeIds, chatHistory, lang, t, parseAgentIntent, onAgentAction],
  );

  const startExplore = useCallback(async () => {
    if (!data || intersectionId === null) return;
    setChatLoading(true);
    setChatMessages([
      { role: "system", content: t("detailChat.analyzing") },
    ]);

    try {
      const res: ChatHypothesisResponse = await api.chatHypothesis({
        intersection_id: intersectionId,
        message: "",
        history: [],
        language: lang(),
      });
      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: res.reply,
        suggestions: res.suggestions,
        hypothesis: res.hypothesis,
      };
      setChatMessages([assistantMsg]);
      setChatHistory([
        { role: "assistant", content: JSON.stringify(res) },
      ]);
    } catch (err) {
      setChatMessages([
        { role: "system", content: err instanceof Error ? err.message : t("detailChat.error") },
      ]);
    } finally {
      setChatLoading(false);
    }
  }, [data, intersectionId, lang, t]);

  const handleSuggestionClick = useCallback(
    (suggestion: string) => {
      sendMessage(suggestion);
    },
    [sendMessage],
  );

  const renderContent = () => {
    if (intersectionId === null) {
      return (
        <div className="flex items-center justify-center flex-1 text-neutral-500 text-sm p-6 text-center">
          <div>
            <BookOpen size={32} className="mx-auto mb-3 text-neutral-600" />
            <p className="font-mono text-xs uppercase tracking-wider">
              {t("detailChat.emptyHint")}
            </p>
            <p className="text-[10px] mt-1 text-neutral-600 font-mono uppercase tracking-wider">
              {t("detailChat.legendHint")}
            </p>
            {selectedDisciplineNames.length > 0 && (
              <p className="text-[10px] mt-3 text-neutral-600 font-mono">
                {lang() === "zh"
                  ? `画布上有 ${selectedDisciplineNames.length} 个学科`
                  : `${selectedDisciplineNames.length} disciplines on canvas`}
              </p>
            )}
          </div>
        </div>
      );
    }

    if (loading) {
      return (
        <div className="flex items-center justify-center flex-1">
          <Loader2 className="animate-spin text-neutral-400" size={24} />
        </div>
      );
    }

    if (error) {
      return (
        <div className="flex items-center justify-center flex-1 text-center p-6">
          <div>
            <AlertCircle size={32} className="mx-auto mb-3 text-red-400" />
            <p className="text-sm text-red-300 mb-1 font-mono">{t("detailChat.loadError")}</p>
            <p className="text-xs text-neutral-500">{error}</p>
            <button
              onClick={onClose}
              className="mt-3 px-3 py-1 text-xs border border-neutral-700 hover:border-cyan-400 text-neutral-400 hover:text-white transition-colors font-mono uppercase tracking-wider"
            >
              {t("detailChat.close")}
            </button>
          </div>
        </div>
      );
    }

    if (!data) return null;

    return (
      <>
        {/* Header */}
        <div className="flex items-start justify-between p-4 border-b border-neutral-800 shrink-0">
          <div>
            <h2 className="text-sm font-mono font-bold text-white uppercase tracking-wider">
              {data.title}
            </h2>
            <div className="flex gap-1.5 mt-1.5 flex-wrap">
              {data.disciplines.map((d) => (
                <span
                  key={d.id}
                  className="text-[10px] px-2 py-0.5 border border-cyan-500/30 text-cyan-400 font-mono uppercase tracking-wider"
                >
                  {lang() === "zh" ? (d.name_zh || d.name_en) : d.name_en}
                </span>
              ))}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-neutral-500 hover:text-white transition-colors"
          >
            <X size={16} />
          </button>
        </div>

        {/* Action bar -- always visible */}
        {data.disciplines.length >= 2 && (
          <div className="flex gap-2 px-4 py-2 border-b border-neutral-800 shrink-0">
            <button
              onClick={startExplore}
              disabled={chatLoading}
              className="flex-1 flex items-center justify-center gap-1.5 px-2 py-1.5 border border-cyan-400/40 hover:border-cyan-400 text-cyan-400 hover:text-white text-[10px] font-mono uppercase tracking-wider transition-colors disabled:opacity-40"
            >
              <Sparkles size={12} />
              {t("detailChat.exploreDirections")}
            </button>
            <button
              onClick={() => {
                const ids = data.disciplines.map((d) => d.id).join(",");
                const bestDirection =
                  confirmedHypothesis ||
                  lastUserDirection ||
                  (data.hypotheses.length > 0
                    ? data.hypotheses[data.hypotheses.length - 1].hypothesis_text
                    : undefined);
                navigate(`/debate?intersection=${data.id}&disciplines=${ids}`, {
                  state: {
                    intersectionTitle: data.title,
                    coreTension: data.core_tension,
                    openQuestions: data.open_questions,
                    hypothesis: bestDirection,
                    direction: lastUserDirection || undefined,
                  },
                });
              }}
              className="flex-1 flex items-center justify-center gap-1.5 px-2 py-1.5 border border-neutral-700 hover:border-cyan-400 text-neutral-400 hover:text-white text-[10px] font-mono uppercase tracking-wider transition-colors"
            >
              <Swords size={12} />
              {t("detailChat.startDebate")}
            </button>
            <button
              onClick={() => {
                const ids = data.disciplines.map((d) => d.id).join(",");
                const bestDirection =
                  confirmedHypothesis ||
                  lastUserDirection ||
                  (data.hypotheses.length > 0
                    ? data.hypotheses[data.hypotheses.length - 1].hypothesis_text
                    : undefined);
                navigate(`/debate?intersection=${data.id}&disciplines=${ids}&then=paper`, {
                  state: {
                    intersectionTitle: data.title,
                    coreTension: data.core_tension,
                    openQuestions: data.open_questions,
                    hypothesis: bestDirection,
                    direction: lastUserDirection || undefined,
                    startPaper: true,
                  },
                });
              }}
              className="flex-1 flex items-center justify-center gap-1.5 px-2 py-1.5 border border-neutral-700 hover:border-cyan-400 text-neutral-400 hover:text-white text-[10px] font-mono uppercase tracking-wider transition-colors"
            >
              <FileText size={12} />
              {t("detailChat.generatePaper")}
            </button>
          </div>
        )}

        {/* Scrollable detail content */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4 min-h-0">
          {data.status === "gap" && (
            <div className="flex items-start gap-2 p-3 border border-red-500/30 bg-red-500/5">
              <AlertCircle size={14} className="text-red-400 mt-0.5 shrink-0" />
              <div>
                <p className="text-red-300 text-xs font-mono uppercase tracking-wider font-bold">
                  {t("detailChat.researchGap")}
                </p>
                <p className="text-red-400/70 text-[10px] mt-0.5 font-mono">
                  {t("detailChat.researchGapDesc")}
                </p>
              </div>
            </div>
          )}

          {data.core_tension && (
            <section>
              <h3 className="text-[10px] font-mono font-bold text-neutral-500 uppercase tracking-[0.15em] mb-1">
                {t("detailChat.coreTension")}
              </h3>
              <p className="text-xs text-neutral-400 leading-relaxed">{data.core_tension}</p>
            </section>
          )}

          {data.classic_dialogue && (
            <section>
              <h3 className="text-[10px] font-mono font-bold text-neutral-500 uppercase tracking-[0.15em] mb-1">
                {t("detailChat.classicDialogue")}
              </h3>
              <p className="text-xs text-neutral-400 leading-relaxed">{data.classic_dialogue}</p>
            </section>
          )}

          {data.frontier_progress && (
            <section>
              <h3 className="text-[10px] font-mono font-bold text-neutral-500 uppercase tracking-[0.15em] mb-1">
                {t("detailChat.frontierProgress")}
              </h3>
              <p className="text-xs text-neutral-400 leading-relaxed">{data.frontier_progress}</p>
            </section>
          )}

          {data.open_questions && (
            <section>
              <h3 className="text-[10px] font-mono font-bold text-neutral-500 uppercase tracking-[0.15em] mb-1">
                {t("detailChat.openQuestions")}
              </h3>
              <p className="text-xs text-neutral-400 leading-relaxed">{data.open_questions}</p>
            </section>
          )}

          {data.scholars.length > 0 && (
            <section>
              <h3 className="text-[10px] font-mono font-bold text-neutral-500 uppercase tracking-[0.15em] mb-2">
                <User size={12} className="inline mr-1" />
                {t("detailChat.scholars")}
              </h3>
              <div className="flex flex-wrap gap-1.5">
                {data.scholars.map((s) => (
                  <span key={s.id} className="text-[10px] px-2 py-0.5 border border-green-500/30 text-green-400 font-mono">
                    {s.name}
                  </span>
                ))}
              </div>
            </section>
          )}

          {data.papers.length > 0 && (
            <section>
              <h3 className="text-[10px] font-mono font-bold text-neutral-500 uppercase tracking-[0.15em] mb-2">
                <BookOpen size={12} className="inline mr-1" />
                {t("detailChat.papers")}
              </h3>
              <ul className="space-y-1">
                {data.papers.map((p) => (
                  <li key={p.id} className="text-xs text-neutral-400">
                    {p.title}
                    {p.year && <span className="text-neutral-600 ml-1">({p.year})</span>}
                  </li>
                ))}
              </ul>
            </section>
          )}

          {data.hypotheses.length > 0 && (
            <section>
              <h3 className="text-[10px] font-mono font-bold text-neutral-500 uppercase tracking-[0.15em] mb-2">
                <Sparkles size={12} className="inline mr-1" />
                {t("detailChat.aiHypotheses")}
              </h3>
              {data.hypotheses.map((h) => (
                <div key={h.id} className="p-3 border border-cyan-500/20 bg-cyan-500/5 mb-2">
                  <p className="text-xs text-cyan-100 leading-relaxed whitespace-pre-wrap">{h.hypothesis_text}</p>
                  <p className="text-[10px] text-cyan-400/50 mt-2 font-mono">
                    {h.model_name} / {new Date(h.created_at).toLocaleDateString(lang())}
                  </p>
                </div>
              ))}
            </section>
          )}

          {confirmedHypothesis && (
            <div className="p-3 border-2 border-cyan-400/40 bg-cyan-500/5">
              <div className="flex items-center gap-1.5 mb-2">
                <Check size={12} className="text-cyan-400" />
                <span className="text-[10px] font-mono font-bold text-cyan-400 uppercase tracking-wider">
                  {t("detailChat.confirmedHypothesis")}
                </span>
              </div>
              <p className="text-xs text-cyan-100 leading-relaxed whitespace-pre-wrap">{confirmedHypothesis}</p>
            </div>
          )}

          {/* Action buttons moved to fixed action bar above */}
        </div>
      </>
    );
  };

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {renderContent()}

      {/* Chat area -- always visible, resizable */}
      <div
        onMouseDown={handleChatDragStart}
        className="h-1 shrink-0 cursor-row-resize hover:bg-cyan-400/40 active:bg-cyan-400/60 transition-colors border-t border-cyan-400/20"
      />
      <div className="flex flex-col shrink-0" style={{ height: chatHeight }}>
        <div className="flex items-center justify-between px-3 py-1 border-b border-neutral-800">
          <span className="text-[10px] font-mono font-bold text-cyan-400 uppercase tracking-[0.15em] flex items-center gap-1.5">
            <Terminal size={10} />
            {t("detailChat.chatTitle")}
          </span>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-2 min-h-0">
          {chatMessages.length === 0 && (
            <p className="text-[10px] text-neutral-600 font-mono text-center py-4">
              {lang() === "zh"
                ? (intersectionId
                    ? "输入指令或问题，如「去掉XX」「加上XX」「发起辩论」"
                    : selectedNodeIds.length > 0
                      ? `画布上有 ${selectedNodeIds.length} 个学科，直接提问即可`
                      : "先在左侧选择学科，然后可以对话探索")
                : (intersectionId
                    ? "Type a command or question, e.g. \"remove XX\", \"add XX\", \"start debate\""
                    : selectedNodeIds.length > 0
                      ? `${selectedNodeIds.length} disciplines on canvas. Ask anything.`
                      : "Select disciplines first, then chat to explore")}
            </p>
          )}
          {chatMessages.map((msg, i) => (
            <div key={i}>
              {msg.role === "system" ? (
                <p className="text-[10px] text-neutral-500 font-mono text-center py-0.5">
                  {msg.content}
                </p>
              ) : msg.role === "action" ? (
                <div className="flex items-center gap-1.5 py-0.5">
                  <Check size={10} className="text-cyan-400" />
                  <p className="text-[10px] text-cyan-400 font-mono">{msg.content}</p>
                </div>
              ) : msg.role === "user" ? (
                <div className="flex justify-end">
                  <div className="max-w-[85%] px-2.5 py-1.5 bg-cyan-500/10 border border-cyan-500/20 text-xs text-white">
                    {msg.content}
                  </div>
                </div>
              ) : (
                <div className="max-w-[95%]">
                  <div className="px-2.5 py-1.5 bg-neutral-900 border border-neutral-800 text-xs text-neutral-300 leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </div>
                  {msg.suggestions && msg.suggestions.length > 0 && (
                    <div className="mt-1.5 space-y-1">
                      {msg.suggestions.map((s, j) => (
                        <button
                          key={j}
                          onClick={() => handleSuggestionClick(s)}
                          disabled={chatLoading}
                          className="block w-full text-left px-2.5 py-1 border border-dashed border-cyan-500/30 hover:border-cyan-400 text-[10px] text-cyan-400 font-mono transition-colors disabled:opacity-40"
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  )}
                  {msg.hypothesis && (
                    <div className="mt-1.5 p-2 border border-cyan-400/30 bg-cyan-500/5">
                      <p className="text-[10px] font-mono text-cyan-400 uppercase tracking-wider mb-1">
                        {t("detailChat.hypothesisReady")}
                      </p>
                      <p className="text-xs text-cyan-100 whitespace-pre-wrap leading-relaxed">
                        {msg.hypothesis}
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          ))}
          {chatLoading && (
            <div className="flex items-center gap-2 text-neutral-500">
              <Loader2 size={10} className="animate-spin" />
              <span className="text-[10px] font-mono">{t("detailChat.thinking")}</span>
            </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* Input */}
        <div className="px-3 py-1.5 border-t border-neutral-800 flex gap-2 shrink-0">
          <textarea
            ref={textareaRef}
            value={chatInput}
            onChange={(e) => {
              setChatInput(e.target.value);
              const el = e.target;
              el.style.height = "auto";
              el.style.height = Math.min(el.scrollHeight, 120) + "px";
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                sendMessage(chatInput);
              }
            }}
            disabled={chatLoading}
            rows={1}
            placeholder={t("detailChat.inputPlaceholder")}
            className="flex-1 bg-transparent border border-neutral-700 focus:border-cyan-400 px-2.5 py-1.5 text-xs text-white placeholder-neutral-600 font-mono outline-none transition-colors resize-none overflow-y-auto leading-relaxed"
          />
          <button
            onClick={() => sendMessage(chatInput)}
            disabled={chatLoading || !chatInput.trim()}
            className="p-1.5 border border-neutral-700 hover:border-cyan-400 text-neutral-500 hover:text-cyan-400 transition-colors disabled:opacity-30 self-end"
          >
            <Send size={12} />
          </button>
        </div>
      </div>
    </div>
  );
}
