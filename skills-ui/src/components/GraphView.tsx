import * as d3 from "d3";
import { useEffect, useMemo, useRef } from "react";

import type { GraphLink, GraphNode } from "../types";

interface GraphViewProps {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface SimulationNode extends d3.SimulationNodeDatum {
  id: string;
  label: string;
  name: string;
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
  const summary = useMemo(
    () =>
      `${nodes.length} nodes and ${links.length} relationships. ` +
      `Skill nodes connect to capabilities, workflow stages and task shapes.`,
    [links.length, nodes.length],
  );

  useEffect(() => {
    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    if (!svgRef.current || nodes.length === 0) {
      return;
    }

    const width = 960;
    const height = 560;
    const graphNodes: SimulationNode[] = nodes.map((node) => ({ ...node }));
    const nodeIds = new Set(graphNodes.map((node) => node.id));
    const graphLinks: SimulationLink[] = links
      .filter((linkItem) => nodeIds.has(linkItem.source) && nodeIds.has(linkItem.target))
      .map((linkItem) => ({ ...linkItem }));

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

    const link = svg
      .append("g")
      .attr("stroke", "#475569")
      .attr("stroke-opacity", 0.7)
      .selectAll("line")
      .data(graphLinks)
      .join("line")
      .attr("stroke-width", 1.4);

    const node = svg
      .append("g")
      .selectAll("g")
      .data(graphNodes)
      .join("g");

    node
      .append("circle")
      .attr("r", (datum) => (datum.label === "Skill" ? 9 : 7))
      .attr("fill", (datum) => nodeColour[datum.label] ?? "#cbd5e1")
      .attr("stroke", "#020617")
      .attr("stroke-width", 1.5);

    node.append("title").text((datum) => `${datum.name} (${datum.label})`);

    simulation.on("tick", () => {
      link
        .attr("x1", (datum) => positionedX(datum.source))
        .attr("y1", (datum) => positionedY(datum.source))
        .attr("x2", (datum) => positionedX(datum.target))
        .attr("y2", (datum) => positionedY(datum.target));

      node.attr("transform", (datum) => `translate(${datum.x ?? 0}, ${datum.y ?? 0})`);
    });

    return () => {
      simulation.stop();
    };
  }, [links, nodes]);

  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
      <div className="mb-4 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h2 className="text-xl font-semibold text-white">Skills Knowledge Graph</h2>
          <p className="text-sm text-slate-300">{summary}</p>
        </div>
        <span className="rounded-full bg-sky-400/10 px-3 py-1 text-sm font-medium text-sky-200">
          D3 force graph
        </span>
      </div>
      <svg
        ref={svgRef}
        role="img"
        aria-label={summary}
        viewBox="0 0 960 560"
        className="h-[28rem] w-full rounded-2xl border border-slate-800 bg-slate-950"
      />
      <details className="mt-4 text-sm text-slate-300">
        <summary className="cursor-pointer font-medium text-slate-100">
          Accessible graph summary
        </summary>
        <ul className="mt-3 grid gap-2 sm:grid-cols-2">
          {nodes.slice(0, 12).map((node) => (
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

function positionedX(value: string | number | SimulationNode): number {
  return typeof value === "object" ? (value.x ?? 0) : 0;
}

function positionedY(value: string | number | SimulationNode): number {
  return typeof value === "object" ? (value.y ?? 0) : 0;
}
