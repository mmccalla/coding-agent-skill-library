import * as d3 from "d3";
import { useEffect, useMemo, useRef, useState } from "react";

import type { GraphLink, GraphNode } from "../types";

interface GraphViewProps {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface SimulationNode extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  name: string;
  category?: string;
  source_path?: string;
}

interface SimulationLink extends d3.SimulationLinkDatum<SimulationNode> {
  type: string;
}

const nodeColour: Record<string, string> = {
  Skill: "#38bdf8",
  Capability: "#a78bfa",
  WorkflowStage: "#34d399",
  TaskShape: "#fbbf24",
  ControlTheme: "#fb7185",
  KnowledgeDomain: "#f472b6",
};

export function GraphView({ nodes, links }: GraphViewProps) {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const svgSelectionRef = useRef<d3.Selection<SVGSVGElement, unknown, null, undefined> | null>(
    null,
  );
  const zoomBehaviourRef = useRef<d3.ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  const [zoomScale, setZoomScale] = useState(1);
  const [enabledTypes, setEnabledTypes] = useState<Set<string>>(
    () => new Set([...new Set(nodes.map((node) => node.label))]),
  );
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [showNodeLabels, setShowNodeLabels] = useState(false);
  const [showEdgeLabels, setShowEdgeLabels] = useState(false);

  const nodeTypes = useMemo(
    () => [...new Set(nodes.map((node) => node.label))].sort(),
    [nodes],
  );
  const skillCategories = useMemo(
    () =>
      [
        ...new Set(
          nodes
            .filter((node) => node.label === "Skill" && node.category)
            .map((node) => node.category as string),
        ),
      ].sort(),
    [nodes],
  );
  const visibleSkillIds = useMemo(
    () =>
      new Set(
        nodes
          .filter(
            (node) =>
              node.label === "Skill" &&
              (selectedCategory === "all" || node.category === selectedCategory),
          )
          .map((node) => node.id),
      ),
    [nodes, selectedCategory],
  );
  const contextNodeIds = useMemo(() => {
    if (selectedCategory === "all") {
      return new Set<string>();
    }
    const connected = new Set<string>();
    for (const link of links) {
      if (visibleSkillIds.has(link.source)) {
        connected.add(link.target);
      }
      if (visibleSkillIds.has(link.target)) {
        connected.add(link.source);
      }
    }
    return connected;
  }, [links, selectedCategory, visibleSkillIds]);
  const visibleNodes = useMemo(
    () =>
      nodes.filter((node) => {
        if (!enabledTypes.has(node.label)) {
          return false;
        }
        if (selectedCategory === "all") {
          return true;
        }
        return visibleSkillIds.has(node.id) || contextNodeIds.has(node.id);
      }),
    [contextNodeIds, enabledTypes, nodes, selectedCategory, visibleSkillIds],
  );
  const visibleLinks = useMemo(() => {
    const visibleNodeIds = new Set(visibleNodes.map((node) => node.id));
    return links.filter(
      (link) => visibleNodeIds.has(link.source) && visibleNodeIds.has(link.target),
    );
  }, [links, visibleNodes]);
  const selectedNode = useMemo(
    () => visibleNodes.find((node) => node.id === selectedNodeId) ?? null,
    [selectedNodeId, visibleNodes],
  );
  const selectedRelationshipCount = useMemo(
    () =>
      selectedNode
        ? visibleLinks.filter(
            (link) => link.source === selectedNode.id || link.target === selectedNode.id,
          ).length
        : 0,
    [selectedNode, visibleLinks],
  );
  const summary = useMemo(
    () =>
      `${visibleNodes.length} visible nodes and ${visibleLinks.length} visible relationships. ` +
      `Skill nodes connect to capabilities, workflow stages and task shapes.`,
    [visibleLinks.length, visibleNodes.length],
  );

  useEffect(() => {
    setEnabledTypes((current) => {
      const availableTypes = new Set(nodeTypes);
      const next = new Set([...current].filter((type) => availableTypes.has(type)));
      for (const type of nodeTypes) {
        if (!current.size) {
          next.add(type);
        }
      }
      return next.size ? next : availableTypes;
    });
  }, [nodeTypes]);

  useEffect(() => {
    if (selectedNodeId && !visibleNodes.some((node) => node.id === selectedNodeId)) {
      setSelectedNodeId(null);
    }
  }, [selectedNodeId, visibleNodes]);

  useEffect(() => {
    const svgElement = svgRef.current;
    if (!svgElement || visibleNodes.length === 0) {
      return;
    }
    const svg = d3.select<SVGSVGElement, unknown>(svgElement);
    svgSelectionRef.current = svg;
    svg.selectAll("*").remove();
    setZoomScale(1);

    const width = 960;
    const height = 560;
    const graphNodes: SimulationNode[] = visibleNodes.map((node) => ({ ...node }));
    const nodeIds = new Set(graphNodes.map((node) => node.id));
    const graphLinks: SimulationLink[] = visibleLinks
      .filter((linkItem) => nodeIds.has(linkItem.source) && nodeIds.has(linkItem.target))
      .map((linkItem) => ({ ...linkItem }));
    const viewport = svg.append("g");

    const zoomBehaviour = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.2, 4])
      .on("zoom", (event) => {
        viewport.attr("transform", event.transform.toString());
        setZoomScale(event.transform.k);
      });
    zoomBehaviourRef.current = zoomBehaviour;
    svg.call(zoomBehaviour);

    const simulation = d3
      .forceSimulation(graphNodes)
      .force(
        "link",
        d3
          .forceLink<SimulationNode, SimulationLink>(graphLinks)
          .id((node) => node.id)
          .distance(90),
      )
      .force("charge", d3.forceManyBody().strength(-220))
      .force("centre", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(26));

    const link = viewport
      .append("g")
      .attr("stroke", "#475569")
      .attr("stroke-opacity", 0.7)
      .selectAll("line")
      .data(graphLinks)
      .join("line")
      .attr("stroke-width", 1.4);

    const edgeLabel = showEdgeLabels
      ? viewport
          .append("g")
          .attr("fill", "#cbd5e1")
          .attr("font-size", 9)
          .attr("font-family", "ui-monospace, SFMono-Regular, Menlo, monospace")
          .attr("pointer-events", "none")
          .selectAll("text")
          .data(graphLinks)
          .join("text")
          .attr("class", "edge-label")
          .attr("text-anchor", "middle")
          .attr("paint-order", "stroke")
          .attr("stroke", "#020617")
          .attr("stroke-width", 3)
          .attr("stroke-linejoin", "round")
          .text((datum) => datum.type)
      : null;

    const node = viewport
      .append("g")
      .selectAll<SVGGElement, SimulationNode>("g")
      .data(graphNodes)
      .join("g")
      .attr("cursor", "grab")
      .on("click", (_event, datum) => {
        setSelectedNodeId(datum.id);
      })
      .call(
        d3
          .drag<SVGGElement, SimulationNode>()
          .on("start", (event, datum) => {
            if (!event.active) {
              simulation.alphaTarget(0.3).restart();
            }
            datum.fx = datum.x;
            datum.fy = datum.y;
          })
          .on("drag", (event, datum) => {
            datum.fx = event.x;
            datum.fy = event.y;
          })
          .on("end", (event, datum) => {
            if (!event.active) {
              simulation.alphaTarget(0);
            }
            datum.fx = null;
            datum.fy = null;
          }),
      );

    node
      .append("circle")
      .attr("r", (datum) => (datum.label === "Skill" ? 9 : 7))
      .attr("fill", (datum) => nodeColour[datum.label] ?? "#cbd5e1")
      .attr("stroke", (datum) => (datum.id === selectedNodeId ? "#f8fafc" : "#020617"))
      .attr("stroke-width", 1.5);

    node.append("title").text((datum) => `${datum.name} (${datum.label})`);

    const nodeLabel = showNodeLabels
      ? node
          .append("text")
          .attr("class", "node-label")
          .attr("x", 12)
          .attr("y", 4)
          .attr("fill", "#e2e8f0")
          .attr("font-size", 10)
          .attr("font-family", "ui-sans-serif, system-ui, sans-serif")
          .attr("pointer-events", "none")
          .attr("paint-order", "stroke")
          .attr("stroke", "#020617")
          .attr("stroke-width", 3)
          .attr("stroke-linejoin", "round")
          .text((datum) => datum.name)
      : null;

    simulation.on("tick", () => {
      link
        .attr("x1", (datum) => positionedX(datum.source))
        .attr("y1", (datum) => positionedY(datum.source))
        .attr("x2", (datum) => positionedX(datum.target))
        .attr("y2", (datum) => positionedY(datum.target));

      node.attr("transform", (datum) => `translate(${datum.x ?? 0}, ${datum.y ?? 0})`);

      edgeLabel
        ?.attr("x", (datum) => midpoint(positionedX(datum.source), positionedX(datum.target)))
        .attr("y", (datum) => midpoint(positionedY(datum.source), positionedY(datum.target)));
      nodeLabel?.attr("display", "block");
    });

    return () => {
      svgSelectionRef.current = null;
      zoomBehaviourRef.current = null;
      simulation.stop();
    };
  }, [selectedNodeId, showEdgeLabels, showNodeLabels, visibleLinks, visibleNodes]);

  function toggleNodeType(type: string) {
    setEnabledTypes((current) => {
      const next = new Set(current);
      if (next.has(type)) {
        next.delete(type);
      } else {
        next.add(type);
      }
      return next;
    });
  }

  function adjustZoom(direction: "in" | "out") {
    const svg = svgSelectionRef.current;
    const zoomBehaviour = zoomBehaviourRef.current;
    if (!svg || !zoomBehaviour) {
      return;
    }
    const factor = direction === "in" ? 1.2 : 1 / 1.2;
    svg.transition().duration(180).call(zoomBehaviour.scaleBy, factor);
  }

  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Skills Knowledge Graph</h2>
          <p className="text-sm text-slate-300">{summary}</p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="rounded-full bg-sky-400/10 px-3 py-1 text-sm font-medium text-sky-200">
            Pan, zoom and drag nodes
          </span>
          <div
            className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-950/80 px-2 py-1"
            aria-label="Graph zoom controls"
          >
            <button
              type="button"
              onClick={() => adjustZoom("out")}
              className="rounded-full border border-slate-700 px-3 py-1 text-sm text-slate-100 hover:bg-slate-800"
              aria-label="Zoom out graph"
            >
              Zoom out
            </button>
            <output
              aria-live="polite"
              className="min-w-14 text-center text-xs font-semibold text-slate-300"
            >
              {Math.round(zoomScale * 100)}%
            </output>
            <button
              type="button"
              onClick={() => adjustZoom("in")}
              className="rounded-full border border-slate-700 px-3 py-1 text-sm text-slate-100 hover:bg-slate-800"
              aria-label="Zoom in graph"
            >
              Zoom in
            </button>
          </div>
        </div>
      </div>
      <div className="mb-4 grid gap-4 lg:grid-cols-[1fr_0.6fr]">
        <fieldset className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <legend className="px-1 text-sm font-semibold text-white">Node type filters</legend>
          <div className="mt-3 flex flex-wrap gap-3">
            {nodeTypes.map((type) => (
              <label
                key={type}
                className="flex items-center gap-2 rounded-full border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-200"
              >
                <input
                  type="checkbox"
                  checked={enabledTypes.has(type)}
                  onChange={() => toggleNodeType(type)}
                  className="h-4 w-4 accent-sky-300"
                />
                <span>{type}</span>
              </label>
            ))}
          </div>
        </fieldset>
        <div className="grid gap-4">
          <fieldset className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
            <legend className="px-1 text-sm font-semibold text-white">Label display</legend>
            <div className="mt-3 grid gap-3 text-sm text-slate-200">
              <label className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900 px-3 py-2">
                <input
                  type="checkbox"
                  checked={showNodeLabels}
                  onChange={(event) => setShowNodeLabels(event.target.checked)}
                  className="h-4 w-4 accent-sky-300"
                />
                <span>Show node labels</span>
              </label>
              <label className="flex items-center gap-2 rounded-xl border border-slate-800 bg-slate-900 px-3 py-2">
                <input
                  type="checkbox"
                  checked={showEdgeLabels}
                  onChange={(event) => setShowEdgeLabels(event.target.checked)}
                  className="h-4 w-4 accent-sky-300"
                />
                <span>Show edge labels</span>
              </label>
            </div>
          </fieldset>
          <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
            <label htmlFor="skill-category" className="text-sm font-semibold text-white">
              Skill category
            </label>
            <select
              id="skill-category"
              value={selectedCategory}
              onChange={(event) => setSelectedCategory(event.target.value)}
              className="mt-3 w-full rounded-xl border border-slate-700 bg-slate-900 px-3 py-2 text-sm text-slate-100"
            >
              <option value="all">All skill categories</option>
              {skillCategories.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
      <svg
        ref={svgRef}
        role="img"
        aria-label={summary}
        viewBox="0 0 960 560"
        className="h-[28rem] w-full rounded-2xl border border-slate-800 bg-slate-950"
      />
      <NodeDetailsPanel
        node={selectedNode}
        relationshipCount={selectedRelationshipCount}
        onClear={() => setSelectedNodeId(null)}
      />
      <details className="mt-4 text-sm text-slate-300">
        <summary className="cursor-pointer font-medium text-slate-100">
          Accessible graph summary
        </summary>
        <ul className="mt-3 grid gap-2 sm:grid-cols-2">
          {visibleNodes.slice(0, 12).map((node) => (
            <li key={node.id} className="rounded-xl bg-slate-800/70 p-3">
              <span className="font-medium text-white">{node.name}</span>
              <span className="ml-2 text-slate-400">{node.label}</span>
            </li>
          ))}
        </ul>
      </details>
    </section>
  );
}

function NodeDetailsPanel({
  node,
  relationshipCount,
  onClear,
}: {
  node: GraphNode | null;
  relationshipCount: number;
  onClear: () => void;
}) {
  return (
    <aside
      className="mt-4 rounded-2xl border border-slate-800 bg-slate-950 p-4"
      aria-live="polite"
    >
      <div className="flex items-start justify-between gap-4">
        <div>
          <h3 className="text-lg font-semibold text-white">Selected node details</h3>
          <p className="mt-1 text-sm text-slate-400">
            Select a node in the graph to inspect its evidence and graph context.
          </p>
        </div>
        {node && (
          <button
            type="button"
            onClick={onClear}
            className="rounded-full border border-slate-700 px-3 py-1 text-sm text-slate-200 hover:bg-slate-800"
          >
            Clear
          </button>
        )}
      </div>
      {node ? (
        <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-3">
          <Detail label="Name" value={node.name} />
          <Detail label="Type" value={node.label} />
          <Detail label="Category" value={node.category || "Not applicable"} />
          <Detail label="Visible relationships" value={relationshipCount.toString()} />
          <Detail label="Node ID" value={node.id} />
          <Detail label="Source path" value={node.source_path || "Not available"} />
        </dl>
      ) : (
        <p className="mt-4 rounded-xl bg-slate-900 p-3 text-sm text-slate-300">
          No node selected.
        </p>
      )}
    </aside>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-slate-900 p-3">
      <dt className="text-xs uppercase tracking-wide text-slate-500">{label}</dt>
      <dd className="mt-1 break-all font-medium text-slate-100">{value}</dd>
    </div>
  );
}

function positionedX(value: string | number | SimulationNode): number {
  return typeof value === "object" ? (value.x ?? 0) : 0;
}

function positionedY(value: string | number | SimulationNode): number {
  return typeof value === "object" ? (value.y ?? 0) : 0;
}

function midpoint(start: number, end: number): number {
  return start + (end - start) / 2;
}
