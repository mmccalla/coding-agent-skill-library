import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";

const graphResponse = {
  status: "ok",
  nodes: [
    {
      id: "skill:knowledge-graph-rag",
      label: "Skill",
      name: "knowledge-graph-rag",
      category: "data-architecture",
      source_path: "skills/data-architecture/knowledge-graph-rag/SKILL.md",
    },
    {
      id: "skill:accessibility-wcag",
      label: "Skill",
      name: "accessibility-wcag",
      category: "user-experience",
      source_path: "skills/user-experience/accessibility-wcag/SKILL.md",
    },
    {
      id: "capability:retrieval",
      label: "Capability",
      name: "retrieval",
    },
  ],
  links: [
    {
      source: "skill:knowledge-graph-rag",
      target: "capability:retrieval",
      type: "HAS_CAPABILITY",
    },
  ],
  node_count: 3,
  link_count: 1,
};

const technicalInfo = {
  status: "ok",
  server_name: "skills-kg",
  read_only: true,
  tools: [
    "route_skill_query",
    "resolve_skill",
    "get_skill",
    "recommend_skills",
    "get_skill_context",
    "get_skill_execution_guide",
  ],
  resources: ["skills://ontology", "skills://contract"],
  limits: { "recommend_skills.limit": 10, "get_skill.chunk_limit": 10 },
  api_endpoints: [
    "POST /skills/route",
    "GET /skills/resolve",
    "GET /skills/{skill_id}/execution-guide",
    "GET /skills/graph",
    "POST /skills/upload/preview",
  ],
};

const openApiResponse = {
  openapi: "3.1.0",
  info: { title: "Skills KG GraphRAG", version: "0.1.0" },
  paths: {
    "/skills/route": {
      post: {
        summary: "Route Skill Query",
        description: "Classify skill questions before selecting evidence.",
      },
    },
    "/skills/resolve": {
      get: {
        summary: "Resolve Skill",
        description: "Resolve a human skill name to a canonical skill id.",
      },
    },
    "/skills/{skill_id}/execution-guide": {
      get: {
        summary: "Get Skill Execution Guide",
        description: "Return execution guidance and verification checklist.",
      },
    },
  },
};

describe("App", () => {
  let queryShouldFail = false;
  let queryShouldReturnStructuredError = false;
  let lastQueryRequest: unknown = null;
  let lastModelListUrl = "";

  beforeEach(() => {
    queryShouldFail = false;
    queryShouldReturnStructuredError = false;
    lastQueryRequest = null;
    lastModelListUrl = "";
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
        const url = String(input);
        if (url.endsWith("/health/ready")) {
          return jsonResponse({ status: "ok", read_only: true });
        }
        if (url.endsWith("/skills/graph")) {
          return jsonResponse(graphResponse);
        }
        if (url.endsWith("/mcp/technical-info")) {
          return jsonResponse(technicalInfo);
        }
        if (url.endsWith("/openapi.json")) {
          return jsonResponse(openApiResponse);
        }
        if (url.includes("/ollama/models")) {
          lastModelListUrl = url;
          return jsonResponse({
            status: "ok",
            ollama_endpoint: "http://127.0.0.1:11434",
            models: [
              { name: "qwen3:1.7b", running: true },
              { name: "kgrag-qwen3-4b:latest", running: false },
            ],
          });
        }
        if (url.endsWith("/skills/upload/preview")) {
          return jsonResponse({
            status: "ok",
            filename: "SKILL.md",
            name: "example-skill",
            description: "A safe preview.",
            line_count: 8,
            word_count: 16,
            warnings: [],
            persisted: false,
            message: "Upload preview only.",
          });
        }
        if (url.endsWith("/skills/query")) {
          lastQueryRequest = init?.body ? JSON.parse(String(init.body)) : null;
          const requestQuery =
            typeof lastQueryRequest === "object" &&
            lastQueryRequest !== null &&
            "query" in lastQueryRequest &&
            typeof (lastQueryRequest as { query?: unknown }).query === "string"
              ? (lastQueryRequest as { query: string }).query
              : "";
          if (queryShouldReturnStructuredError) {
            return jsonResponse(
              {
                detail: {
                  error_type: "ollama_load_failed",
                  message: "Ollama could not load the selected model.",
                  hint: "Confirm the model exists with `ollama list`, then retry or choose another model.",
                  operation: "skills.query",
                  request_id: "req_test_123",
                },
              },
              502,
              "Bad Gateway",
            );
          }
          if (queryShouldFail) {
            return jsonResponse(
              { detail: "Could not connect to local Ollama." },
              502,
              "Bad Gateway",
            );
          }
          if (requestQuery.includes("Tell me about knowledge-graph-rag")) {
            return jsonResponse({
              status: "ok",
              answer: "knowledge-graph-rag is the direct skill profile.",
              model: "test-model",
              ollama_endpoint: "http://127.0.0.1:11434",
              evidence: {
                route: "direct_lookup",
                routing: {
                  route: "direct_lookup",
                  confidence: 0.86,
                  suggested_tool: "get_skill",
                  resolved_skill_id: "skill:knowledge-graph-rag",
                },
                skill: {
                  skill_id: "skill:knowledge-graph-rag",
                  skill_name: "knowledge-graph-rag",
                  aliases: ["kg-enabled-rag"],
                  retrieval_units: [
                    {
                      retrieval_unit_id: "retrieval-1",
                      text: "Use this skill when implementing graph-backed retrieval with evidence.",
                      source_path: "skills/data-architecture/knowledge-graph-rag/SKILL.md",
                      section_id: "skill:knowledge-graph-rag:section:0-when-to-use",
                    },
                  ],
                },
                context: {
                  skill_id: "skill:knowledge-graph-rag",
                  related_skill_ids: ["skill:knowledge-retrieval-rag"],
                  evidence_paths: [
                    "skill:knowledge-graph-rag -[COMPLEMENTS]-> skill:knowledge-retrieval-rag",
                  ],
                },
              },
            });
          }
          return jsonResponse({
            status: "ok",
            answer: "Use knowledge-graph-rag with source evidence.",
            model: "test-model",
            ollama_endpoint: "http://127.0.0.1:11434",
            evidence: {
              route: "recommendation",
              recommendations: [
                {
                  skill_id: "skill:knowledge-graph-rag",
                  skill_name: "knowledge-graph-rag",
                  rationale: "Relevant to GraphRAG.",
                  source_paths: ["skills/data-architecture/knowledge-graph-rag/SKILL.md"],
                  evidence_snippets: ["Use graph evidence."],
                },
              ],
            },
          });
        }
        return new Response("Not found", { status: 404 });
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders service status, graph and MCP technical information", async () => {
    render(<App />);

    expect(await screen.findByRole("heading", { name: "Ask the Skills Graph" })).toBeInTheDocument();
    expect(screen.getByRole("navigation", { name: /Workspace sections/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Ask/i })).toHaveAttribute("aria-current", "page");
    expect(screen.getByText("3 nodes · 1 links")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /API Contract/i }));
    expect(screen.getAllByText("route_skill_query").length).toBeGreaterThan(0);
    expect(screen.getByLabelText(/3 visible nodes and 1 visible relationships/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Skill category/i)).toBeInTheDocument();
    expect(screen.getByRole("checkbox", { name: "Skill" })).toBeChecked();
    expect(screen.getByText("No node selected.")).toBeInTheDocument();
  });

  it("filters the graph by skill category and node type", async () => {
    render(<App />);
    await screen.findByRole("heading", { name: "Ask the Skills Graph" });
    fireEvent.click(screen.getByRole("button", { name: "Graph" }));

    fireEvent.change(screen.getByLabelText(/Skill category/i), {
      target: { value: "user-experience" },
    });
    fireEvent.click(screen.getByLabelText(/Capability/i));

    expect(screen.getByLabelText(/1 visible nodes and 0 visible relationships/i)).toBeInTheDocument();
  });

  it("toggles node and edge labels on the graph", async () => {
    const { container } = render(<App />);
    await screen.findByRole("heading", { name: "Ask the Skills Graph" });
    fireEvent.click(screen.getByRole("button", { name: "Graph" }));

    expect(container.querySelector(".node-label")).toBeNull();
    expect(container.querySelector(".edge-label")).toBeNull();

    fireEvent.click(screen.getByRole("checkbox", { name: /Show node labels/i }));
    fireEvent.click(screen.getByRole("checkbox", { name: /Show edge labels/i }));

    await waitFor(() =>
      expect(container.querySelector(".node-label")?.textContent).toBe("knowledge-graph-rag"),
    );
    expect(container.querySelector(".edge-label")?.textContent).toBe("HAS_CAPABILITY");
  });

  it("provides explicit zoom controls for the graph", async () => {
    render(<App />);
    await screen.findByRole("heading", { name: "Ask the Skills Graph" });
    fireEvent.click(screen.getByRole("button", { name: "Graph" }));

    expect(screen.getByLabelText("Graph zoom controls")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Zoom out graph" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Zoom in graph" })).toBeInTheDocument();
    expect(screen.getByText("100%")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Zoom in graph" }));

    await waitFor(() => expect(screen.getByText("120%")).toBeInTheDocument());
  });

  it("shows node details when a graph node is selected", async () => {
    const { container } = render(<App />);
    await screen.findByRole("heading", { name: "Ask the Skills Graph" });
    fireEvent.click(screen.getByRole("button", { name: "Graph" }));

    const firstNode = container.querySelector("svg g g circle");
    expect(firstNode).not.toBeNull();
    fireEvent.click(firstNode as SVGCircleElement);

    expect(await screen.findByText("Selected node details")).toBeInTheDocument();
    const details = screen.getByRole("complementary");
    expect(within(details).getByText("knowledge-graph-rag")).toBeInTheDocument();
    expect(
      within(details).getByText("skills/data-architecture/knowledge-graph-rag/SKILL.md"),
    ).toBeInTheDocument();
  });

  it("queries the graph through the editable Ollama endpoint", async () => {
    render(<App />);
    await screen.findByRole("heading", { name: "Ask the Skills Graph" });

    fireEvent.click(screen.getByRole("button", { name: /Load Ollama models/i }));
    await screen.findByLabelText(/Ollama model/i);
    expect(lastModelListUrl).toContain("ollama_endpoint=http%3A%2F%2F127.0.0.1%3A11434");
    fireEvent.change(screen.getByLabelText(/Ollama model/i), {
      target: { value: "qwen3:1.7b" },
    });
    fireEvent.change(screen.getByLabelText(/Graph query/i), {
      target: { value: "Which skill supports GraphRAG?" },
    });
    fireEvent.change(screen.getByLabelText(/Ollama endpoint/i), {
      target: { value: "http://127.0.0.1:11434" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Query graph with Ollama/i }));

    expect(await screen.findByText("Use knowledge-graph-rag with source evidence.")).toBeInTheDocument();
    expect(screen.getByText("Model: test-model")).toBeInTheDocument();
    expect(lastQueryRequest).toMatchObject({ model: "qwen3:1.7b" });
    const queryResult = screen.getByRole("article", { name: /Graph query result/i });
    expect(within(queryResult).getByText("knowledge-graph-rag")).toBeInTheDocument();
  });

  it("renders direct lookup evidence when the backend does not return recommendations", async () => {
    render(<App />);
    await screen.findByRole("heading", { name: "Ask the Skills Graph" });

    fireEvent.click(screen.getByRole("button", { name: /Load Ollama models/i }));
    await screen.findByLabelText(/Ollama model/i);
    fireEvent.change(screen.getByLabelText(/Ollama model/i), {
      target: { value: "qwen3:1.7b" },
    });
    fireEvent.change(screen.getByLabelText(/Graph query/i), {
      target: { value: "Tell me about knowledge-graph-rag" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Query graph with Ollama/i }));

    expect(await screen.findByText("knowledge-graph-rag is the direct skill profile.")).toBeInTheDocument();
    const queryResult = screen.getByRole("article", { name: /Graph query result/i });
    expect(within(queryResult).getByText("Routing decision")).toBeInTheDocument();
    expect(within(queryResult).getByText("Route: direct_lookup")).toBeInTheDocument();
    expect(within(queryResult).getByText("Resolved skill: skill:knowledge-graph-rag")).toBeInTheDocument();
    expect(
      within(queryResult).getByText("Source: skills/data-architecture/knowledge-graph-rag/SKILL.md"),
    ).toBeInTheDocument();
    expect(within(queryResult).getByText("Related graph context")).toBeInTheDocument();
  });

  it("requires a user-selected Ollama model before querying", async () => {
    render(<App />);
    await screen.findByRole("heading", { name: "Ask the Skills Graph" });

    fireEvent.change(screen.getByLabelText(/Graph query/i), {
      target: { value: "Which skill supports GraphRAG?" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Query graph with Ollama/i }));

    expect(await screen.findByText("Load and choose an Ollama model before querying.")).toBeInTheDocument();
  });

  it("shows detailed backend errors for Ollama failures", async () => {
    queryShouldFail = true;
    render(<App />);
    await screen.findByRole("heading", { name: "Ask the Skills Graph" });

    fireEvent.click(screen.getByRole("button", { name: /Load Ollama models/i }));
    await screen.findByLabelText(/Ollama model/i);
    fireEvent.change(screen.getByLabelText(/Ollama model/i), {
      target: { value: "qwen3:1.7b" },
    });
    fireEvent.change(screen.getByLabelText(/Graph query/i), {
      target: { value: "Which skill supports GraphRAG?" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Query graph with Ollama/i }));

    expect(await screen.findByText("Could not connect to local Ollama.")).toBeInTheDocument();
  });

  it("shows actionable structured diagnostics for graph query failures", async () => {
    queryShouldReturnStructuredError = true;
    render(<App />);
    await screen.findByRole("heading", { name: "Ask the Skills Graph" });

    fireEvent.click(screen.getByRole("button", { name: /Load Ollama models/i }));
    await screen.findByLabelText(/Ollama model/i);
    fireEvent.change(screen.getByLabelText(/Ollama model/i), {
      target: { value: "kgrag-qwen3-4b:latest" },
    });
    fireEvent.change(screen.getByLabelText(/Graph query/i), {
      target: { value: "How should I build a web application?" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Query graph with Ollama/i }));

    const alert = await screen.findByRole("alert", { name: /Graph query failed/i });
    expect(within(alert).getByText("Ollama could not load the selected model.")).toBeInTheDocument();
    expect(within(alert).getByText("HTTP 502 Bad Gateway")).toBeInTheDocument();
    expect(within(alert).getByText("ollama_load_failed")).toBeInTheDocument();
    expect(within(alert).getByText("skills.query")).toBeInTheDocument();
    expect(within(alert).getByText("req_test_123")).toBeInTheDocument();
    expect(within(alert).getByText(/Confirm the model exists/)).toBeInTheDocument();
  });

  it("previews an uploaded SKILL.md without persisting it", async () => {
    render(<App />);
    await screen.findByRole("heading", { name: "Ask the Skills Graph" });
    fireEvent.click(screen.getByRole("button", { name: "Upload" }));

    const input = screen.getByLabelText(/Skill markdown file/i);
    const file = new File(["---\nname: example-skill\n---"], "SKILL.md", {
      type: "text/markdown",
    });
    fireEvent.change(input, { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: /Preview upload/i }));

    await waitFor(() => expect(screen.getByText("example-skill")).toBeInTheDocument());
    expect(screen.getByText("No")).toBeInTheDocument();
  });

  it("shows the agent workflow contract as a first-class workspace section", async () => {
    render(<App />);

    await screen.findByRole("heading", { name: "Ask the Skills Graph" });
    fireEvent.click(screen.getByRole("button", { name: /Agent Workflow/i }));

    expect(screen.getByRole("heading", { name: "What Agents Need" })).toBeInTheDocument();
    expect(screen.getAllByText("route_skill_query").length).toBeGreaterThan(0);
    expect(screen.getAllByText("get_skill_execution_guide").length).toBeGreaterThan(0);
    expect(screen.getByText(/Evidence before action/i)).toBeInTheDocument();
  });

  it("loads OpenAPI standards guidance for querying the API", async () => {
    render(<App />);

    await screen.findByRole("heading", { name: "Ask the Skills Graph" });
    fireEvent.click(screen.getByRole("button", { name: /API Contract/i }));

    expect(await screen.findByText("OpenAPI Standards & API Explorer")).toBeInTheDocument();
    expect(screen.getAllByText("POST /skills/route").length).toBeGreaterThan(0);
    expect(screen.getAllByText("GET /skills/resolve").length).toBeGreaterThan(0);
    expect(screen.getByText("Classify skill questions before selecting evidence.")).toBeInTheDocument();
  });
});

function jsonResponse(body: unknown, status = 200, statusText = "OK"): Response {
  return new Response(JSON.stringify(body), {
    status,
    statusText,
    headers: { "Content-Type": "application/json" },
  });
}
