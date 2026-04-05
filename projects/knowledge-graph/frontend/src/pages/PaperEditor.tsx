import { useState, useEffect, useCallback } from "react";
import { useTranslation } from "react-i18next";
import { useParams, useNavigate } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import {
  Loader2,
  ArrowLeft,
  Sparkles,
  ChevronDown,
  ChevronUp,
  FileText,
  Download,
  Check,
  Pencil,
  Plus,
  RotateCcw,
} from "lucide-react";
import { api } from "../api/client";
import type { DraftOut, PaperSectionOut, SectionUpdate } from "../types";

export default function PaperEditor() {
  const { t } = useTranslation();
  const { draftId } = useParams<{ draftId: string }>();
  const navigate = useNavigate();

  const [draft, setDraft] = useState<DraftOut | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [genSectionId, setGenSectionId] = useState<number | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const [editingTitle, setEditingTitle] = useState(false);
  const [titleValue, setTitleValue] = useState("");
  const [saving, setSaving] = useState(false);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3500);
  }, []);

  const loadDraft = useCallback(async () => {
    if (!draftId) return;
    setLoading(true);
    setDraft(null);
    setError(null);
    try {
      const d = await api.getDraft(Number(draftId));
      setDraft(d);
      setTitleValue(d.title);
    } catch (err) {
      setError(err instanceof Error ? err.message : t("paper.loadFailed"));
    } finally {
      setLoading(false);
    }
  }, [draftId, t]);

  useEffect(() => {
    loadDraft();
  }, [loadDraft]);

  const handleSaveTitle = async () => {
    if (!draft || !titleValue.trim() || titleValue === draft.title) {
      setEditingTitle(false);
      return;
    }
    setSaving(true);
    try {
      const updated = await api.updateDraft(draft.id, { title: titleValue.trim() });
      setDraft(updated);
      setEditingTitle(false);
    } catch (err) {
      showToast(err instanceof Error ? err.message : t("paper.saveFailed"));
    } finally {
      setSaving(false);
    }
  };

  const handleSaveSection = async (sectionId: number, updates: SectionUpdate) => {
    if (!draft) return;
    setSaving(true);
    try {
      const updated = await api.updateDraft(draft.id, {
        sections: [{ id: sectionId, ...updates }],
      });
      setDraft(updated);
      showToast(t("paper.saved"));
    } catch (err) {
      showToast(err instanceof Error ? err.message : t("paper.saveFailed"));
    } finally {
      setSaving(false);
    }
  };

  const handleGenerate = async (sectionId: number) => {
    if (!draft) return;
    setGenSectionId(sectionId);
    try {
      const updated = await api.generateSection(draft.id, sectionId);
      setDraft((prev) => {
        if (!prev) return prev;
        const newSections = prev.sections.map((s) =>
          s.id === updated.id ? updated : s
        );
        const allDone = newSections.every((s) => s.status === "completed");
        const hasAnyContent = newSections.some((s) => s.status === "completed" || s.status === "generating");
        const newStatus = allDone ? "completed" : hasAnyContent ? "writing" : prev.status;
        return { ...prev, sections: newSections, status: newStatus };
      });
      showToast(t("paper.generateComplete", { heading: updated.heading }));
      setExpandedId(sectionId);
    } catch (err) {
      showToast(err instanceof Error ? err.message : t("paper.generateFailed"));
    } finally {
      setGenSectionId(null);
    }
  };

  const handleAddSection = async () => {
    if (!draft) return;
    const newOrder = draft.sections.length;
    setSaving(true);
    try {
      const updated = await api.updateDraft(draft.id, {
        sections: [{ heading: t("paper.newSection"), sort_order: newOrder, summary: "" }],
      });
      setDraft(updated);
    } catch (err) {
      showToast(err instanceof Error ? err.message : t("paper.addFailed"));
    } finally {
      setSaving(false);
    }
  };

  const handleExport = async () => {
    if (!draft) return;
    try {
      const md = await api.exportDraft(draft.id);
      const blob = new Blob([md], { type: "text/markdown" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${draft.title.replace(/[^a-zA-Z0-9\u4e00-\u9fff]/g, "_")}.md`;
      a.click();
      URL.revokeObjectURL(url);
      showToast(t("paper.exportSuccess"));
    } catch (err) {
      showToast(err instanceof Error ? err.message : t("paper.exportFailed"));
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="animate-spin text-cyan-400" size={24} />
      </div>
    );
  }

  if (error && !draft) {
    return (
      <div className="flex items-center justify-center h-full text-center p-8">
        <div>
          <p className="font-mono text-xs text-red-500">{t("paper.loadFailed")}</p>
          <p className="font-mono text-[10px] text-neutral-600 mt-1">{error}</p>
          <button
            onClick={() => navigate(-1)}
            className="mt-4 px-4 py-2 font-mono text-xs border border-neutral-800 text-neutral-400 hover:text-white hover:border-white transition-colors"
          >
            {t("common.back")}
          </button>
        </div>
      </div>
    );
  }

  if (!draft) return null;

  const completedCount = draft.sections.filter((s) => s.status === "completed").length;
  const progress = draft.sections.length > 0 ? completedCount / draft.sections.length : 0;

  return (
    <div className="flex flex-col h-full">
      <header className="px-6 py-3 border-b-2 border-neutral-800 flex items-center gap-4">
        <button
          onClick={() => navigate(-1)}
          className="text-neutral-600 hover:text-white transition-colors"
        >
          <ArrowLeft size={16} />
        </button>

        <div className="flex-1 min-w-0">
          {editingTitle ? (
            <div className="flex items-center gap-2">
              <input
                value={titleValue}
                onChange={(e) => setTitleValue(e.target.value)}
                onBlur={handleSaveTitle}
                onKeyDown={(e) => e.key === "Enter" && handleSaveTitle()}
                className="flex-1 px-2 py-1 bg-transparent border border-neutral-700 font-mono text-sm text-white focus:outline-none focus:border-cyan-400"
                autoFocus
              />
              {saving && <Loader2 size={12} className="animate-spin text-neutral-500" />}
            </div>
          ) : (
            <h1
              onClick={() => setEditingTitle(true)}
              className="font-mono text-sm text-white font-bold truncate cursor-pointer hover:text-cyan-300 transition-colors"
              title={t("paper.editTitle")}
            >
              {draft.title}
              <Pencil size={10} className="inline ml-2 text-neutral-700" />
            </h1>
          )}
          {draft.direction && (
            <p className="font-mono text-[9px] text-neutral-600 mt-0.5 truncate uppercase tracking-wider">
              {draft.direction}
            </p>
          )}
        </div>

        <div className="flex items-center gap-3">
          <div className="w-24 h-1 bg-neutral-800">
            <div
              className="h-full bg-cyan-400 transition-all duration-500"
              style={{ width: `${progress * 100}%` }}
            />
          </div>
          <span className="font-mono text-[9px] text-neutral-600">
            {completedCount}/{draft.sections.length}
          </span>
        </div>

        <button
          onClick={handleExport}
          className="flex items-center gap-1.5 px-3 py-1.5 border border-neutral-800 text-neutral-400 hover:text-white hover:border-white font-mono text-[10px] uppercase tracking-wider transition-colors"
        >
          <Download size={10} />
          {t("paper.exportMarkdown")}
        </button>
      </header>

      <main className="flex-1 overflow-y-auto px-6 py-5">
        <div className="max-w-4xl mx-auto space-y-2">
          <AnimatePresence mode="popLayout">
            {draft.sections.map((section, idx) => (
              <SectionCard
                key={section.id}
                section={section}
                index={idx}
                expanded={expandedId === section.id}
                onToggle={() =>
                  setExpandedId(expandedId === section.id ? null : section.id)
                }
                generating={genSectionId === section.id}
                onGenerate={() => handleGenerate(section.id)}
                onSave={(updates) => handleSaveSection(section.id, updates)}
                saving={saving}
              />
            ))}
          </AnimatePresence>

          <button
            onClick={handleAddSection}
            className="w-full py-3 border border-dashed border-neutral-800 hover:border-neutral-600 font-mono text-[10px] text-neutral-600 hover:text-neutral-300 flex items-center justify-center gap-2 uppercase tracking-wider transition-colors"
          >
            <Plus size={12} />
            {t("paper.newSection")}
          </button>
        </div>
      </main>

      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed bottom-6 left-1/2 -translate-x-1/2 px-4 py-2 bg-neutral-900 border border-neutral-700 font-mono text-xs text-neutral-300 shadow-lg z-50"
          >
            {toast}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

function SectionCard({
  section,
  index,
  expanded,
  onToggle,
  generating,
  onGenerate,
  onSave,
  saving,
}: {
  section: PaperSectionOut;
  index: number;
  expanded: boolean;
  onToggle: () => void;
  generating: boolean;
  onGenerate: () => void;
  onSave: (updates: SectionUpdate) => void;
  saving: boolean;
}) {
  const { t } = useTranslation();
  const [editingHeading, setEditingHeading] = useState(false);
  const [headingValue, setHeadingValue] = useState(section.heading);
  const [instructionValue, setInstructionValue] = useState(
    section.writing_instruction || ""
  );
  const [summaryValue, setSummaryValue] = useState(section.summary || "");

  useEffect(() => {
    setHeadingValue(section.heading);
    setSummaryValue(section.summary || "");
    setInstructionValue(section.writing_instruction || "");
  }, [section]);

  const statusIcon = () => {
    if (generating) return <Loader2 size={12} className="animate-spin text-cyan-400" />;
    if (section.status === "completed") return <Check size={12} className="text-cyan-400" />;
    return <FileText size={12} className="text-neutral-700" />;
  };

  const statusLabel = () => {
    if (generating) return t("paper.generating");
    if (section.status === "completed") return `v${section.version}`;
    return t("paper.pending");
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className={`border transition-colors ${
        expanded
          ? "border-cyan-400/30"
          : "border-neutral-800 hover:border-neutral-700"
      }`}
    >
      <div
        className="flex items-center gap-3 px-4 py-2.5 cursor-pointer"
        onClick={onToggle}
      >
        <span className="font-mono text-[9px] text-neutral-700 w-5 text-right">{index + 1}</span>

        {editingHeading ? (
          <input
            value={headingValue}
            onChange={(e) => setHeadingValue(e.target.value)}
            onBlur={() => {
              setEditingHeading(false);
              if (headingValue !== section.heading) {
                onSave({ heading: headingValue });
              }
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter") {
                setEditingHeading(false);
                if (headingValue !== section.heading) {
                  onSave({ heading: headingValue });
                }
              }
            }}
            onClick={(e) => e.stopPropagation()}
            className="flex-1 px-2 py-0.5 bg-transparent border border-neutral-700 font-mono text-xs text-white focus:outline-none focus:border-cyan-400"
            autoFocus
          />
        ) : (
          <h3
            className="flex-1 font-mono text-xs text-white truncate"
            onDoubleClick={(e) => {
              e.stopPropagation();
              setEditingHeading(true);
            }}
          >
            {section.heading}
          </h3>
        )}

        <div className="flex items-center gap-2">
          {statusIcon()}
          <span className="font-mono text-[9px] text-neutral-600">{statusLabel()}</span>
          {expanded ? (
            <ChevronUp size={12} className="text-neutral-700" />
          ) : (
            <ChevronDown size={12} className="text-neutral-700" />
          )}
        </div>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-4 pb-4 space-y-3 border-t border-neutral-800">
              <div className="pt-3">
                <label className="font-mono text-[9px] text-neutral-700 uppercase tracking-wider">
                  {t("paper.sectionDesc")}
                </label>
                <textarea
                  value={summaryValue}
                  onChange={(e) => setSummaryValue(e.target.value)}
                  onBlur={() => {
                    if (summaryValue !== (section.summary || "")) {
                      onSave({ summary: summaryValue });
                    }
                  }}
                  className="w-full mt-1 px-3 py-2 bg-transparent border border-neutral-800 font-mono text-[11px] text-neutral-400 focus:outline-none focus:border-cyan-400 resize-none"
                  rows={2}
                  placeholder={t("paper.sectionDescPlaceholder")}
                />
              </div>

              <div>
                <label className="font-mono text-[9px] text-neutral-700 uppercase tracking-wider">
                  {t("paper.writingInstruction")}
                </label>
                <textarea
                  value={instructionValue}
                  onChange={(e) => setInstructionValue(e.target.value)}
                  onBlur={() => {
                    if (instructionValue !== (section.writing_instruction || "")) {
                      onSave({ writing_instruction: instructionValue });
                    }
                  }}
                  className="w-full mt-1 px-3 py-2 bg-transparent border border-neutral-800 font-mono text-[11px] text-neutral-400 focus:outline-none focus:border-cyan-400 resize-none"
                  rows={2}
                  placeholder={t("paper.writingInstructionPlaceholder")}
                />
              </div>

              {section.content && (
                <div className="p-4 border border-neutral-800">
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-[9px] text-neutral-700 uppercase tracking-wider">
                      {t("paper.generatedContent", { version: section.version })}
                    </span>
                  </div>
                  <div className="font-mono text-[11px] text-neutral-300 leading-relaxed whitespace-pre-wrap max-h-96 overflow-y-auto">
                    {section.content}
                  </div>
                </div>
              )}

              <div className="flex items-center gap-2 pt-1">
                <button
                  onClick={onGenerate}
                  disabled={generating || saving}
                  className="flex items-center gap-2 px-3 py-1.5 bg-cyan-400 text-black font-mono text-[10px] font-bold uppercase tracking-wider hover:bg-cyan-300 disabled:opacity-40 transition-colors"
                >
                  {generating ? (
                    <Loader2 size={10} className="animate-spin" />
                  ) : section.content ? (
                    <RotateCcw size={10} />
                  ) : (
                    <Sparkles size={10} />
                  )}
                  {section.content ? t("paper.regenerate") : t("paper.generateContent")}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
