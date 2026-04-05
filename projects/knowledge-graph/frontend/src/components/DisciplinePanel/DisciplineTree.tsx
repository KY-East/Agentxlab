import { useState, useEffect, useCallback, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { ChevronRight, ChevronDown } from "lucide-react";
import type { Discipline } from "../../types";

interface Props {
  tree: Discipline[];
  selectedIds: Set<number>;
  onToggle: (id: number) => void;
  glowingIds?: Set<number>;
  onGlowDismiss?: (id: number) => void;
}

function formatWorksCount(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(n >= 10_000 ? 0 : 1)}K`;
  return String(n);
}

function buildParentMap(
  nodes: Discipline[],
  map: Map<number, number | null> = new Map(),
): Map<number, number | null> {
  for (const node of nodes) {
    map.set(node.id, node.parent_id);
    if (node.children.length > 0) buildParentMap(node.children, map);
  }
  return map;
}

function collectAncestors(
  id: number,
  parentMap: Map<number, number | null>,
): Set<number> {
  const ancestors = new Set<number>();
  let current = parentMap.get(id) ?? null;
  while (current != null) {
    ancestors.add(current);
    current = parentMap.get(current) ?? null;
  }
  return ancestors;
}

function collectAllIds(nodes: Discipline[]): Set<number> {
  const ids = new Set<number>();
  for (const node of nodes) {
    ids.add(node.id);
    if (node.children.length > 0) {
      for (const cid of collectAllIds(node.children)) ids.add(cid);
    }
  }
  return ids;
}

function filterTree(nodes: Discipline[], query: string): Discipline[] {
  if (!query) return nodes;
  const lower = query.toLowerCase();
  return nodes.reduce<Discipline[]>((acc, node) => {
    const matchesSelf =
      node.name_en.toLowerCase().includes(lower) ||
      (node.name_zh?.toLowerCase().includes(lower) ?? false);
    const filteredChildren = filterTree(node.children, query);
    if (matchesSelf || filteredChildren.length > 0) {
      acc.push({ ...node, children: filteredChildren });
    }
    return acc;
  }, []);
}

interface TreeNodeProps {
  node: Discipline;
  selectedIds: Set<number>;
  onToggle: (id: number) => void;
  depth: number;
  expandedIds: Set<number>;
  onExpandToggle: (id: number) => void;
  glowingIds: Set<number>;
  onGlowDismiss?: (id: number) => void;
}

function TreeNode({
  node,
  selectedIds,
  onToggle,
  depth,
  expandedIds,
  onExpandToggle,
  glowingIds,
  onGlowDismiss,
}: TreeNodeProps) {
  const { i18n } = useTranslation();
  const isZh = i18n.language?.startsWith("zh");
  const displayName = isZh ? (node.name_zh || node.name_en) : node.name_en;
  const secondaryName = isZh ? node.name_en : node.name_zh;

  const hasChildren = node.children.length > 0;
  const isSelected = selectedIds.has(node.id);
  const isGlowing = glowingIds.has(node.id);
  const isCustom = node.is_custom === true;
  const expanded = expandedIds.has(node.id);

  const handleClick = useCallback(() => {
    if (isGlowing && onGlowDismiss) {
      onGlowDismiss(node.id);
    }
    if (hasChildren) {
      onExpandToggle(node.id);
    } else {
      onToggle(node.id);
    }
  }, [isGlowing, onGlowDismiss, hasChildren, onToggle, onExpandToggle, node.id]);

  return (
    <div>
      <div
        className={[
          "flex items-center gap-1 cursor-pointer transition-colors font-mono",
          "text-[11px] leading-tight",
          isSelected
            ? "bg-neutral-800 text-white"
            : "text-neutral-400 hover:bg-neutral-900",
          isCustom ? "border border-dashed border-cyan-400/30" : "",
          isGlowing ? "animate-discipline-glow" : "",
        ]
          .filter(Boolean)
          .join(" ")}
        style={{
          paddingLeft: `${depth * 14 + 6}px`,
          paddingTop: 3,
          paddingBottom: 3,
          paddingRight: 6,
        }}
        onClick={handleClick}
      >
        {hasChildren ? (
          expanded ? (
            <ChevronDown size={12} className="shrink-0 text-neutral-700" />
          ) : (
            <ChevronRight size={12} className="shrink-0 text-neutral-700" />
          )
        ) : (
          <span
            className={`shrink-0 inline-block w-[4px] h-[4px] ${
              isSelected ? "bg-white" : "bg-neutral-700"
            }`}
          />
        )}

        <span className="truncate">{displayName}</span>

        {secondaryName && secondaryName !== displayName && (
          <span className="text-[9px] text-neutral-600 truncate">
            {secondaryName}
          </span>
        )}

        {node.works_count != null && node.works_count > 0 && (
          <span className="text-[9px] text-neutral-600 ml-auto shrink-0 tabular-nums">
            {formatWorksCount(node.works_count)}
          </span>
        )}

        {isCustom && (
          <span className="text-[9px] text-cyan-400/60 ml-1 shrink-0 uppercase tracking-wider">
            custom
          </span>
        )}
      </div>

      {expanded && hasChildren && (
        <div>
          {node.children.map((child) => (
            <TreeNode
              key={child.id}
              node={child}
              selectedIds={selectedIds}
              onToggle={onToggle}
              depth={depth + 1}
              expandedIds={expandedIds}
              onExpandToggle={onExpandToggle}
              glowingIds={glowingIds}
              onGlowDismiss={onGlowDismiss}
            />
          ))}
        </div>
      )}
    </div>
  );
}

export default function DisciplineTree({
  tree,
  selectedIds,
  onToggle,
  glowingIds,
  onGlowDismiss,
}: Props) {
  const { t } = useTranslation();
  const [search, setSearch] = useState("");
  const [expandedIds, setExpandedIds] = useState<Set<number>>(new Set());

  const parentMap = useMemo(() => buildParentMap(tree), [tree]);

  const safeGlowingIds = glowingIds ?? new Set<number>();

  useEffect(() => {
    if (safeGlowingIds.size === 0) return;
    const toExpand = new Set<number>();
    for (const gid of safeGlowingIds) {
      for (const aid of collectAncestors(gid, parentMap)) {
        toExpand.add(aid);
      }
    }
    if (toExpand.size === 0) return;
    setExpandedIds((prev) => {
      const next = new Set(prev);
      let changed = false;
      for (const id of toExpand) {
        if (!next.has(id)) {
          next.add(id);
          changed = true;
        }
      }
      return changed ? next : prev;
    });
  }, [safeGlowingIds, parentMap]);

  const filtered = useMemo(() => filterTree(tree, search), [tree, search]);

  const searchExpandedIds = useMemo(() => {
    if (!search) return new Set<number>();
    return collectAllIds(filtered);
  }, [search, filtered]);

  const mergedExpanded = useMemo(() => {
    if (!search) return expandedIds;
    const merged = new Set(expandedIds);
    for (const id of searchExpandedIds) merged.add(id);
    return merged;
  }, [search, expandedIds, searchExpandedIds]);

  const handleExpandToggle = useCallback((id: number) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  return (
    <div className="flex flex-col h-full">
      <div className="p-2 border-b border-neutral-800">
        <input
          type="text"
          placeholder={t("common.search")}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full bg-neutral-900 border border-neutral-800 px-2 py-1 text-[11px] font-mono text-neutral-300 placeholder-neutral-600 outline-none focus:border-cyan-400/40"
        />
      </div>
      <div className="flex-1 overflow-y-auto py-1">
        {filtered.map((node) => (
          <TreeNode
            key={node.id}
            node={node}
            selectedIds={selectedIds}
            onToggle={onToggle}
            depth={0}
            expandedIds={mergedExpanded}
            onExpandToggle={handleExpandToggle}
            glowingIds={safeGlowingIds}
            onGlowDismiss={onGlowDismiss}
          />
        ))}
        {filtered.length === 0 && (
          <p className="text-neutral-600 text-[11px] font-mono text-center mt-8">
            {t("common.noResults")}
          </p>
        )}
      </div>
    </div>
  );
}
