import { useState, useEffect, useCallback, useMemo } from "react";
import { useNavigate, useSearchParams, useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";
import i18n from "../i18n";
import {
  Sparkles,
  Swords,
  Users,
  Loader2,
  Play,
  Clock,
  ChevronRight,
  Settings2,
  Info,
} from "lucide-react";
import { api } from "../api/client";
import { useAuth } from "../contexts/AuthContext";
import type { Discipline, DebateBrief, ModeSuggestion } from "../types";

interface NavigationContext {
  intersectionTitle?: string;
  coreTension?: string;
  openQuestions?: string;
  hypothesis?: string;
  explanation?: string;
  direction?: string;
  discoveryQuestion?: string;
  isGap?: boolean;
}

function collectLeaves(nodes: Discipline[]): Discipline[] {
  const result: Discipline[] = [];
  for (const n of nodes) {
    if (!n.children || n.children.length === 0) result.push(n);
    else result.push(...collectLeaves(n.children));
  }
  return result;
}

export default function Debate() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const navCtx = (location.state as NavigationContext) || {};

  const [leaves, setLeaves] = useState<Discipline[]>([]);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [mode, setMode] = useState<"free" | "debate">("free");
  const [debateLang, setDebateLang] = useState<"zh" | "en">(() =>
    i18n.language?.startsWith("zh") ? "zh" : "en"
  );

  useEffect(() => {
    setDebateLang(i18n.language?.startsWith("zh") ? "zh" : "en");
  }, [i18n.language]);

  const [proposition, setProposition] = useState("");
  const [suggestion, setSuggestion] = useState<ModeSuggestion | null>(null);
  const [suggestLoading, setSuggestLoading] = useState(false);
  const [creating, setCreating] = useState(false);
  const [history, setHistory] = useState<DebateBrief[]>([]);
  const [search, setSearch] = useState("");
  const [toast, setToast] = useState<string | null>(null);
  const [showWeights, setShowWeights] = useState(false);
  const [weights, setWeights] = useState<Record<number, "core" | "support">>({});

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 4000);
  }, []);

  useEffect(() => {
    api.getDisciplines(user?.id).then((tree) => {
      setLeaves(collectLeaves(tree));
    }).catch((err) => {
      showToast(err instanceof Error ? err.message : t("debate.loadFailed"));
    });
    api.getDebates().then(setHistory).catch((err) => {
      showToast(err instanceof Error ? err.message : t("debate.historyLoadFailed"));
    });
  }, [showToast, t]);

  useEffect(() => {
    const raw = searchParams.get("disciplines");
    if (raw && leaves.length > 0) {
      const ids = raw.split(",").map(Number).filter((n) => !isNaN(n));
      setSelected(new Set(ids));
    }
  }, [searchParams, leaves]);

  useEffect(() => {
    if (!navCtx.coreTension && !navCtx.direction && !navCtx.hypothesis) return;
    const candidate =
      navCtx.hypothesis || navCtx.coreTension || navCtx.direction || "";
    if (candidate && !proposition) {
      setProposition(candidate);
      setMode("debate");
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const toggle = (id: number) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
    setSuggestion(null);
  };

  const handleSuggestMode = async () => {
    if (selected.size < 2) return;
    setSuggestLoading(true);
    try {
      const names = leaves
        .filter((d) => selected.has(d.id))
        .map((d) => d.name_en);
      const s = await api.suggestMode(names);
      setSuggestion(s);
      setMode(s.mode as "free" | "debate");
      if (s.suggested_proposition) setProposition(s.suggested_proposition);
    } catch (err) {
      showToast(err instanceof Error ? err.message : t("debate.modeSuggestFailed"));
    } finally {
      setSuggestLoading(false);
    }
  };

  const handleCreate = async () => {
    if (selected.size < 2) return;
    if (mode === "debate" && !proposition.trim()) return;
    setCreating(true);
    try {
      const intersectionId = searchParams.get("intersection");
      const dw: Record<number, number> = {};
      for (const [id, role] of Object.entries(weights)) {
        if (selected.has(Number(id))) {
          dw[Number(id)] = role === "core" ? 60 : 30;
        }
      }
      const debate = await api.createDebate({
        discipline_ids: [...selected],
        mode,
        proposition: mode === "debate" ? proposition : undefined,
        intersection_id: intersectionId ? Number(intersectionId) : undefined,
        discipline_weights: Object.keys(dw).length > 0 ? dw : undefined,
        language: debateLang,
      });
      navigate(`/debate/${debate.id}`);
    } catch (err) {
      showToast(err instanceof Error ? err.message : t("debate.createFailed"));
    } finally {
      setCreating(false);
    }
  };

  const hasAnyWeight = Object.keys(weights).some((id) => selected.has(Number(id)));
  const previewTeams = useMemo(() => {
    const sel = leaves.filter((d) => selected.has(d.id));
    const teams: { disc: Discipline; isCore: boolean | null; members: { name: string; rank: string }[] }[] = [];
    for (const d of sel) {
      const w = weights[d.id];
      const isCore = w ? w === "core" : hasAnyWeight ? false : null;
      const short = d.name_en.slice(0, 25);
      const zh = d.name_zh || d.name_en;
      const members =
        isCore === true
          ? [
              { name: `Prof. ${short} (${zh})`, rank: t("debateSession.rank.professor") },
              { name: `Assoc. Prof. ${short} (${zh})`, rank: t("debateSession.rank.associate") },
            ]
          : isCore === false
            ? [{ name: `Prof. ${short} (${zh})`, rank: t("debateSession.rank.professor") }]
            : [{ name: `${zh}`, rank: t("debate.aiAssigned") }];
      teams.push({ disc: d, isCore, members });
    }
    return teams;
  }, [leaves, selected, weights, hasAnyWeight, t]);

  const filtered = search
    ? leaves.filter(
        (d) =>
          d.name_en.toLowerCase().includes(search.toLowerCase()) ||
          (d.name_zh && d.name_zh.includes(search))
      )
    : leaves.slice(0, 40);

  const inputClass =
    "w-full mb-3 px-3 py-2 bg-[#0a0a0a] border-2 border-neutral-800 text-white placeholder-neutral-500 text-sm focus:outline-none focus:border-cyan-400";

  return (
    <div className="h-full overflow-y-auto bg-[#0a0a0a]">
      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="mb-10">
          <h1 className="text-2xl font-mono font-bold uppercase tracking-wider text-white">
            {t("debate.title")}
          </h1>
          <p className="text-neutral-400 mt-2 text-sm">{t("debate.subtitle")}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: config */}
          <div className="lg:col-span-2 space-y-6">
            {/* Context from graph/discovery */}
            {(navCtx.intersectionTitle || navCtx.discoveryQuestion) && (
              <section className="p-4 border-2 border-neutral-800 space-y-2 bg-[#0a0a0a]">
                <h3 className="font-mono text-[10px] uppercase tracking-wider text-cyan-400 flex items-center gap-1.5">
                  <Info size={12} />
                  {t("debate.contextTitle", {
                    source: navCtx.discoveryQuestion
                      ? t("debate.contextDiscovery")
                      : t("debate.contextGraph"),
                  })}
                </h3>
                {navCtx.intersectionTitle && (
                  <p className="text-sm text-white font-medium">
                    {navCtx.intersectionTitle}
                    {navCtx.isGap && (
                      <span className="ml-2 text-[10px] px-1.5 py-0.5 border border-red-500 text-red-400 uppercase font-mono tracking-wider">
                        {t("canvas.researchGap")}
                      </span>
                    )}
                  </p>
                )}
                {navCtx.discoveryQuestion && (
                  <p className="text-xs text-neutral-400">
                    <span className="text-neutral-500">{t("discovery.question")}: </span>
                    {navCtx.discoveryQuestion}
                  </p>
                )}
                {navCtx.coreTension && (
                  <p className="text-xs text-neutral-400">
                    <span className="text-neutral-500">{t("debate.contextCoreTension")}: </span>
                    {navCtx.coreTension}
                  </p>
                )}
                {navCtx.explanation && (
                  <p className="text-xs text-neutral-400">
                    <span className="text-neutral-500">{t("debate.contextExplanation")}: </span>
                    {navCtx.explanation}
                  </p>
                )}
                {navCtx.direction && (
                  <p className="text-xs text-neutral-400">
                    <span className="text-neutral-500">{t("debate.contextDirection")}: </span>
                    {navCtx.direction}
                  </p>
                )}
                {navCtx.openQuestions && (
                  <p className="text-xs text-neutral-400">
                    <span className="text-neutral-500">{t("debate.contextOpenQuestions")}: </span>
                    {navCtx.openQuestions}
                  </p>
                )}
                {navCtx.hypothesis && (
                  <p className="text-xs text-cyan-400">
                    <span className="text-neutral-500">{t("debate.contextHypothesis")}: </span>
                    {navCtx.hypothesis}
                  </p>
                )}
              </section>
            )}

            {/* Discipline picker */}
            <section className="p-5 border-2 border-neutral-800 bg-[#0a0a0a]">
              <h3 className="font-mono text-[10px] uppercase tracking-wider text-neutral-400 mb-3">
                {t("debate.selectDisciplines")}
              </h3>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={t("debate.searchDisciplines")}
                className={inputClass}
              />
              <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto">
                {filtered.map((d) => (
                  <button
                    key={d.id}
                    onClick={() => toggle(d.id)}
                    className={`px-3 py-1.5 text-xs font-mono uppercase tracking-wider border-2 transition-colors ${
                      selected.has(d.id)
                        ? "border-cyan-400 bg-cyan-400/10 text-cyan-400"
                        : "border-neutral-800 text-neutral-400 hover:border-neutral-600 hover:text-white"
                    }`}
                  >
                    {d.name_zh || d.name_en}
                  </button>
                ))}
              </div>
              {selected.size > 0 && (
                <p className="text-xs text-neutral-500 mt-2 font-mono">
                  {t("debate.selected", { count: selected.size })}
                </p>
              )}
            </section>

            {/* Mode picker */}
            <section className="p-5 border-2 border-neutral-800 bg-[#0a0a0a]">
              <div className="flex items-center justify-between mb-3">
                <h3 className="font-mono text-[10px] uppercase tracking-wider text-neutral-400">
                  {t("debate.mode")}
                </h3>
                {selected.size >= 2 && (
                  <button
                    onClick={handleSuggestMode}
                    disabled={suggestLoading}
                    className="flex items-center gap-1 px-3 py-1 text-xs border-2 border-cyan-400 text-cyan-400 font-mono font-bold uppercase tracking-wider hover:bg-cyan-400/10 disabled:opacity-50"
                  >
                    {suggestLoading ? (
                      <Loader2 size={12} className="animate-spin" />
                    ) : (
                      <Sparkles size={12} />
                    )}
                    {t("debate.aiRecommend")}
                  </button>
                )}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setMode("free")}
                  className={`p-4 border-2 text-left transition-colors ${
                    mode === "free"
                      ? "border-cyan-400 bg-cyan-400/5"
                      : "border-neutral-800 bg-[#0a0a0a] hover:border-neutral-600"
                  }`}
                >
                  <Users size={20} className="text-cyan-400 mb-2" />
                  <p className="text-sm font-mono font-bold uppercase tracking-wider text-white">
                    {t("debate.freeDiscussion")}
                  </p>
                  <p className="text-xs text-neutral-500 mt-1">{t("debate.freeDesc")}</p>
                </button>
                <button
                  onClick={() => setMode("debate")}
                  className={`p-4 border-2 text-left transition-colors ${
                    mode === "debate"
                      ? "border-cyan-400 bg-cyan-400/5"
                      : "border-neutral-800 bg-[#0a0a0a] hover:border-neutral-600"
                  }`}
                >
                  <Swords size={20} className="text-red-400 mb-2" />
                  <p className="text-sm font-mono font-bold uppercase tracking-wider text-white">
                    {t("debate.structuredDebate")}
                  </p>
                  <p className="text-xs text-neutral-500 mt-1">{t("debate.structuredDesc")}</p>
                </button>
              </div>
              {suggestion && (
                <div className="mt-3 p-3 border-2 border-cyan-400/40 bg-cyan-400/5">
                  <p className="text-xs text-cyan-400 font-mono">
                    <Sparkles size={12} className="inline mr-1" />
                    {t("debate.suggestionWithReason", { reason: i18n.language?.startsWith("zh") ? suggestion.reason_zh : suggestion.reason_en })}
                  </p>
                </div>
              )}
              {mode === "debate" && (
                <div className="mt-4">
                  <label className="font-mono text-[10px] uppercase tracking-wider text-neutral-400 mb-1 block">
                    {t("debate.proposition")}
                  </label>
                  <textarea
                    value={proposition}
                    onChange={(e) => setProposition(e.target.value)}
                    placeholder={t("debate.propositionPlaceholder")}
                    rows={2}
                    className={`${inputClass} resize-none mb-0`}
                  />
                </div>
              )}
            </section>

            {/* Language selector */}
            <section className="p-5 border-2 border-neutral-800 bg-[#0a0a0a]">
              <h3 className="font-mono text-[10px] uppercase tracking-wider text-neutral-400 mb-3">
                {t("debate.language")}
              </h3>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setDebateLang("zh")}
                  className={`p-3 border-2 text-center transition-colors ${
                    debateLang === "zh"
                      ? "border-cyan-400 bg-cyan-400/5"
                      : "border-neutral-800 bg-[#0a0a0a] hover:border-neutral-600"
                  }`}
                >
                  <p className="text-sm font-mono font-bold uppercase tracking-wider text-white">
                    {t("debate.langZh")}
                  </p>
                  <p className="text-xs text-neutral-500 mt-0.5">{t("debate.langZhDesc")}</p>
                </button>
                <button
                  onClick={() => setDebateLang("en")}
                  className={`p-3 border-2 text-center transition-colors ${
                    debateLang === "en"
                      ? "border-cyan-400 bg-cyan-400/5"
                      : "border-neutral-800 bg-[#0a0a0a] hover:border-neutral-600"
                  }`}
                >
                  <p className="text-sm font-mono font-bold uppercase tracking-wider text-white">
                    {t("debate.langEn")}
                  </p>
                  <p className="text-xs text-neutral-500 mt-0.5">{t("debate.langEnDesc")}</p>
                </button>
              </div>
            </section>

            {/* Weight settings */}
            {selected.size >= 2 && (
              <section className="p-5 border-2 border-neutral-800 bg-[#0a0a0a]">
                <button
                  onClick={() => setShowWeights(!showWeights)}
                  className="flex items-center gap-2 text-sm text-neutral-400 hover:text-neutral-200 transition-colors w-full"
                >
                  <Settings2 size={14} />
                  <span className="font-mono text-[10px] uppercase tracking-wider">
                    {t("debate.weightSettings")}
                  </span>
                  <span className="text-[10px] text-neutral-600 ml-auto font-mono">
                    {showWeights ? t("debate.collapse") : t("debate.weightOptional")}
                  </span>
                </button>
                {showWeights && (
                  <div className="mt-3 space-y-2">
                    <p className="text-[10px] text-neutral-500 mb-2 font-mono">
                      {t("debate.weightCoreHint")}
                    </p>
                    {leaves.filter((d) => selected.has(d.id)).map((d) => (
                      <div key={d.id} className="flex items-center gap-3">
                        <span className="text-xs text-neutral-300 truncate flex-1">
                          {d.name_zh || d.name_en}
                        </span>
                        <div className="flex gap-1">
                          <button
                            onClick={() => setWeights((prev) => ({ ...prev, [d.id]: "core" }))}
                            className={`px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider border-2 transition-colors ${
                              weights[d.id] === "core"
                                ? "border-yellow-500 text-yellow-400 bg-yellow-500/10"
                                : "border-neutral-800 text-neutral-500 hover:text-neutral-300"
                            }`}
                          >
                            {t("debate.core")}
                          </button>
                          <button
                            onClick={() => setWeights((prev) => ({ ...prev, [d.id]: "support" }))}
                            className={`px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider border-2 transition-colors ${
                              weights[d.id] === "support"
                                ? "border-sky-500 text-sky-400 bg-sky-500/10"
                                : "border-neutral-800 text-neutral-500 hover:text-neutral-300"
                            }`}
                          >
                            {t("debate.support")}
                          </button>
                          {weights[d.id] && (
                            <button
                              onClick={() => setWeights((prev) => {
                                const next = { ...prev };
                                delete next[d.id];
                                return next;
                              })}
                              className="px-1 text-[10px] text-neutral-600 hover:text-neutral-400"
                            >
                              &times;
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            )}

            {/* Start button */}
            <button
              onClick={handleCreate}
              disabled={selected.size < 2 || creating || (mode === "debate" && !proposition.trim())}
              className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-cyan-400 text-black font-mono text-xs font-bold uppercase tracking-wider hover:bg-cyan-300 disabled:opacity-40 disabled:cursor-not-allowed border-2 border-cyan-400"
            >
              {creating ? (
                <Loader2 size={18} className="animate-spin" />
              ) : (
                <Play size={18} />
              )}
              {t("debate.startDebate")}
            </button>
          </div>

          {/* Right: agent preview + history */}
          <div className="space-y-6">
            {/* Agent preview */}
            {selected.size >= 2 && (
              <section className="p-5 border-2 border-neutral-800 bg-[#0a0a0a]">
                <h3 className="font-mono text-[10px] uppercase tracking-wider text-neutral-400 mb-3">
                  {t("debate.agentPreview")}
                </h3>
                <div className="space-y-3">
                  {previewTeams.map((team) => (
                    <div key={team.disc.id}>
                      <p className="text-[10px] text-neutral-500 mb-1 flex items-center gap-1 font-mono uppercase tracking-wider">
                        {team.disc.name_zh || team.disc.name_en}
                        {team.isCore === true && <span className="text-yellow-500/70">&#9733;</span>}
                      </p>
                      {team.members.map((m, j) => (
                        <div
                          key={j}
                          className="flex items-center gap-2 p-2 border border-neutral-800 bg-[#0a0a0a] mb-1"
                        >
                          <div className="w-7 h-7 border border-neutral-800 flex items-center justify-center text-xs font-mono font-bold text-white shrink-0">
                            {m.rank[0]}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-xs text-white truncate">{m.name}</p>
                            <span
                              className={`text-[10px] font-mono uppercase tracking-wider ${
                                j === 0 ? "text-yellow-400" : "text-sky-400"
                              }`}
                            >
                              {m.rank}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ))}
                  <div className="flex items-center gap-2 p-2 border border-neutral-800 bg-[#0a0a0a]">
                    <div className="w-7 h-7 border border-cyan-400/50 flex items-center justify-center text-xs font-mono font-bold text-cyan-400 shrink-0">
                      M
                    </div>
                    <div className="flex-1">
                      <p className="text-xs text-white font-mono">{t("debate.moderatorSubtitle")}</p>
                      <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400">
                        {t("debate.moderator")}
                      </span>
                    </div>
                  </div>
                </div>
                <p className="text-[10px] text-neutral-600 mt-2 font-mono">
                  {hasAnyWeight ? t("debate.hasWeightHint") : t("debate.noWeightHint")}
                </p>
              </section>
            )}

            {/* History */}
            <section className="p-5 border-2 border-neutral-800 bg-[#0a0a0a]">
              <h3 className="font-mono text-[10px] uppercase tracking-wider text-neutral-400 mb-3 flex items-center gap-1.5">
                <Clock size={14} />
                {t("debate.history")}
              </h3>
              {history.length === 0 ? (
                <p className="text-xs text-neutral-500 font-mono">{t("debate.noHistory")}</p>
              ) : (
                <div className="space-y-2">
                  {history.slice(0, 10).map((d) => (
                    <button
                      key={d.id}
                      onClick={() => navigate(`/debate/${d.id}`)}
                      className="w-full flex items-center justify-between p-2 border border-neutral-800 bg-[#0a0a0a] hover:border-neutral-600 transition-colors text-left"
                    >
                      <div className="min-w-0">
                        <p className="text-xs text-white truncate">{d.title}</p>
                        <div className="flex items-center gap-1.5 mt-0.5">
                          <span className="text-[10px] text-neutral-500 font-mono uppercase">
                            {d.mode === "free"
                              ? t("debate.freeDiscussion")
                              : t("debate.structuredDebate")}
                          </span>
                          <span
                            className={`text-[10px] px-1 font-mono uppercase tracking-wider border ${
                              d.status === "completed"
                                ? "border-green-500/50 text-green-400"
                                : d.status === "active"
                                  ? "border-blue-500/50 text-blue-400"
                                  : "border-amber-500/50 text-amber-400"
                            }`}
                          >
                            {d.status === "completed"
                              ? t("debate.statusCompleted")
                              : d.status === "active"
                                ? t("debate.statusActive")
                                : t("debate.statusSummarizing")}
                          </span>
                        </div>
                      </div>
                      <ChevronRight size={14} className="text-neutral-600 shrink-0" />
                    </button>
                  ))}
                </div>
              )}
            </section>
          </div>
        </div>

        {toast && (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50 px-4 py-2 bg-red-500 text-white text-sm font-mono shadow-lg border-2 border-red-600">
            {toast}
          </div>
        )}
      </div>
    </div>
  );
}
