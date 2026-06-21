import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";

const graphResponse = {
  status: "ok",
  nodes: [
    {
      id: "skill:kg-enabled-rag",
      label: "Skill",
      name: "kg-enabled-rag",
      category: "data-architecture",
      source_path: "skills/data-architecture/kg-enabled-rag/SKILL.md",
    },
  ],
  links: [
    {
      source: "skill:kg-enabled-rag",
      target: "capability:retrieval",
      type: "HAS_CAPABILITY",
    },
  ],
  node_count: 1,
  link_count: 1,
};

const technicalInfo = {
  status: "ok",
  server_name: "skills-kg",
  read_only: true,
  tools: ["recommend_skills", "search_skills"],
  resources: ["skills://ontology", "skills://contract"],
  limits: { "recommend_skills.limit": 10 },
  api_endpoints: ["GET /skills/graph", "POST /skills/upload/preview"],
};

describe("App", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (input: RequestInfo | URL) => {
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
        return new Response("Not found", { status: 404 });
      }),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders service status, graph and MCP technical information", async () => {
    render(<App />);

    expect(await screen.findByText("Skills Knowledge Graph")).toBeInTheDocument();
    expect(screen.getByText("1 nodes · 1 links")).toBeInTheDocument();
    expect(screen.getByText("recommend_skills")).toBeInTheDocument();
    expect(screen.getByLabelText(/1 nodes and 1 relationships/i)).toBeInTheDocument();
  });

  it("previews an uploaded SKILL.md without persisting it", async () => {
    render(<App />);
    await screen.findByText("Skills Knowledge Graph");

    const input = screen.getByLabelText(/Skill markdown file/i);
    const file = new File(["---\nname: example-skill\n---"], "SKILL.md", {
      type: "text/markdown",
    });
    fireEvent.change(input, { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: /Preview upload/i }));

    await waitFor(() => expect(screen.getByText("example-skill")).toBeInTheDocument());
    expect(screen.getByText("No")).toBeInTheDocument();
  });
});

function jsonResponse(body: unknown): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
  });
}
