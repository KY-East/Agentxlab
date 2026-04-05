import { useState, useCallback, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import {
  Loader2,
  Send,
  FileText,
  Check,
  Pencil,
  ArrowRight,
} from "lucide-react";
import { api } from "../../api/client";

interface Direction {
  title: string;
  description: string;
  estimated_sections: number;
}

interface OutlineSection {
  heading: string;
  summary: string;
}

type ChatMsg =
  | { role: "system"; text: string }
  | { role: "directions"; directions: Direction[] }
  | { role: "outline"; title: string; sections: OutlineSection[] }
  | { role: "user"; text: string }
  | { role: "assistant"; text: string }
  | { role: "progress"; done: number; total: number; current: string }
  | { role: "complete"; draftId: number };

interface Props {
  debateId: number;
}

export default function PaperChat({ debateId }: Props) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const bottomRef = useRef<HTMLDivElement>(null);

  const [messages, setMessages] = useState<ChatMsg[]>([]);
  const [loading, setLoading] = useState(false);
  const [input, setInput] = useState("");
  const [outlineTitle, setOutlineTitle] = useState("");
  const [outlineSections, setOutlineSections] = useState<OutlineSection[]>([]);
  const [phase, setPhase] = useState<"init" | "directions" | "outline" | "writing" | "done">("init");
  const [editingIdx, setEditingIdx] = useState<number | null>(null);
  const [draftId, setDraftId] = useState<number | null>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const push = useCallback((msg: ChatMsg) => {
    setMessages((prev) => [...prev, msg]);
  }, []);

  const handleInit = useCallback(async () => {
    if (phase !== "init") return;
    setLoading(true);
    push({ role: "system", text: t("paperChat.analyzing") });
    try {
      const res = await api.suggestDirections(debateId);
      push({ role: "system", text: t("paperChat.suggestIntro") });
      push({ role: "directions", directions: res.directions });
      setPhase("directions");
    } catch {
      push({ role: "system", text: t("paperChat.error") });
    } finally {
      setLoading(false);
    }
  }, [debateId, phase, push, t]);

  useEffect(() => {
    handleInit();
  }, [handleInit]);

  const handlePickDirection = useCallback(
    async (direction: Direction) => {
      push({ role: "user", text: direction.title });
      setLoading(true);
      push({ role: "system", text: t("paperChat.generatingOutline") });
      try {
        const draft = await api.createDraft(debateId, direction.title);
        setDraftId(draft.id);
        const sections = draft.sections.map((s) => ({
          heading: s.heading,
          summary: s.summary || "",
        }));
        setOutlineTitle(draft.title);
        setOutlineSections(sections);
        push({ role: "system", text: t("paperChat.outlineReady") });
        push({ role: "outline", title: draft.title, sections });
        setPhase("outline");
      } catch {
        push({ role: "system", text: t("paperChat.error") });
      } finally {
        setLoading(false);
      }
    },
    [debateId, push, t],
  );

  const handleSendChat = useCallback(async () => {
    const msg = input.trim();
    if (!msg) return;
    setInput("");

    if (phase === "directions") {
      push({ role: "user", text: msg });
      setLoading(true);
      push({ role: "system", text: t("paperChat.generatingOutline") });
      try {
        const draft = await api.createDraft(debateId, msg);
        setDraftId(draft.id);
        const sections = draft.sections.map((s) => ({
          heading: s.heading,
          summary: s.summary || "",
        }));
        setOutlineTitle(draft.title);
        setOutlineSections(sections);
        push({ role: "system", text: t("paperChat.outlineReady") });
        push({ role: "outline", title: draft.title, sections });
        setPhase("outline");
      } catch {
        push({ role: "system", text: t("paperChat.error") });
      } finally {
        setLoading(false);
      }
      return;
    }

    if (phase === "outline") {
      push({ role: "user", text: msg });
      setLoading(true);
      push({ role: "system", text: t("paperChat.refining") });
      try {
        const result = await api.chatRefineOutline({
          debate_id: debateId,
          current_title: outlineTitle,
          current_sections: outlineSections,
          message: msg,
        });
        setOutlineTitle(result.title);
        setOutlineSections(result.sections);
        if (result.reply) {
          push({ role: "assistant", text: result.reply });
        }
        push({ role: "outline", title: result.title, sections: result.sections });

        if (draftId) {
          await api.updateDraft(draftId, {
            title: result.title,
            sections: result.sections.map((s, i) => ({
              heading: s.heading,
              summary: s.summary,
              sort_order: i,
            })),
          });
        }
      } catch {
        push({ role: "system", text: t("paperChat.error") });
      } finally {
        setLoading(false);
      }
    }
  }, [input, phase, debateId, outlineTitle, outlineSections, draftId, push, t]);

  const handleConfirmOutline = useCallback(async () => {
    if (!draftId) return;
    setPhase("writing");
    setLoading(true);
    const total = outlineSections.length;
    let done = 0;

    push({ role: "progress", done: 0, total, current: outlineSections[0]?.heading || "" });

    try {
      const response = await api.generateAllSections(draftId);
      const reader = response.body?.getReader();
      if (!reader) throw new Error("No reader");

      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done: streamDone, value } = await reader.read();
        if (streamDone) break;
        buffer += decoder.decode(value, { stream: true });

        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          try {
            const event = JSON.parse(line.slice(6));
            if (event.event === "section_start") {
              push({ role: "system", text: t("paperChat.writingSection", { heading: event.heading }) });
              setMessages((prev) =>
                prev.map((m) =>
                  m.role === "progress" ? { ...m, current: event.heading, done } : m,
                ),
              );
            } else if (event.event === "section_done") {
              done++;
              push({ role: "system", text: t("paperChat.sectionDone", { heading: event.heading }) });
              setMessages((prev) =>
                prev.map((m) =>
                  m.role === "progress" ? { ...m, done } : m,
                ),
              );
            } else if (event.event === "all_done") {
              push({ role: "system", text: t("paperChat.allDone") });
              push({ role: "complete", draftId });
              setPhase("done");
            }
          } catch { /* skip malformed */ }
        }
      }
    } catch {
      push({ role: "system", text: t("paperChat.error") });
    } finally {
      setLoading(false);
    }
  }, [draftId, outlineSections, push, t]);

  const handleSectionEdit = useCallback(
    (idx: number, field: "heading" | "summary", value: string) => {
      setOutlineSections((prev) => {
        const next = [...prev];
        next[idx] = { ...next[idx], [field]: value };
        return next;
      });
    },
    [],
  );

  return (
    <div className="flex flex-col h-full border-t border-neutral-800">
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {messages.map((msg, i) => (
          <ChatBubble
            key={i}
            msg={msg}
            onPickDirection={handlePickDirection}
            onConfirmOutline={handleConfirmOutline}
            onSectionEdit={handleSectionEdit}
            editingIdx={editingIdx}
            setEditingIdx={setEditingIdx}
            navigate={navigate}
            phase={phase}
            t={t}
          />
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-neutral-600 font-mono text-xs">
            <Loader2 size={12} className="animate-spin" />
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {(phase === "directions" || phase === "outline") && (
        <div className="border-t border-neutral-800 px-4 py-3 flex items-center gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSendChat()}
            placeholder={
              phase === "directions"
                ? t("paperChat.chooseOrType")
                : t("paperChat.chatPlaceholder")
            }
            className="flex-1 bg-transparent border border-neutral-800 px-3 py-2 font-mono text-xs text-white placeholder-neutral-700 focus:outline-none focus:border-cyan-400"
            disabled={loading}
          />
          <button
            onClick={handleSendChat}
            disabled={!input.trim() || loading}
            className="px-3 py-2 bg-cyan-400 text-black font-mono text-xs font-bold uppercase tracking-wider hover:bg-cyan-300 disabled:opacity-40 transition-colors"
          >
            <Send size={12} />
          </button>
        </div>
      )}
    </div>
  );
}

function ChatBubble({
  msg,
  onPickDirection,
  onConfirmOutline,
  onSectionEdit,
  editingIdx,
  setEditingIdx,
  navigate,
  phase,
  t,
}: {
  msg: ChatMsg;
  onPickDirection: (d: Direction) => void;
  onConfirmOutline: () => void;
  onSectionEdit: (idx: number, field: "heading" | "summary", value: string) => void;
  editingIdx: number | null;
  setEditingIdx: (idx: number | null) => void;
  navigate: ReturnType<typeof useNavigate>;
  phase: string;
  t: ReturnType<typeof useTranslation>["t"];
}) {
  if (msg.role === "system") {
    return (
      <div className="font-mono text-[11px] text-neutral-500 border-l-2 border-neutral-800 pl-3 py-1">
        {msg.text}
      </div>
    );
  }

  if (msg.role === "user") {
    return (
      <div className="flex justify-end">
        <div className="bg-cyan-400/10 border border-cyan-400/20 px-3 py-2 max-w-[80%]">
          <p className="font-mono text-xs text-cyan-300">{msg.text}</p>
        </div>
      </div>
    );
  }

  if (msg.role === "assistant") {
    return (
      <div className="font-mono text-xs text-neutral-300 border-l-2 border-cyan-400/30 pl-3 py-1">
        {msg.text}
      </div>
    );
  }

  if (msg.role === "directions") {
    return (
      <div className="space-y-2">
        {msg.directions.map((d, i) => (
          <button
            key={i}
            onClick={() => onPickDirection(d)}
            className="w-full text-left border border-neutral-800 hover:border-cyan-400/50 p-3 transition-colors group"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1 min-w-0">
                <p className="font-mono text-xs text-white font-bold group-hover:text-cyan-300 transition-colors">
                  {d.title}
                </p>
                <p className="font-mono text-[10px] text-neutral-500 mt-1 leading-relaxed">
                  {d.description}
                </p>
              </div>
              <span className="shrink-0 font-mono text-[9px] text-neutral-700 uppercase tracking-wider mt-0.5">
                {t("paperChat.sections")}: {d.estimated_sections}
              </span>
            </div>
          </button>
        ))}
      </div>
    );
  }

  if (msg.role === "outline") {
    return (
      <div className="border border-neutral-800 p-3 space-y-2">
        <p className="font-mono text-xs text-white font-bold">{msg.title}</p>
        <div className="space-y-1">
          {msg.sections.map((s, i) => (
            <div
              key={i}
              className="flex items-start gap-2 py-1 border-b border-neutral-900 last:border-0"
            >
              <span className="font-mono text-[9px] text-neutral-700 w-5 shrink-0 text-right mt-0.5">
                {i + 1}
              </span>
              {editingIdx === i ? (
                <div className="flex-1 space-y-1">
                  <input
                    value={s.heading}
                    onChange={(e) => onSectionEdit(i, "heading", e.target.value)}
                    onBlur={() => setEditingIdx(null)}
                    onKeyDown={(e) => e.key === "Enter" && setEditingIdx(null)}
                    className="w-full bg-transparent border border-neutral-700 px-2 py-0.5 font-mono text-[11px] text-white focus:outline-none focus:border-cyan-400"
                    autoFocus
                  />
                </div>
              ) : (
                <div
                  className="flex-1 cursor-pointer group"
                  onClick={() => setEditingIdx(i)}
                >
                  <p className="font-mono text-[11px] text-neutral-300 group-hover:text-white transition-colors">
                    {s.heading}
                    <Pencil
                      size={8}
                      className="inline ml-1 text-neutral-700 group-hover:text-neutral-400"
                    />
                  </p>
                  {s.summary && (
                    <p className="font-mono text-[9px] text-neutral-600 mt-0.5">
                      {s.summary}
                    </p>
                  )}
                </div>
              )}
            </div>
          ))}
        </div>
        {phase === "outline" && (
          <button
            onClick={onConfirmOutline}
            className="mt-2 flex items-center gap-2 px-4 py-2 bg-cyan-400 text-black font-mono text-xs font-bold uppercase tracking-wider hover:bg-cyan-300 transition-colors"
          >
            <Check size={12} />
            {t("paperChat.confirmOutline")}
          </button>
        )}
      </div>
    );
  }

  if (msg.role === "progress") {
    const pct = msg.total > 0 ? (msg.done / msg.total) * 100 : 0;
    return (
      <div className="border border-neutral-800 p-3 space-y-2">
        <div className="flex items-center justify-between">
          <p className="font-mono text-[10px] text-neutral-400 uppercase tracking-wider">
            {t("paperChat.writingProgress", { done: msg.done, total: msg.total })}
          </p>
          <span className="font-mono text-[10px] text-cyan-400">{Math.round(pct)}%</span>
        </div>
        <div className="w-full h-1 bg-neutral-800">
          <div
            className="h-full bg-cyan-400 transition-all duration-500"
            style={{ width: `${pct}%` }}
          />
        </div>
        {msg.current && (
          <p className="font-mono text-[9px] text-neutral-600">
            <FileText size={9} className="inline mr-1" />
            {msg.current}
          </p>
        )}
      </div>
    );
  }

  if (msg.role === "complete") {
    return (
      <button
        onClick={() => navigate(`/paper/${msg.draftId}`)}
        className="flex items-center gap-2 px-4 py-2 bg-cyan-400 text-black font-mono text-xs font-bold uppercase tracking-wider hover:bg-cyan-300 transition-colors"
      >
        <ArrowRight size={12} />
        {t("paperChat.goToEditor")}
      </button>
    );
  }

  return null;
}
