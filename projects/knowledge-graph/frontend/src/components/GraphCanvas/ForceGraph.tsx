import { useEffect, useRef, useCallback } from "react";
import { useTranslation } from "react-i18next";
import * as d3 from "d3";
import type { GraphData, D3Node, D3Edge } from "../../types";

const PALETTE = [
  "#22d3ee", "#f97316", "#a3e635", "#f472b6", "#818cf8",
  "#fb923c", "#34d399", "#e879f9", "#fbbf24", "#38bdf8",
  "#c084fc", "#4ade80", "#f87171", "#2dd4bf", "#a78bfa",
];

function buildRootColorMap(nodes: D3Node[]): Map<number, string> {
  const rootIds = new Set<number>();
  for (const n of nodes) {
    rootIds.add(n.root_id ?? n.id);
  }

  const rootToColor = new Map<number, string>();
  let idx = 0;
  for (const rid of rootIds) {
    rootToColor.set(rid, PALETTE[idx % PALETTE.length]);
    idx++;
  }

  const result = new Map<number, string>();
  for (const n of nodes) {
    const root = n.root_id ?? n.id;
    result.set(n.id, rootToColor.get(root) ?? "#94a3b8");
  }
  return result;
}

const DEFAULT_COLOR = "#94a3b8";

interface Props {
  data: GraphData;
  onNodeClick?: (nodeId: number) => void;
  onEdgeClick?: (intersectionId: number) => void;
  selectedNodes?: Set<number>;
}

export default function ForceGraph({
  data,
  onNodeClick,
  onEdgeClick,
  selectedNodes,
}: Props) {
  const { i18n } = useTranslation();
  const isZh = i18n.language?.startsWith("zh");
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const render = useCallback(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const container = containerRef.current;
    if (!container) return;
    const width = container.clientWidth;
    const height = container.clientHeight;

    svg.attr("viewBox", [0, 0, width, height].join(" "));

    const nodes: D3Node[] = data.nodes.map((n) => ({ ...n }));
    const nodeMap = new Map(nodes.map((n) => [n.id, n]));
    const colorMap = buildRootColorMap(nodes);

    const links: D3Edge[] = data.edges
      .filter((e) => nodeMap.has(e.source) && nodeMap.has(e.target))
      .map((e) => ({
        source: nodeMap.get(e.source)!,
        target: nodeMap.get(e.target)!,
        intersection_id: e.intersection_id,
        title: e.title,
        status: e.status,
        weight: e.weight,
        paper_count: e.paper_count ?? 0,
        core_tension: e.core_tension ?? null,
      }));

    const simulation = d3
      .forceSimulation<D3Node>(nodes)
      .force(
        "link",
        d3
          .forceLink<D3Node, D3Edge>(links)
          .id((d) => d.id)
          .distance(120)
      )
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(30));

    const g = svg.append("g");

    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 5])
      .on("zoom", (event) => {
        g.attr("transform", event.transform);
      });
    (svg as d3.Selection<SVGSVGElement, unknown, null, undefined>).call(zoom);

    const link = g
      .append("g")
      .selectAll<SVGLineElement, D3Edge>("line")
      .data(links)
      .join("line")
      .attr("stroke", (d) => {
        if (d.status === "gap") return "#ef4444";
        if (d.status === "active") return "#22d3ee";
        if (d.paper_count > 10) return "#737373";
        return "#404040";
      })
      .attr("stroke-width", (d) => {
        if (d.status === "gap") return 2.5;
        if (d.status === "active") return 4;
        if (d.paper_count > 20) return 4;
        if (d.paper_count > 10) return 3;
        if (d.paper_count > 3) return 2;
        return 1.5;
      })
      .attr("stroke-dasharray", (d) => {
        if (d.status === "gap") return "6 4";
        return "none";
      })
      .attr("stroke-opacity", (d) => {
        if (d.status === "gap") return 0.9;
        if (d.status === "active") return 0.9;
        if (d.paper_count > 10) return 0.8;
        if (d.paper_count > 3) return 0.6;
        return 0.45;
      })
      .style("cursor", (d) => (d.intersection_id ? "pointer" : "default"))
      .on("click", (_event, d) => {
        if (d.intersection_id) onEdgeClick?.(d.intersection_id);
      });

    const tooltip = d3
      .select(container)
      .append("div")
      .attr(
        "class",
        "absolute pointer-events-none bg-neutral-900 border border-neutral-700 text-neutral-300 text-[10px] font-mono px-2 py-1 shadow-lg opacity-0 transition-opacity z-50 max-w-xs leading-relaxed"
      );

    link
      .on("mouseenter", (event, d) => {
        const parts: string[] = [d.title];
        if (d.status === "gap") {
          parts.push("[RESEARCH GAP]");
        } else if (d.paper_count > 0) {
          parts.push(`${d.paper_count} papers`);
        }
        if (d.core_tension) {
          parts.push(`"${d.core_tension}"`);
        }
        tooltip
          .style("opacity", "1")
          .html(parts.join("<br>"))
          .style("left", `${event.offsetX + 10}px`)
          .style("top", `${event.offsetY - 20}px`);
      })
      .on("mouseleave", () => {
        tooltip.style("opacity", "0");
      });

    const edgeLabels = g
      .append("g")
      .selectAll<SVGTextElement, D3Edge>("text")
      .data(links.filter((d) => d.paper_count > 0 || d.status === "gap"))
      .join("text")
      .text((d) => {
        if (d.status === "gap") return "GAP";
        if (d.paper_count > 0) return String(d.paper_count);
        return "";
      })
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .style("font-family", "'JetBrains Mono', monospace")
      .style("font-size", "9px")
      .style("font-weight", "bold")
      .style("fill", (d) => (d.status === "gap" ? "#ef4444" : "#a3a3a3"))
      .style("pointer-events", "none");

    const node = g
      .append("g")
      .selectAll<SVGGElement, D3Node>("g")
      .data(nodes)
      .join("g")
      .style("cursor", "pointer")
      .on("click", (_event, d) => {
        onNodeClick?.(d.id);
      })
      .call(
        d3
          .drag<SVGGElement, D3Node>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
          })
          .on("drag", (event, d) => {
            d.fx = event.x;
            d.fy = event.y;
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
          })
      );

    node
      .append("circle")
      .attr("r", 10)
      .attr("fill", (d) => colorMap.get(d.id) ?? DEFAULT_COLOR)
      .attr("fill-opacity", 0.75)
      .attr("stroke", (d) =>
        selectedNodes?.has(d.id) ? "#22d3ee" : "transparent"
      )
      .attr("stroke-width", 3);

    node
      .append("text")
      .text((d) => isZh ? (d.name_zh ?? d.name_en) : d.name_en)
      .attr("x", 14)
      .attr("y", 4)
      .style("font-family", "'JetBrains Mono', monospace")
      .style("font-size", "10px")
      .style("fill", "#e5e5e5")
      .style("pointer-events", "none");

    node
      .on("mouseenter", (event, d) => {
        const primary = isZh ? (d.name_zh ?? d.name_en) : d.name_en;
        const secondary = isZh ? d.name_en : d.name_zh;
        const label = secondary && secondary !== primary ? `${primary} / ${secondary}` : primary;
        tooltip
          .style("opacity", "1")
          .text(label)
          .style("left", `${event.offsetX + 10}px`)
          .style("top", `${event.offsetY - 20}px`);
      })
      .on("mouseleave", () => {
        tooltip.style("opacity", "0");
      });

    simulation.on("tick", () => {
      link
        .attr("x1", (d) => d.source.x!)
        .attr("y1", (d) => d.source.y!)
        .attr("x2", (d) => d.target.x!)
        .attr("y2", (d) => d.target.y!);

      edgeLabels
        .attr("x", (d) => ((d.source.x ?? 0) + (d.target.x ?? 0)) / 2)
        .attr("y", (d) => ((d.source.y ?? 0) + (d.target.y ?? 0)) / 2);

      node.attr("transform", (d) => `translate(${d.x},${d.y})`);
    });

    return () => {
      simulation.stop();
      tooltip.remove();
    };
  }, [data, onNodeClick, onEdgeClick, selectedNodes, isZh]);

  useEffect(() => {
    const cleanup = render();
    const handleResize = () => render();
    window.addEventListener("resize", handleResize);
    return () => {
      cleanup?.();
      window.removeEventListener("resize", handleResize);
    };
  }, [render]);

  return (
    <div ref={containerRef} className="relative w-full h-full">
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  );
}
