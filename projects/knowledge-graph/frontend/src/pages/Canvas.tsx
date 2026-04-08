import { useState, useCallback, useEffect, useRef } from "react";
import { useSearchParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import i18n from "../i18n";
import {
  Loader2,
  PanelLeftClose,
  PanelLeftOpen,
  PanelRightOpen,
  AlertCircle,
  Search,
  ArrowRight,
} from "lucide-react";
import DisciplineTree from "../components/DisciplinePanel/DisciplineTree";
import ForceGraph from "../components/GraphCanvas/ForceGraph";
import DetailPanel from "../components/DetailPanel/DetailPanel";
import type { AgentAction } from "../components/DetailPanel/DetailPanel";
import EdgeDetailPanel from "../components/EdgeDetailPanel/EdgeDetailPanel";
import DiscoveryPanel from "../components/DiscoveryPanel/DiscoveryPanel";
import { useDisciplines } from "../hooks/useDisciplines";
import { useAuth } from "../contexts/AuthContext";
import { api } from "../api/client";
import type { Discipline, DiscoveryResult, GraphData } from "../types";

function collectLeaves(nodes: Discipline[]): Discipline[] {
  const result: Discipline[] = [];
  for (const n of nodes) {
    if (!n.children || n.children.length === 0) {
      result.push(n);
    } else {
      result.push(...collectLeaves(n.children));
    }
  }
  return result;
}

function findNode(nodes: Discipline[], id: number): Discipline | null {
  for (const n of nodes) {
    if (n.id === id) return n;
    if (n.children) {
      const found = findNode(n.children, id);
      if (found) return found;
    }
  }
  return null;
}

export default function Canvas() {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();
  const { tree, loading: treeLoading, error: treeError, refresh: refreshTree } = useDisciplines();
  const { user } = useAuth();

  const [selectedNodes, setSelectedNodes] = useState<Set<number>>(new Set());
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [graphLoading, setGraphLoading] = useState(false);
  const [graphError, setGraphError] = useState<string | null>(null);
  const [activeIntersection, setActiveIntersection] = useState<number | null>(null);
  const [activeEdgePair, setActiveEdgePair] = useState<[number, number] | null>(null);
  const [generating, setGenerating] = useState(false);
  const [leftOpen, setLeftOpen] = useState(true);
  const [rightOpen, setRightOpen] = useState(true);
  const [toast, setToast] = useState<string | null>(null);
  const [glowingIds, setGlowingIds] = useState<Set<number>>(new Set());

  const [leftWidth, setLeftWidth] = useState(280);
  const [rightWidth, setRightWidth] = useState(360);
  const draggingRef = useRef<"left" | "right" | null>(null);
  const startXRef = useRef(0);
  const startWidthRef = useRef(0);

  const handleDragStart = useCallback(
    (side: "left" | "right") => (e: React.MouseEvent) => {
      e.preventDefault();
      draggingRef.current = side;
      startXRef.current = e.clientX;
      startWidthRef.current = side === "left" ? leftWidth : rightWidth;

      const onMove = (ev: MouseEvent) => {
        const delta = ev.clientX - startXRef.current;
        const maxW = window.innerWidth * 0.4;
        if (draggingRef.current === "left") {
          setLeftWidth(Math.max(200, Math.min(maxW, startWidthRef.current + delta)));
        } else {
          setRightWidth(Math.max(240, Math.min(maxW, startWidthRef.current - delta)));
        }
      };
      const onUp = () => {
        draggingRef.current = null;
        document.removeEventListener("mousemove", onMove);
        document.removeEventListener("mouseup", onUp);
        document.body.style.cursor = "";
        document.body.style.userSelect = "";
      };
      document.addEventListener("mousemove", onMove);
      document.addEventListener("mouseup", onUp);
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    },
    [leftWidth, rightWidth],
  );

  const [discoveryResult, setDiscoveryResult] = useState<DiscoveryResult | null>(null);
  const [discoverQuery, setDiscoverQuery] = useState("");
  const [discoverLoading, setDiscoverLoading] = useState(false);

  useEffect(() => {
    if (selectedNodes.size === 0) {
      setGraphData({ nodes: [], edges: [] });
      return;
    }
    let cancelled = false;
    setGraphLoading(true);
    setGraphError(null);
    api.getGraph([...selectedNodes]).then((data) => {
      if (!cancelled) setGraphData(data);
    }).catch((err) => {
      if (!cancelled) setGraphError(err instanceof Error ? err.message : t("canvas.loadFailed"));
    }).finally(() => {
      if (!cancelled) setGraphLoading(false);
    });
    return () => { cancelled = true; };
  }, [selectedNodes, t]);

  const showToast = useCallback((msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 4000);
  }, []);

  useEffect(() => {
    if (treeLoading) return;

    const fieldId = searchParams.get("field");
    const q = searchParams.get("q");
    const isDiscover = searchParams.get("discover");

    if (isDiscover) {
      try {
        const raw = sessionStorage.getItem("discoveryResult");
        if (raw) {
          const result: DiscoveryResult = JSON.parse(raw);
          sessionStorage.removeItem("discoveryResult");
          setDiscoveryResult(result);
          setDiscoverQuery(result.question);

          const allIds = new Set<number>();
          for (const m of result.matched_disciplines) allIds.add(m.discipline_id);
          if (allIds.size > 0) {
            setSelectedNodes(allIds);
            setGlowingIds(new Set(allIds));
          }
          setRightOpen(true);
        }
      } catch {
        /* ignore malformed data */
      }
      setSearchParams({}, { replace: true });
      return;
    }

    if (!fieldId && !q) return;

    if (fieldId) {
      const id = Number(fieldId);
      if (!isNaN(id)) {
        const node = findNode(tree, id);
        if (node) {
          const leaves = collectLeaves([node]);
          if (leaves.length > 0) {
            const sorted = [...leaves].sort(
              (a, b) => (b.works_count ?? 0) - (a.works_count ?? 0),
            );
            setSelectedNodes(new Set(sorted.slice(0, 15).map((d) => d.id)));
          } else {
            setSelectedNodes(new Set([id]));
          }
        } else {
          setSelectedNodes(new Set([id]));
        }
      }
    } else if (q) {
      const keyword = q.toLowerCase();
      const leaves = collectLeaves(tree);
      const matched = leaves.filter(
        (d) =>
          d.name_en.toLowerCase().includes(keyword) ||
          (d.name_zh && d.name_zh.includes(q))
      );
      if (matched.length > 0) {
        setSelectedNodes(new Set(matched.slice(0, 5).map((d) => d.id)));
      }
    }

    setSearchParams({}, { replace: true });
  }, [treeLoading, tree, searchParams, setSearchParams]);

  const handleDiscover = useCallback(async () => {
    const q = discoverQuery.trim();
    if (!q) return;
    setDiscoverLoading(true);
    setDiscoveryResult(null);
    try {
      const result = await api.discover(q);
      setDiscoveryResult(result);

      const allIds = new Set<number>();
      for (const m of result.matched_disciplines) allIds.add(m.discipline_id);
      if (allIds.size > 0) {
        setSelectedNodes(allIds);
        setGlowingIds(new Set(allIds));
      }
      setRightOpen(true);
    } catch (err) {
      showToast(err instanceof Error ? err.message : t("home.analyzeFailed"));
    } finally {
      setDiscoverLoading(false);
    }
  }, [discoverQuery, showToast, t]);

  const handleDiscoverSelectCombo = useCallback((ids: number[]) => {
    setSelectedNodes(new Set(ids));
    setDiscoveryResult(null);
    setActiveIntersection(null);
    setActiveEdgePair(null);
  }, []);

  const handleDiscoverHypothesis = useCallback(
    async (ids: number[]) => {
      setSelectedNodes(new Set(ids));
      setGenerating(true);
      try {
        const lang = i18n.language?.startsWith("zh") ? "zh" : "en";
        await api.generateHypothesis(ids, undefined, lang);
        const results = await api.queryIntersections(ids);
        if (results.length > 0) {
          setActiveIntersection(results[0].id);
          setDiscoveryResult(null);
          setRightOpen(true);
        }
      } catch (err) {
        showToast(err instanceof Error ? err.message : t("canvas.generateHypothesisFailed"));
      } finally {
        setGenerating(false);
      }
    },
    [showToast, t]
  );

  const handleNodeToggle = useCallback((id: number) => {
    setSelectedNodes((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const handleEdgeClick = useCallback((intersectionId: number) => {
    setActiveEdgePair(null);
    setActiveIntersection(intersectionId);
    setRightOpen(true);
  }, []);

  const handleEvidenceEdgeClick = useCallback((sourceId: number, targetId: number) => {
    setActiveIntersection(null);
    setActiveEdgePair([sourceId, targetId]);
    setRightOpen(true);
  }, []);

  const handleNodeClick = useCallback(
    (nodeId: number) => handleNodeToggle(nodeId),
    [handleNodeToggle]
  );

  const allLeaves = useCallback(() => collectLeaves(tree), [tree]);

  const selectedDisciplineNames = useCallback((): string[] => {
    const leaves = allLeaves();
    const isZh = i18n.language?.startsWith("zh");
    return [...selectedNodes].map((id) => {
      const d = leaves.find((l) => l.id === id);
      if (!d) return String(id);
      return isZh ? (d.name_zh || d.name_en) : d.name_en;
    });
  }, [selectedNodes, allLeaves]);

  const findBestParent = useCallback(
    (name: string): Discipline | null => {
      const lower = (s: string) => s.toLowerCase().trim();
      const all = allLeaves();
      for (const d of tree) {
        if (
          lower(d.name_en).includes(lower(name)) ||
          (d.name_zh && d.name_zh.includes(name.trim()))
        ) {
          return d;
        }
        if (d.children) {
          for (const c of d.children) {
            if (
              lower(c.name_en).includes(lower(name)) ||
              (c.name_zh && c.name_zh.includes(name.trim()))
            ) {
              return c;
            }
          }
        }
      }
      const firstSelected = all.find((d) => selectedNodes.has(d.id));
      if (firstSelected?.parent_id) {
        const parent = tree.flatMap((t) => [t, ...(t.children || [])]).find(
          (d) => d.id === firstSelected.parent_id,
        );
        if (parent) return parent;
      }
      return null;
    },
    [tree, allLeaves, selectedNodes],
  );

  const handleAgentAction = useCallback(
    (action: AgentAction) => {
      const leaves = allLeaves();
      const lower = (s: string) => s.toLowerCase().trim();

      if (action.type === "remove_discipline") {
        const name = String(action.payload?.name || "");
        const match = leaves.find(
          (d) =>
            lower(d.name_en) === lower(name) ||
            (d.name_zh && d.name_zh === name.trim()),
        );
        if (match && selectedNodes.has(match.id)) {
          setSelectedNodes((prev) => {
            const next = new Set(prev);
            next.delete(match.id);
            return next;
          });
          setActiveIntersection(null);
        } else {
          showToast(
            i18n.language?.startsWith("zh")
              ? `未找到已选学科「${name}」`
              : `Discipline "${name}" not found in selection`,
          );
        }
      } else if (action.type === "add_discipline") {
        const name = String(action.payload?.name || "");
        const match = leaves.find(
          (d) =>
            lower(d.name_en) === lower(name) ||
            lower(d.name_en).includes(lower(name)) ||
            (d.name_zh && d.name_zh.includes(name.trim())),
        );
        if (match) {
          setSelectedNodes((prev) => new Set([...prev, match.id]));
        } else if (user) {
          const parent = findBestParent(name);
          api
            .createDiscipline({
              name_en: name,
              name_zh: action.payload?.name_zh as string | undefined,
              parent_id: parent?.id,
              created_by: user.id,
            })
            .then((newDisc) => {
              refreshTree();
              setSelectedNodes((prev) => new Set([...prev, newDisc.id]));
              showToast(
                i18n.language?.startsWith("zh")
                  ? `已创建学科「${name}」并同步论文数据`
                  : `Created "${name}" and synced paper data`,
              );
            })
            .catch((err) => {
              showToast(
                err instanceof Error ? err.message : "Failed to create discipline",
              );
            });
        } else {
          showToast(
            i18n.language?.startsWith("zh")
              ? `未找到学科「${name}」，登录后可自动创建`
              : `"${name}" not found. Log in to create it.`,
          );
        }
      } else if (action.type === "start_debate") {
        if (selectedNodes.size >= 2) {
          const ids = [...selectedNodes].join(",");
          window.location.href = `/debate?disciplines=${ids}`;
        } else {
          showToast(
            i18n.language?.startsWith("zh")
              ? "至少选择 2 个学科才能发起辩论"
              : "Select at least 2 disciplines to start a debate",
          );
        }
      } else if (action.type === "clear_all") {
        setSelectedNodes(new Set());
        setDiscoveryResult(null);
        setActiveIntersection(null);
        setActiveEdgePair(null);
      }
    },
    [allLeaves, selectedNodes, showToast, user, findBestParent, refreshTree],
  );

  const handleQueryIntersections = useCallback(async () => {
    if (selectedNodes.size < 2) return;
    try {
      const results = await api.queryIntersections([...selectedNodes]);
      if (results.length > 0) {
        setActiveIntersection(results[0].id);
        setRightOpen(true);
      } else {
        showToast(t("canvas.noIntersection"));
        const ids = [...selectedNodes];
        setGenerating(true);
        try {
          const lang = i18n.language?.startsWith("zh") ? "zh" : "en";
          const hyp = await api.generateHypothesis(ids, undefined, lang);
          if (hyp) {
            const freshResults = await api.queryIntersections(ids);
            if (freshResults.length > 0) {
              setActiveIntersection(freshResults[0].id);
              setRightOpen(true);
            }
          }
        } catch {
          showToast(t("canvas.autoHypothesisFailed"));
        } finally {
          setGenerating(false);
        }
      }
    } catch (err) {
      showToast(err instanceof Error ? err.message : t("canvas.queryIntersectionFailed"));
    }
  }, [selectedNodes, showToast, t]);

  return (
    <div className="flex h-full">
      {/* Left: Discipline Tree */}
      <aside
        className={`border-r-2 border-neutral-800 shrink-0 flex flex-col ${
          leftOpen ? "" : "w-0 overflow-hidden"
        }`}
        style={leftOpen ? { width: leftWidth } : undefined}
      >
        <div className="px-3 py-2.5 border-b border-neutral-800 flex items-center justify-between">
          <h2 className="font-mono text-[10px] font-bold text-neutral-500 uppercase tracking-[0.15em]">
            {t("canvas.disciplines")}
          </h2>
          <button
            onClick={() => setLeftOpen(false)}
            className="p-1 hover:bg-neutral-900 text-neutral-600 hover:text-white transition-colors"
          >
            <PanelLeftClose size={12} />
          </button>
        </div>
        {treeLoading ? (
          <div className="flex items-center justify-center flex-1">
            <Loader2 className="animate-spin text-gray-500" size={20} />
          </div>
        ) : treeError ? (
          <div className="flex items-center justify-center flex-1 px-4 text-center">
            <p className="text-xs text-red-400">{treeError}</p>
          </div>
        ) : (
          <DisciplineTree
            tree={tree}
            selectedIds={selectedNodes}
            onToggle={handleNodeToggle}
            glowingIds={glowingIds}
            onGlowDismiss={(id) => setGlowingIds((prev) => {
              const next = new Set(prev);
              next.delete(id);
              return next;
            })}
          />
        )}
      </aside>

      {leftOpen && (
        <div
          onMouseDown={handleDragStart("left")}
          className="w-1 shrink-0 cursor-col-resize hover:bg-cyan-400/40 active:bg-cyan-400/60 transition-colors"
        />
      )}

      {!leftOpen && (
        <button
          onClick={() => setLeftOpen(true)}
          className="flex items-center px-1 border-r border-white/10 hover:bg-white/5 text-gray-500 hover:text-white transition-colors"
        >
          <PanelLeftOpen size={14} />
        </button>
      )}

      {/* Center: Force Graph */}
      <main className="flex-1 min-w-0 relative flex flex-col">
        {/* Discovery search bar */}
        <div className="shrink-0 px-4 py-2 border-b border-white/10 flex items-center gap-2">
          <div className="relative flex-1 max-w-lg">
            <Search
              size={14}
              className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500"
            />
            <input
              type="text"
              value={discoverQuery}
              onChange={(e) => setDiscoverQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleDiscover()}
              disabled={discoverLoading}
              placeholder={t("home.inputPlaceholder")}
              className="w-full pl-8 pr-3 py-1.5 rounded-lg bg-white/5 border border-white/10 text-white placeholder-gray-500 text-sm focus:outline-none focus:ring-1 focus:ring-violet-500/50 disabled:opacity-50"
            />
          </div>
          <button
            onClick={handleDiscover}
            disabled={discoverLoading || !discoverQuery.trim()}
            className="flex items-center gap-1 px-3 py-1.5 bg-violet-600 hover:bg-violet-500 disabled:opacity-40 text-sm text-white rounded-lg transition-colors"
          >
            {discoverLoading ? (
              <Loader2 size={14} className="animate-spin" />
            ) : (
              <ArrowRight size={14} />
            )}
            {t("canvas.discover")}
          </button>
          {selectedNodes.size > 0 && (
            <div className="flex items-center gap-2 ml-2 pl-2 border-l border-white/10">
              <span className="text-xs text-gray-500">
                {t("canvas.selected_count", { count: selectedNodes.size })}
              </span>
              {selectedNodes.size >= 2 && (
                <button
                  onClick={handleQueryIntersections}
                  className="px-2 py-1 bg-violet-600/80 hover:bg-violet-500 text-xs rounded-lg transition-colors"
                >
                  {t("canvas.queryIntersection")}
                </button>
              )}
              <button
                onClick={() => {
                  setSelectedNodes(new Set());
                  setDiscoveryResult(null);
                  setActiveIntersection(null);
                  setActiveEdgePair(null);
                }}
                className="px-2 py-1 bg-white/5 hover:bg-white/10 text-xs text-gray-400 rounded-lg transition-colors"
              >
                {t("canvas.clear")}
              </button>
            </div>
          )}
        </div>

        {/* Graph area */}
        <div className="flex-1 min-h-0 relative">

        {graphLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-950/80 z-10">
            <Loader2 className="animate-spin text-violet-400" size={32} />
          </div>
        )}
        {graphError && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center p-8">
              <p className="text-red-400 text-sm mb-2">{t("canvas.loadFailed")}</p>
              <p className="text-gray-500 text-xs">{graphError}</p>
            </div>
          </div>
        )}
        {graphData && graphData.nodes.length > 0 ? (
          <ForceGraph
            data={graphData}
            onNodeClick={handleNodeClick}
            onEdgeClick={handleEdgeClick}
            onEvidenceEdgeClick={handleEvidenceEdgeClick}
            selectedNodes={selectedNodes}
          />
        ) : !graphLoading && !graphError && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center p-8 max-w-sm">
              <div className="text-4xl mb-4">—</div>
              <p className="text-gray-400 text-sm mb-1">{t("canvas.emptyState")}</p>
              <p className="text-gray-600 text-xs">{t("canvas.queryHint")}</p>
            </div>
          </div>
        )}
        {generating && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-950/60 z-10">
            <div className="flex items-center gap-2 px-4 py-2 bg-violet-600 rounded-xl">
              <Loader2 className="animate-spin" size={16} />
              <span className="text-sm">{t("canvas.generatingHypothesis")}</span>
            </div>
          </div>
        )}
        {toast && (
          <div className="absolute bottom-4 left-1/2 -translate-x-1/2 z-30 max-w-md">
            <div className="flex items-start gap-2 px-4 py-3 bg-gray-900/95 backdrop-blur border border-white/10 rounded-xl shadow-lg">
              <AlertCircle size={16} className="text-amber-400 mt-0.5 shrink-0" />
              <p className="text-sm text-gray-300">{toast}</p>
            </div>
          </div>
        )}
        </div>{/* end graph area */}
      </main>

      {!rightOpen && (
        <button
          onClick={() => setRightOpen(true)}
          className="flex items-center px-1 border-l border-white/10 hover:bg-white/5 text-gray-500 hover:text-white transition-colors"
        >
          <PanelRightOpen size={14} />
        </button>
      )}

      {rightOpen && (
        <div
          onMouseDown={handleDragStart("right")}
          className="w-1 shrink-0 cursor-col-resize hover:bg-cyan-400/40 active:bg-cyan-400/60 transition-colors"
        />
      )}

      {/* Right: Detail Panel or Discovery Panel */}
      <aside
        className={`border-l border-white/10 shrink-0 ${
          rightOpen ? "" : "w-0 overflow-hidden"
        }`}
        style={rightOpen ? { width: rightWidth } : undefined}
      >
        {discoveryResult ? (
          <DiscoveryPanel
            result={discoveryResult}
            onClose={() => {
              setDiscoveryResult(null);
              setRightOpen(false);
            }}
            onSelectCombo={handleDiscoverSelectCombo}
            onGenerateHypothesis={handleDiscoverHypothesis}
          />
        ) : activeEdgePair ? (
          <EdgeDetailPanel
            sourceId={activeEdgePair[0]}
            targetId={activeEdgePair[1]}
            onClose={() => setActiveEdgePair(null)}
          />
        ) : (
          <DetailPanel
            intersectionId={activeIntersection}
            onClose={() => setActiveIntersection(null)}
            onAgentAction={handleAgentAction}
            selectedDisciplineNames={selectedDisciplineNames()}
            selectedNodeIds={[...selectedNodes]}
          />
        )}
      </aside>
    </div>
  );
}
