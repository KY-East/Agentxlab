import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import i18n from "../../i18n";
import {
  X,
  Loader2,
  Swords,
  Terminal,
  Send,
  Check,
} from "lucide-react";
import { api } from "../../api/client";
import type { EdgeDetail, ChatHypothesisResponse } from "../../types";
import ModelSelector from "../ModelSelector";

interface ChatMessage {
  role: "system" | "user" | "assistant" | "action";
  content: string;
  suggestions?: string[];
  hypothesis?: string | null;
}

interface Props {
  sourceId: number;
  targetId: number;
  onClose: () => void;
}

export default function EdgeDetailPanel({ sourceId, targetId, onClose }: Props) {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const isZh = i18n.language?.startsWith("zh");
  const lang = isZh ? "zh" : "en";

  const [data, setData] = useState<EdgeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatHistory, setChatHistory] = useState<{ role: string; content: string }[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatHeight, setChatHeight] = useState(200);
  const chatEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const dragRef = useRef<{ startY: number; startH: number } | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    setChatMessages([]);
    setChatHistory([]);
    api
      .getEdgeDetail(sourceId, targetId)
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [sourceId, targetId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, chatLoading]);

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

  const topPairSummary =
    data && data.topic_pairs.length > 0
      ? data.topic_pairs
          .slice(0, 3)
          .map((p) => `${p.topic_a_name} x ${p.topic_b_name}`)
          .join("; ")
      : null;

  const buildContextPrefix = useCallback(() => {
    if (!data) return "";
    const topPairs = data.topic_pairs
      .slice(0, 5)
      .map((p) => `  - ${p.topic_a_name} x ${p.topic_b_name} (${p.shared_papers})`)
      .join("\n");
    if (isZh) {
      return (
        `[当前交叉学科]\n${data.subfield_a_name} x ${data.subfield_b_name}\n` +
        `共享论文：${data.total_papers} 篇\n` +
        (topPairs ? `主要 topic 交叉：\n${topPairs}\n\n` : "\n") +
        `[用户问题]\n`
      );
    }
    return (
      `[Current cross-field]\n${data.subfield_a_name} x ${data.subfield_b_name}\n` +
      `Shared papers: ${data.total_papers}\n` +
      (topPairs ? `Top topic intersections:\n${topPairs}\n\n` : "\n") +
      `[User question]\n`
    );
  }, [data, isZh]);

  const sendMessage = useCallback(
    async (text: string) => {
      if (!text.trim()) return;
      const userMsg: ChatMessage = { role: "user", content: text };
      setChatMessages((prev) => [...prev, userMsg]);
      setChatInput("");
      if (textareaRef.current) textareaRef.current.style.height = "auto";

      setChatLoading(true);

      const isFirstMessage = chatHistory.length === 0;
      const messageForApi = isFirstMessage
        ? buildContextPrefix() + text
        : text;

      try {
        const res: ChatHypothesisResponse = await api.edgeChat({
          subfield_a_id: sourceId,
          subfield_b_id: targetId,
          message: messageForApi,
          history: chatHistory,
          language: lang,
        });
        const assistantMsg: ChatMessage = {
          role: "assistant",
          content: res.reply,
          suggestions: res.suggestions,
          hypothesis: res.hypothesis,
        };
        setChatMessages((prev) => [...prev, assistantMsg]);
        setChatHistory((prev) => [
          ...prev,
          { role: "user", content: messageForApi },
          { role: "assistant", content: JSON.stringify(res) },
        ]);
      } catch (err) {
        setChatMessages((prev) => [
          ...prev,
          {
            role: "system",
            content: err instanceof Error ? err.message : "Error",
          },
        ]);
      } finally {
        setChatLoading(false);
      }
    },
    [sourceId, targetId, chatHistory, lang, buildContextPrefix],
  );

  const handleSuggestionClick = useCallback(
    (suggestion: string) => {
      sendMessage(suggestion);
    },
    [sendMessage],
  );

  return (
    <div className="flex flex-col h-full overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-neutral-800 shrink-0 bg-neutral-950">
        <h2 className="text-[11px] font-bold uppercase tracking-widest text-white font-mono truncate">
          {isZh ? "交叉详情" : "CROSS DETAIL"}
        </h2>
        <button
          onClick={onClose}
          className="text-neutral-600 hover:text-white transition-colors"
        >
          <X size={14} />
        </button>
      </div>

      {/* Action bar */}
      {data && !loading && (
        <div className="flex gap-2 px-4 py-2 border-b border-neutral-800 shrink-0 bg-neutral-950">
          <button
            onClick={() => {
              navigate(`/debate?disciplines=${sourceId},${targetId}`, {
                state: {
                  intersectionTitle: `${data.subfield_a_name} x ${data.subfield_b_name}`,
                  hypothesis: topPairSummary || undefined,
                },
              });
            }}
            className="flex-1 flex items-center justify-center gap-1.5 px-2 py-1.5 border border-neutral-700 hover:border-cyan-400 text-neutral-400 hover:text-white text-[10px] font-mono uppercase tracking-wider transition-colors"
          >
            <Swords size={12} />
            {isZh ? "辩论" : "DEBATE"}
          </button>
          <button
            onClick={() => {
              const tag = data ? `${data.subfield_a_name}` : "";
              navigate(`/forum?zone=ai_generated${tag ? `&discipline_tag=${encodeURIComponent(tag)}` : ""}`);
            }}
            className="flex-1 flex items-center justify-center gap-1.5 px-2 py-1.5 border border-neutral-700 hover:border-cyan-400 text-neutral-400 hover:text-white text-[10px] font-mono uppercase tracking-wider transition-colors"
          >
            {isZh ? "论坛" : "FORUM"}
          </button>
        </div>
      )}

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto p-4 bg-neutral-950 text-neutral-300 font-mono text-xs min-h-0">
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 size={16} className="animate-spin text-neutral-600" />
          </div>
        )}

        {error && (
          <p className="text-red-400 text-[11px]">{error}</p>
        )}

        {data && !loading && (
          <>
            <div className="mb-4 pb-3 border-b border-neutral-800">
              <div className="text-white text-[12px] font-bold mb-1">
                {data.subfield_a_name}
              </div>
              <div className="text-neutral-600 text-[10px] mb-2">&times;</div>
              <div className="text-white text-[12px] font-bold mb-3">
                {data.subfield_b_name}
              </div>
              <div className="text-cyan-400 text-[13px] tabular-nums">
                {data.total_papers} {isZh ? "篇共享论文" : "shared papers"}
              </div>
            </div>

            {data.topic_pairs.length > 0 ? (
              <div>
                <h3 className="text-[10px] uppercase tracking-widest text-neutral-600 mb-3">
                  {isZh ? "TOPIC 交叉明细" : "TOPIC INTERSECTIONS"}
                </h3>
                <div className="space-y-2">
                  {data.topic_pairs.map((pair, i) => (
                    <div
                      key={i}
                      className="border border-neutral-800 p-2.5 hover:border-neutral-700 transition-colors"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <div className="text-neutral-200 text-[11px] leading-relaxed truncate">
                            {pair.topic_a_name}
                          </div>
                          <div className="text-neutral-600 text-[9px] my-0.5">&times;</div>
                          <div className="text-neutral-200 text-[11px] leading-relaxed truncate">
                            {pair.topic_b_name}
                          </div>
                        </div>
                        <span className="text-cyan-400 text-[11px] tabular-nums shrink-0 mt-1">
                          {pair.shared_papers}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <p className="text-neutral-600 text-[11px] text-center py-6">
                {isZh
                  ? "共享论文存在于 subfield 级别，无 topic 级明细"
                  : "Shared papers at subfield level, no topic-level breakdown"}
              </p>
            )}
          </>
        )}
      </div>

      {/* Chat drag handle */}
      <div
        onMouseDown={handleChatDragStart}
        className="h-1 shrink-0 cursor-row-resize hover:bg-cyan-400/40 active:bg-cyan-400/60 transition-colors border-t border-cyan-400/20"
      />

      {/* Chat area */}
      <div className="flex flex-col shrink-0 bg-neutral-950" style={{ height: chatHeight }}>
        <div className="flex items-center justify-between px-3 py-1 border-b border-neutral-800">
          <span className="text-[10px] font-mono font-bold text-cyan-400 uppercase tracking-[0.15em] flex items-center gap-1.5">
            <Terminal size={10} />
            {isZh ? "对话" : "CHAT"}
          </span>
          <ModelSelector />
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-2 min-h-0">
          {chatMessages.length === 0 && (
            <p className="text-[10px] text-neutral-600 font-mono text-center py-4">
              {isZh
                ? "输入问题探索这个交叉领域，如「有哪些可研究的方向」"
                : "Ask about this cross-field connection, e.g. \"What research directions exist?\""}
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
                        {isZh ? "假设已就绪" : "HYPOTHESIS READY"}
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
              <span className="text-[10px] font-mono">{isZh ? "思考中..." : "Thinking..."}</span>
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
            placeholder={isZh ? "输入问题..." : "Ask a question..."}
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
