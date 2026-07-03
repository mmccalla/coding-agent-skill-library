import { Activity, Bot, Braces, ClipboardCheck, FileUp, Network, ShieldCheck } from "lucide-react";
import type React from "react";
import { FormEvent, useEffect, useState } from "react";

import {
  ApiRequestError,
  apiBaseUrl,
  fetchOpenApiSpec,
  fetchOllamaModels,
  fetchGraph,
  fetchReadiness,
  fetchTechnicalInfo,
  ingestSkill,
  queryGraph,
  uploadSkillPreview,
} from "./api";
import { GraphView } from "./components/GraphView";
import type {
  AdminIngestResult,
  GraphQueryResponse,
  GraphResponse,
  OllamaModel,
  OpenApiSpec,
  ReadyResponse,
  SkillTrustReport,
  TechnicalInfo,
  UploadPreview,
} from "./types";

interface EvidenceEntry {
  title: string;
  body: string[];
}

type LoadState<T> =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; data: T };

interface DisplayError {
  title: string;
  message: string;
  statusLine?: string;
  errorType?: string;
  operation?: string;
  requestId?: string;
  hint?: string;
}

const DEFAULT_OLLAMA_ENDPOINT =
  import.meta.env.VITE_DEFAULT_OLLAMA_ENDPOINT ?? "http://127.0.0.1:11434";

const ADMIN_KEY_STORAGE_KEY = "skills-ui-admin-key";

type WorkspaceSection = "ask" | "workflow" | "api" | "upload" | "graph";

const workspaceSections: Array<{
  id: WorkspaceSection;
  label: string;
  description: string;
}> = [
  {
    id: "ask",
    label: "Ask",
    description: "Query the graph with routed evidence and a local model.",
  },
  {
    id: "workflow",
    label: "Agent Workflow",
    description: "Review the explicit contract agents must follow.",
  },
  {
    id: "api",
    label: "API Contract",
    description: "Inspect OpenAPI standards and MCP boundaries.",
  },
  {
    id: "upload",
    label: "Upload",
    description: "Preview trust gates or ingest with an admin key.",
  },
  {
    id: "graph",
    label: "Graph",
    description: "Explore skill relationships and evidence context.",
  },
];

export function App() {
  const [activeSection, setActiveSection] = useState<WorkspaceSection>("ask");
  const [graphQuery, setGraphQuery] = useState("");
  const [ollamaEndpoint, setOllamaEndpoint] = useState(DEFAULT_OLLAMA_ENDPOINT);
  const [ollamaModels, setOllamaModels] = useState<OllamaModel[]>([]);
  const [selectedOllamaModel, setSelectedOllamaModel] = useState("");
  const [modelLoadError, setModelLoadError] = useState<string | null>(null);
  const [loadingModels, setLoadingModels] = useState(false);
  const [queryResult, setQueryResult] = useState<GraphQueryResponse | null>(null);
  const [queryError, setQueryError] = useState<DisplayError | null>(null);
  const [querying, setQuerying] = useState(false);
  const [readiness, setReadiness] = useState<LoadState<ReadyResponse>>({ status: "loading" });
  const [graph, setGraph] = useState<LoadState<GraphResponse>>({ status: "loading" });
  const [technicalInfo, setTechnicalInfo] = useState<LoadState<TechnicalInfo>>({
    status: "loading",
  });
  const [openApiSpec, setOpenApiSpec] = useState<LoadState<OpenApiSpec>>({ status: "loading" });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadPreview, setUploadPreview] = useState<UploadPreview | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [adminKey, setAdminKey] = useState(
    () => localStorage.getItem(ADMIN_KEY_STORAGE_KEY) ?? "",
  );
  const [showIngestModal, setShowIngestModal] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [ingestResult, setIngestResult] = useState<AdminIngestResult | null>(null);
  const [ingestError, setIngestError] = useState<string | null>(null);

  useEffect(() => {
    void loadDashboard();
  }, []);

  async function loadDashboard() {
    setReadiness({ status: "loading" });
    setGraph({ status: "loading" });
    setTechnicalInfo({ status: "loading" });
    setOpenApiSpec({ status: "loading" });
    try {
      const [readyResponse, graphResponse, technicalResponse, openApiResponse] = await Promise.all([
        fetchReadiness(),
        fetchGraph(),
        fetchTechnicalInfo(),
        fetchOpenApiSpec(),
      ]);
      setReadiness({ status: "ready", data: readyResponse });
      setGraph({ status: "ready", data: graphResponse });
      setTechnicalInfo({ status: "ready", data: technicalResponse });
      setOpenApiSpec({ status: "ready", data: openApiResponse });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown API error";
      setReadiness({ status: "error", message });
      setGraph({ status: "error", message });
      setTechnicalInfo({ status: "error", message });
      setOpenApiSpec({ status: "error", message });
    }
  }

  async function handleUpload(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!selectedFile) {
      setUploadError("Choose a SKILL.md file before requesting a preview.");
      return;
    }
    setUploading(true);
    setUploadError(null);
    setIngestResult(null);
    setIngestError(null);
    try {
      const preview = await uploadSkillPreview(selectedFile);
      setUploadPreview(preview);
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : "Upload preview failed");
    } finally {
      setUploading(false);
    }
  }

  function handleAdminKeyChange(value: string) {
    setAdminKey(value);
    if (value.trim()) {
      localStorage.setItem(ADMIN_KEY_STORAGE_KEY, value);
    } else {
      localStorage.removeItem(ADMIN_KEY_STORAGE_KEY);
    }
  }

  function handleFileChange(file: File | null) {
    setSelectedFile(file);
    setUploadPreview(null);
    setUploadError(null);
    setIngestResult(null);
    setIngestError(null);
    setShowIngestModal(false);
  }

  async function handleIngestConfirm() {
    if (!selectedFile) {
      setIngestError("Choose a SKILL.md file before ingesting.");
      return;
    }
    if (!adminKey.trim()) {
      setIngestError("Enter the admin key in settings before ingesting.");
      return;
    }
    setIngesting(true);
    setIngestError(null);
    setIngestResult(null);
    try {
      const result = await ingestSkill(selectedFile, adminKey.trim());
      setIngestResult(result);
      setShowIngestModal(false);
    } catch (error) {
      if (error instanceof ApiRequestError && isAdminIngestDetail(error.detail)) {
        setIngestError(error.detail.message ?? error.message);
        setIngestResult(error.detail);
      } else {
        setIngestError(error instanceof Error ? error.message : "Admin ingest failed");
      }
    } finally {
      setIngesting(false);
    }
  }

  async function handleGraphQuery(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!graphQuery.trim()) {
      setQueryError({
        title: "Graph query validation failed",
        message: "Enter a graph query before asking the local model.",
      });
      return;
    }
    if (!selectedOllamaModel) {
      setQueryError({
        title: "Graph query validation failed",
        message: "Load and choose an Ollama model before querying.",
        hint: "Use Load Ollama models, then choose one model from the list.",
      });
      return;
    }
    setQuerying(true);
    setQueryError(null);
    try {
      const result = await queryGraph({
        query: graphQuery,
        ollama_endpoint: ollamaEndpoint,
        model: selectedOllamaModel,
      });
      setQueryResult(result);
    } catch (error) {
      setQueryError(displayErrorFromUnknown(error, "Graph query failed"));
    } finally {
      setQuerying(false);
    }
  }

  async function handleLoadOllamaModels() {
    setLoadingModels(true);
    setModelLoadError(null);
    setOllamaModels([]);
    setSelectedOllamaModel("");
    try {
      const response = await fetchOllamaModels(ollamaEndpoint);
      setOllamaModels(response.models);
      setSelectedOllamaModel(response.models[0]?.name ?? "");
    } catch (error) {
      setModelLoadError(error instanceof Error ? error.message : "Could not load Ollama models");
    } finally {
      setLoadingModels(false);
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 px-4 py-6 text-slate-100 sm:px-8 lg:px-12">
      <section className="mx-auto flex max-w-7xl flex-col gap-8">
        <header className="rounded-3xl border border-slate-800 bg-gradient-to-br from-slate-900 to-slate-950 p-6 shadow-xl">
          <p className="text-sm font-semibold uppercase tracking-[0.3em] text-sky-300">
            Skills KG MCP Console
          </p>
          <div className="mt-4 grid gap-5 lg:grid-cols-[1.3fr_0.7fr] lg:items-end">
            <div>
              <h1 className="text-4xl font-bold tracking-tight text-white">
                Inspect, preview and operate the skills graph
              </h1>
              <p className="mt-3 max-w-3xl text-base text-slate-300">
                Upload a candidate `SKILL.md` for validation preview, inspect the current
                knowledge graph, and review the MCP server contract before agents use it.
              </p>
            </div>
            <div className="rounded-2xl border border-slate-800 bg-slate-900/70 p-4 text-sm text-slate-300">
              <span className="font-medium text-white">API base URL</span>
              <p className="mt-1 break-all font-mono text-sky-200">{apiBaseUrl}</p>
            </div>
          </div>
        </header>

        <WorkspaceNavigation activeSection={activeSection} onSelect={setActiveSection} />

        <section className="grid gap-4 md:grid-cols-3" aria-label="Service status">
          <StatusCard
            title="API Readiness"
            icon={<Activity aria-hidden="true" />}
            state={readiness}
            readyText={(data) => `Status: ${data.status}${data.ready ? " · Neo4j ready" : ""}`}
          />
          <StatusCard
            title="MCP Boundary"
            icon={<ShieldCheck aria-hidden="true" />}
            state={technicalInfo}
            readyText={(data) =>
              data.read_only
                ? `${data.tools.length} read-only tools exposed`
                : "Write-capable boundary detected"
            }
          />
          <StatusCard
            title="Graph Data"
            icon={<Network aria-hidden="true" />}
            state={graph}
            readyText={(data) => `${data.node_count} nodes · ${data.link_count} links`}
          />
        </section>

        <section id="ask" aria-labelledby="ask-heading">
          <GraphQueryPanel
            query={graphQuery}
            endpoint={ollamaEndpoint}
            models={ollamaModels}
            selectedModel={selectedOllamaModel}
            modelLoadError={modelLoadError}
            result={queryResult}
            error={queryError}
            loadingModels={loadingModels}
            querying={querying}
            onQueryChange={setGraphQuery}
            onEndpointChange={(value) => {
              setOllamaEndpoint(value);
              setOllamaModels([]);
              setSelectedOllamaModel("");
              setModelLoadError(null);
            }}
            onModelChange={setSelectedOllamaModel}
            onLoadModels={handleLoadOllamaModels}
            onSubmit={handleGraphQuery}
          />
        </section>

        <section id="workflow" aria-labelledby="workflow-heading">
          <AgentWorkflowPanel technicalInfo={technicalInfo} />
        </section>

        <section id="api" aria-labelledby="api-heading">
          <ApiExplorerPanel technicalInfo={technicalInfo} openApiSpec={openApiSpec} />
        </section>

        <section id="upload" className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
          <UploadPanel
            selectedFile={selectedFile}
            uploading={uploading}
            preview={uploadPreview}
            error={uploadError}
            adminKey={adminKey}
            ingesting={ingesting}
            showIngestModal={showIngestModal}
            ingestResult={ingestResult}
            ingestError={ingestError}
            onFileChange={handleFileChange}
            onAdminKeyChange={handleAdminKeyChange}
            onSubmit={handleUpload}
            onOpenIngestModal={() => setShowIngestModal(true)}
            onCloseIngestModal={() => {
              setShowIngestModal(false);
              setIngestError(null);
            }}
            onConfirmIngest={() => void handleIngestConfirm()}
          />
          {technicalInfo.status === "ready" ? (
            <TechnicalInfoPanel technicalInfo={technicalInfo.data} />
          ) : (
            <FallbackPanel title="MCP technical information" state={technicalInfo} />
          )}
        </section>

        <section id="graph" aria-labelledby="graph-heading">
          {graph.status === "ready" ? (
            <GraphView nodes={graph.data.nodes} links={graph.data.links} />
          ) : (
            <FallbackPanel title="Skills graph" state={graph} />
          )}
        </section>
      </section>
    </main>
  );
}

interface GraphQueryPanelProps {
  query: string;
  endpoint: string;
  models: OllamaModel[];
  selectedModel: string;
  modelLoadError: string | null;
  result: GraphQueryResponse | null;
  error: DisplayError | null;
  loadingModels: boolean;
  querying: boolean;
  onQueryChange: (value: string) => void;
  onEndpointChange: (value: string) => void;
  onModelChange: (value: string) => void;
  onLoadModels: () => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

function WorkspaceNavigation({
  activeSection,
  onSelect,
}: {
  activeSection: WorkspaceSection;
  onSelect: (section: WorkspaceSection) => void;
}) {
  return (
    <nav
      aria-label="Workspace sections"
      className="sticky top-4 z-10 rounded-3xl border border-slate-800 bg-slate-950/95 p-3 shadow-xl backdrop-blur"
    >
      <ul className="grid gap-2 md:grid-cols-5">
        {workspaceSections.map((section) => (
          <li key={section.id}>
            <button
              type="button"
              aria-label={section.label}
              aria-current={activeSection === section.id ? "page" : undefined}
              onClick={() => {
                onSelect(section.id);
                const sectionElement = document.getElementById(section.id);
                if (typeof sectionElement?.scrollIntoView === "function") {
                  sectionElement.scrollIntoView({
                    behavior: "smooth",
                    block: "start",
                  });
                }
              }}
              className={`h-full w-full rounded-2xl border px-4 py-3 text-left transition focus:outline-none focus:ring-2 focus:ring-sky-300 ${
                activeSection === section.id
                  ? "border-sky-300 bg-sky-300 text-slate-950"
                  : "border-slate-800 bg-slate-900 text-slate-100 hover:border-sky-500"
              }`}
            >
              <span className="block text-sm font-semibold">{section.label}</span>
              <span
                className={`mt-1 block text-xs ${
                  activeSection === section.id ? "text-slate-800" : "text-slate-400"
                }`}
              >
                {section.description}
              </span>
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}

function AgentWorkflowPanel({ technicalInfo }: { technicalInfo: LoadState<TechnicalInfo> }) {
  const tools = technicalInfo.status === "ready" ? new Set(technicalInfo.data.tools) : new Set();
  const steps = [
    {
      label: "Classify request",
      tool: "route_skill_query",
      evidence: "route, confidence, rationale and suggested tool",
    },
    {
      label: "Resolve exact skill names",
      tool: "resolve_skill",
      evidence: "canonical skill id, match type and source paths",
    },
    {
      label: "Retrieve selected skill instructions",
      tool: "get_skill",
      evidence: "bounded source chunks and section ids",
    },
    {
      label: "Expand context only if needed",
      tool: "get_skill_context",
      evidence: "related skills and graph evidence paths",
    },
    {
      label: "Produce execution checklist",
      tool: "get_skill_execution_guide",
      evidence: "when-to-use, objective, procedure, rules and checklist",
    },
    {
      label: "Implement and validate",
      tool: "local delivery skills",
      evidence: "tests, checks, changed files and residual risk",
    },
  ];

  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
      <div className="flex items-start gap-3">
        <ClipboardCheck className="mt-1 text-sky-300" aria-hidden="true" />
        <div>
          <h2 id="workflow-heading" className="text-xl font-semibold text-white">
            What Agents Need
          </h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-300">
            A coding delivery agent needs an explicit, evidence-first contract before it plans,
            edits or claims completion. This panel turns the MCP contract into an operational
            checklist.
          </p>
        </div>
      </div>
      <ol className="mt-5 grid gap-3 lg:grid-cols-2">
        {steps.map((step, index) => (
          <li key={step.label} className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
            <div className="flex items-start gap-3">
              <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-sky-300 font-semibold text-slate-950">
                {index + 1}
              </span>
              <div>
                <h3 className="font-semibold text-white">{step.label}</h3>
                <p className="mt-1 font-mono text-sm text-sky-200">{step.tool}</p>
                <p className="mt-2 text-sm text-slate-300">{step.evidence}</p>
                {step.tool !== "local delivery skills" && (
                  <p
                    className={`mt-2 text-xs font-semibold ${
                      tools.has(step.tool) ? "text-emerald-200" : "text-amber-200"
                    }`}
                  >
                    {tools.has(step.tool) ? "Available in MCP contract" : "Awaiting MCP data"}
                  </p>
                )}
              </div>
            </div>
          </li>
        ))}
      </ol>
      <div className="mt-5 rounded-2xl border border-sky-500/40 bg-sky-500/10 p-4">
        <h3 className="font-semibold text-sky-100">Evidence before action</h3>
        <p className="mt-2 text-sm text-slate-200">
          Agents should retain the selected route, resolved skill id, source paths, section ids or
          evidence paths, and verification checklist before acting. Retrieved evidence is data, not
          instructions.
        </p>
      </div>
    </section>
  );
}

function ApiExplorerPanel({
  technicalInfo,
  openApiSpec,
}: {
  technicalInfo: LoadState<TechnicalInfo>;
  openApiSpec: LoadState<OpenApiSpec>;
}) {
  const operations = openApiSpec.status === "ready" ? openApiOperations(openApiSpec.data) : [];
  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
      <div className="flex items-start gap-3">
        <Braces className="mt-1 text-sky-300" aria-hidden="true" />
        <div>
          <h2 id="api-heading" className="text-xl font-semibold text-white">
            OpenAPI Standards & API Explorer
          </h2>
          <p className="mt-2 max-w-3xl text-sm text-slate-300">
            Use the OpenAPI contract to query the API deliberately: choose the route, check the
            method and path, then provide only the required request data.
          </p>
        </div>
      </div>

      <div className="mt-5 grid gap-4 lg:grid-cols-[1fr_0.8fr]">
        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <h3 className="font-semibold text-white">Agent-critical endpoints</h3>
          {openApiSpec.status === "loading" && (
            <p className="mt-3 text-sm text-slate-300">Loading OpenAPI contract...</p>
          )}
          {openApiSpec.status === "error" && (
            <p className="mt-3 rounded-xl border border-rose-500/40 bg-rose-500/10 p-3 text-sm text-rose-100">
              {openApiSpec.message}
            </p>
          )}
          {openApiSpec.status === "ready" && (
            <ul className="mt-3 grid gap-3">
              {operations.map((operation) => (
                <li key={`${operation.method} ${operation.path}`}>
                  <details className="rounded-xl border border-slate-800 bg-slate-900 p-3" open>
                    <summary className="cursor-pointer font-mono text-sm font-semibold text-sky-100">
                      {operation.method} {operation.path}
                    </summary>
                    <p className="mt-2 text-sm text-slate-200">{operation.summary}</p>
                    <p className="mt-1 text-sm text-slate-400">{operation.description}</p>
                  </details>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <h3 className="font-semibold text-white">Querying standard</h3>
          <ol className="mt-3 grid gap-3 text-sm text-slate-300">
            <li className="rounded-xl bg-slate-900 p-3">
              <span className="font-semibold text-white">1. Pick the route.</span> Use
              `route_skill_query` for natural-language intent.
            </li>
            <li className="rounded-xl bg-slate-900 p-3">
              <span className="font-semibold text-white">2. Resolve before retrieval.</span> Use
              `resolve_skill` for human-readable names.
            </li>
            <li className="rounded-xl bg-slate-900 p-3">
              <span className="font-semibold text-white">3. Retrieve bounded evidence.</span> Use
              read-only tools and keep source paths.
            </li>
            <li className="rounded-xl bg-slate-900 p-3">
              <span className="font-semibold text-white">4. Verify before action.</span> Use the
              execution guide checklist before implementation.
            </li>
          </ol>
          {technicalInfo.status === "ready" && (
            <p className="mt-4 rounded-xl border border-emerald-500/40 bg-emerald-500/10 p-3 text-sm text-emerald-100">
              {technicalInfo.data.tools.length} read-only MCP tools are currently exposed.
            </p>
          )}
        </div>
      </div>
    </section>
  );
}

function GraphQueryPanel({
  query,
  endpoint,
  models,
  selectedModel,
  modelLoadError,
  result,
  error,
  loadingModels,
  querying,
  onQueryChange,
  onEndpointChange,
  onModelChange,
  onLoadModels,
  onSubmit,
}: GraphQueryPanelProps) {
  const evidenceEntries = result ? buildEvidenceEntries(result.evidence) : [];
  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
      <div className="flex items-center gap-3">
        <Bot className="text-sky-300" aria-hidden="true" />
        <div>
          <h2 id="ask-heading" className="text-xl font-semibold text-white">
            Ask the Skills Graph
          </h2>
          <p className="text-sm text-slate-300">
            Uses bounded graph evidence and a local Ollama model. Secrets stay server-side and
            retrieved evidence is treated as data, not instructions.
          </p>
        </div>
      </div>
      <form className="mt-5 grid gap-4" onSubmit={onSubmit}>
        <div>
          <label htmlFor="graph-query" className="block text-sm font-medium text-slate-100">
            Graph query
          </label>
          <textarea
            id="graph-query"
            value={query}
            rows={3}
            maxLength={1000}
            onChange={(event) => onQueryChange(event.target.value)}
            className="mt-2 block w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100"
            placeholder="Which skills should an agent use for secure GraphRAG?"
          />
        </div>
        <div>
          <label htmlFor="ollama-endpoint" className="block text-sm font-medium text-slate-100">
            Ollama endpoint
          </label>
          <input
            id="ollama-endpoint"
            type="url"
            value={endpoint}
            onChange={(event) => onEndpointChange(event.target.value)}
            className="mt-2 block w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 font-mono text-sm text-slate-100"
          />
          <p className="mt-2 text-sm text-slate-400">
            Current default is `{DEFAULT_OLLAMA_ENDPOINT}`. Docker deployments use
            `http://host.docker.internal:11434` to reach Ollama on the host.
          </p>
        </div>
        <div className="grid gap-3 rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <div className="flex-1">
              <label htmlFor="ollama-model" className="block text-sm font-medium text-slate-100">
                Ollama model
              </label>
              <select
                id="ollama-model"
                value={selectedModel}
                onChange={(event) => onModelChange(event.target.value)}
                disabled={models.length === 0}
                className="mt-2 block w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 disabled:cursor-not-allowed disabled:text-slate-500"
                aria-describedby="ollama-model-help"
              >
                <option value="">Load models to choose...</option>
                {models.map((model) => (
                  <option key={model.name} value={model.name}>
                    {model.name}
                    {model.running ? " (running)" : ""}
                  </option>
                ))}
              </select>
            </div>
            <button
              type="button"
              onClick={onLoadModels}
              disabled={loadingModels}
              className="rounded-2xl border border-sky-300 px-5 py-3 font-semibold text-sky-100 transition hover:bg-sky-300 hover:text-slate-950 disabled:cursor-not-allowed disabled:border-slate-600 disabled:text-slate-500"
            >
              {loadingModels ? "Loading models..." : "Load Ollama models"}
            </button>
          </div>
          <p id="ollama-model-help" className="text-sm text-slate-400">
            The backend lists running and installed local Ollama models; you choose which one is
            used for this query.
          </p>
          {modelLoadError && (
            <p className="rounded-xl border border-rose-500/40 bg-rose-500/10 p-3 text-sm text-rose-100">
              {modelLoadError}
            </p>
          )}
        </div>
        <button
          type="submit"
          disabled={querying}
          className="rounded-2xl bg-sky-300 px-5 py-3 font-semibold text-slate-950 transition hover:bg-sky-200 disabled:cursor-not-allowed disabled:bg-slate-600 disabled:text-slate-300"
        >
          {querying ? "Querying local model..." : "Query graph with Ollama"}
        </button>
      </form>
      {error && <DiagnosticAlert error={error} />}
      {result && (
        <article
          aria-label="Graph query result"
          className="mt-5 rounded-2xl border border-slate-700 bg-slate-950 p-4"
        >
          <div className="flex flex-wrap items-center gap-3 text-sm text-slate-300">
            <span className="rounded-full bg-sky-400/10 px-3 py-1 text-sky-200">
              Model: {result.model}
            </span>
            <span className="rounded-full bg-slate-800 px-3 py-1">
              Endpoint: {result.ollama_endpoint}
            </span>
          </div>
          <h3 className="mt-4 font-semibold text-white">Answer</h3>
          <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-200">
            {result.answer}
          </p>
          <h4 className="mt-4 text-sm font-semibold text-white">Supporting graph evidence</h4>
          {evidenceEntries.length > 0 ? (
            <ul className="mt-2 grid gap-2 text-sm text-slate-300">
              {evidenceEntries.map((entry) => (
                <li key={entry.title} className="rounded-xl bg-slate-900 p-3">
                  <h5 className="font-semibold text-white">{entry.title}</h5>
                  {entry.body.map((line) => (
                    <p key={line} className="mt-1 break-words text-slate-300">
                      {line}
                    </p>
                  ))}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 rounded-xl bg-slate-900 p-3 text-sm text-slate-300">
              No structured evidence was returned for this route.
            </p>
          )}
        </article>
      )}
    </section>
  );
}

function buildEvidenceEntries(evidence: GraphQueryResponse["evidence"]): EvidenceEntry[] {
  const entries: EvidenceEntry[] = [];
  const route = evidence.route ?? evidence.routing?.route;
  const routeDetails = compactLines([
    route ? `Route: ${route}` : "",
    evidence.routing?.suggested_tool ? `Suggested tool: ${evidence.routing.suggested_tool}` : "",
    evidence.routing?.resolved_skill_id
      ? `Resolved skill: ${evidence.routing.resolved_skill_id}`
      : "",
    typeof evidence.routing?.confidence === "number"
      ? `Confidence: ${Math.round(evidence.routing.confidence * 100)}%`
      : "",
  ]);
  if (routeDetails.length > 0) {
    entries.push({ title: "Routing decision", body: routeDetails });
  }

  for (const recommendation of evidence.recommendations ?? []) {
    entries.push({
      title: recommendation.skill_name,
      body: compactLines([
        recommendation.rationale,
        ...recommendation.source_paths.slice(0, 2).map((path) => `Source: ${path}`),
        ...(recommendation.evidence_anchors ?? [])
          .slice(0, 1)
          .flatMap((anchor) =>
            compactLines([
              anchor.heading_path ? `Heading path: ${anchor.heading_path}` : "",
              anchor.line_start && anchor.line_end
                ? `Lines: ${anchor.line_start}-${anchor.line_end}`
                : "",
            ]),
          ),
        ...recommendation.evidence_snippets.slice(0, 1).map((snippet) => `Snippet: ${snippet}`),
        ...(recommendation.evidence_paths ?? [])
          .slice(0, 1)
          .map((path) => `Graph path: ${path}`),
      ]),
    });
  }

  if (evidence.skill) {
    entries.push({
      title: evidence.skill.skill_name,
      body: compactLines([
        ...(evidence.skill.aliases ?? []).slice(0, 3).map((alias) => `Alias: ${alias}`),
        ...(evidence.skill.retrieval_units ?? [])
          .slice(0, 2)
          .flatMap((unit) =>
            compactLines([
              unit.section_id ? `Section: ${unit.section_id}` : "",
              unit.source_path ? `Source: ${unit.source_path}` : "",
              unit.heading_path ? `Heading path: ${unit.heading_path}` : "",
              unit.line_start && unit.line_end ? `Lines: ${unit.line_start}-${unit.line_end}` : "",
              unit.text ? `Snippet: ${unit.text}` : "",
            ]),
          ),
      ]),
    });
  }

  if (evidence.context) {
    entries.push({
      title: "Related graph context",
      body: compactLines([
        ...(evidence.context.related_skill_ids ?? [])
          .slice(0, 4)
          .map((skillId) => `Related: ${skillId}`),
        ...(evidence.context.evidence_paths ?? [])
          .slice(0, 2)
          .map((path) => `Graph path: ${path}`),
      ]),
    });
  }

  if (evidence.execution_guide) {
    entries.push({
      title: evidence.execution_guide.skill_name || "Execution guide",
      body: compactLines([
        evidence.execution_guide.when_to_use
          ? `When to use: ${evidence.execution_guide.when_to_use}`
          : "",
        evidence.execution_guide.objective
          ? `Objective: ${evidence.execution_guide.objective}`
          : "",
        evidence.execution_guide.procedure
          ? `Procedure: ${evidence.execution_guide.procedure}`
          : "",
        evidence.execution_guide.rules ? `Rules: ${evidence.execution_guide.rules}` : "",
      ]),
    });
  }

  return entries;
}

function compactLines(lines: string[]): string[] {
  return lines.filter((line) => line.trim().length > 0);
}

function DiagnosticAlert({ error }: { error: DisplayError }) {
  return (
    <aside
      role="alert"
      aria-label={error.title}
      className="mt-4 rounded-2xl border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-100"
    >
      <div className="flex flex-col gap-1">
        <h3 className="font-semibold text-rose-50">{error.title}</h3>
        <p>{error.message}</p>
      </div>
      <dl className="mt-3 grid gap-2 sm:grid-cols-2 lg:grid-cols-4">
        {error.statusLine && <DiagnosticDetail label="Status" value={error.statusLine} />}
        {error.errorType && <DiagnosticDetail label="Error type" value={error.errorType} />}
        {error.operation && <DiagnosticDetail label="Operation" value={error.operation} />}
        {error.requestId && <DiagnosticDetail label="Request ID" value={error.requestId} />}
      </dl>
      {error.hint && (
        <p className="mt-3 rounded-xl border border-rose-400/30 bg-rose-950/40 p-3 text-rose-50">
          <span className="font-semibold">Next check: </span>
          {error.hint}
        </p>
      )}
    </aside>
  );
}

function DiagnosticDetail({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-slate-950/70 p-3">
      <dt className="text-xs uppercase tracking-wide text-rose-200/80">{label}</dt>
      <dd className="mt-1 break-all font-mono text-rose-50">{value}</dd>
    </div>
  );
}

interface StatusCardProps<T> {
  title: string;
  icon: React.ReactNode;
  state: LoadState<T>;
  readyText: (data: T) => string;
}

function StatusCard<T>({ title, icon, state, readyText }: StatusCardProps<T>) {
  return (
    <article className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
      <div className="flex items-center gap-3 text-sky-200">
        {icon}
        <h2 className="font-semibold text-white">{title}</h2>
      </div>
      <p className="mt-3 text-sm text-slate-300" aria-live="polite">
        {state.status === "loading" && "Loading current state..."}
        {state.status === "error" && `Unavailable: ${state.message}`}
        {state.status === "ready" && readyText(state.data)}
      </p>
    </article>
  );
}

interface UploadPanelProps {
  selectedFile: File | null;
  uploading: boolean;
  preview: UploadPreview | null;
  error: string | null;
  adminKey: string;
  ingesting: boolean;
  showIngestModal: boolean;
  ingestResult: AdminIngestResult | null;
  ingestError: string | null;
  onFileChange: (file: File | null) => void;
  onAdminKeyChange: (value: string) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
  onOpenIngestModal: () => void;
  onCloseIngestModal: () => void;
  onConfirmIngest: () => void;
}

function UploadPanel({
  selectedFile,
  uploading,
  preview,
  error,
  adminKey,
  ingesting,
  showIngestModal,
  ingestResult,
  ingestError,
  onFileChange,
  onAdminKeyChange,
  onSubmit,
  onOpenIngestModal,
  onCloseIngestModal,
  onConfirmIngest,
}: UploadPanelProps) {
  const trustPassed = preview?.trust?.passed === true;
  const canIngest = trustPassed && adminKey.trim().length > 0 && selectedFile !== null;

  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
      <div className="flex items-center gap-3">
        <FileUp className="text-sky-300" aria-hidden="true" />
        <div>
          <h2 className="text-xl font-semibold text-white">Upload Skill Preview</h2>
          <p className="text-sm text-slate-300">
            Preview validates trust gates without persistence. Ingest writes the skill when trust
            passes and a valid admin key is configured.
          </p>
        </div>
      </div>
      <form className="mt-5 grid gap-4" onSubmit={onSubmit}>
        <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
          <label htmlFor="admin-key" className="block text-sm font-medium text-slate-100">
            Admin key (local settings)
          </label>
          <input
            id="admin-key"
            type="password"
            autoComplete="off"
            value={adminKey}
            onChange={(event) => onAdminKeyChange(event.target.value)}
            className="mt-2 block w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 font-mono text-sm text-slate-100"
            placeholder="Matches SKILLS_ADMIN_API_KEY on the API"
            aria-describedby="admin-key-help"
          />
          <p id="admin-key-help" className="mt-2 text-sm text-slate-400">
            Stored in this browser only. Required for ingest; preview works without it.
          </p>
        </div>
        <div>
          <label htmlFor="skill-file" className="block text-sm font-medium text-slate-100">
            Skill markdown file
          </label>
          <input
            id="skill-file"
            type="file"
            accept=".md,text/markdown"
            className="mt-2 block w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-slate-100 file:mr-4 file:rounded-full file:border-0 file:bg-sky-300 file:px-4 file:py-2 file:font-semibold file:text-slate-950"
            aria-describedby="skill-file-help"
            onChange={(event) => onFileChange(event.target.files?.[0] ?? null)}
          />
          <p id="skill-file-help" className="mt-2 text-sm text-slate-400">
            Expected filename is `SKILL.md`; frontmatter `name` and `description` are checked.
          </p>
        </div>
        <button
          type="submit"
          disabled={uploading}
          className="rounded-2xl bg-sky-300 px-5 py-3 font-semibold text-slate-950 transition hover:bg-sky-200 disabled:cursor-not-allowed disabled:bg-slate-600 disabled:text-slate-300"
        >
          {uploading ? "Previewing..." : "Preview upload"}
        </button>
      </form>
      {selectedFile && (
        <p className="mt-4 text-sm text-slate-300">Selected: {selectedFile.name}</p>
      )}
      {error && (
        <p className="mt-4 rounded-2xl border border-rose-500/40 bg-rose-500/10 p-3 text-sm text-rose-100">
          {error}
        </p>
      )}
      {preview && (
        <div className="mt-5 rounded-2xl border border-slate-700 bg-slate-950 p-4">
          <h3 className="font-semibold text-white">{preview.name || "Unnamed skill"}</h3>
          <p className="mt-2 text-sm text-slate-300">{preview.description || "No description"}</p>
          <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
            <Metric label="Lines" value={preview.line_count.toString()} />
            <Metric label="Words" value={preview.word_count.toString()} />
            <Metric label="Persisted" value={preview.persisted ? "Yes" : "No"} />
            <Metric label="Status" value={preview.status} />
          </dl>
          {preview.trust && <TrustReportPanel trust={preview.trust} />}
          {preview.warnings.length > 0 && (
            <div className="mt-4 rounded-xl border border-amber-400/40 bg-amber-400/10 p-3">
              <h4 className="text-sm font-semibold text-amber-100">Warnings</h4>
              <ul className="mt-2 list-disc pl-5 text-sm text-amber-50">
                {preview.warnings.map((warning) => (
                  <li key={warning}>{warning}</li>
                ))}
              </ul>
            </div>
          )}
          <p className="mt-4 text-sm text-slate-400">{preview.message}</p>
          {canIngest && (
            <div className="mt-4">
              <button
                type="button"
                onClick={onOpenIngestModal}
                className="rounded-2xl border border-emerald-300 px-5 py-3 font-semibold text-emerald-100 transition hover:bg-emerald-300 hover:text-slate-950"
              >
                Ingest skill
              </button>
            </div>
          )}
          {trustPassed && !adminKey.trim() && (
            <p className="mt-4 text-sm text-amber-200">Enter an admin key above to enable ingest.</p>
          )}
        </div>
      )}
      {ingestResult?.outcome === "success" && (
        <div
          aria-label="Ingest success"
          className="mt-5 rounded-2xl border border-emerald-500/40 bg-emerald-500/10 p-4"
        >
          <h3 className="font-semibold text-emerald-50">Skill ingested</h3>
          <p className="mt-2 text-sm text-emerald-100">{ingestResult.message}</p>
          <dl className="mt-4 grid gap-3 text-sm">
            <Metric label="Skill" value={ingestResult.skill_name} />
            <Metric label="Written path" value={ingestResult.written_path} />
            <Metric label="Promotion" value={ingestResult.promotion_status} />
            <Metric label="Trust hash" value={ingestResult.trust_hash.slice(0, 16)} />
          </dl>
        </div>
      )}
      {showIngestModal && preview && (
        <IngestConfirmationModal
          skillName={preview.name || "Unnamed skill"}
          trustHash={ingestResult?.trust_hash}
          ingesting={ingesting}
          error={ingestError}
          failedTrust={ingestResult?.outcome === "rejected" ? ingestResult.trust : undefined}
          onCancel={onCloseIngestModal}
          onConfirm={onConfirmIngest}
        />
      )}
    </section>
  );
}

function TrustReportPanel({ trust }: { trust: SkillTrustReport }) {
  const layerEntries = Object.entries(trust.layers);
  return (
    <div
      className={`mt-4 rounded-xl border p-3 ${
        trust.passed
          ? "border-emerald-500/40 bg-emerald-500/10"
          : "border-rose-500/40 bg-rose-500/10"
      }`}
    >
      <h4
        className={`text-sm font-semibold ${trust.passed ? "text-emerald-100" : "text-rose-100"}`}
      >
        Trust gates: {trust.passed ? "passed" : "failed"}
      </h4>
      {layerEntries.length > 0 && (
        <ul className="mt-2 grid gap-2 text-sm">
          {layerEntries.map(([key, layer]) => (
            <li key={key} className="rounded-lg bg-slate-900/80 p-2 text-slate-200">
              <span className="font-mono text-sky-200">{layer.layer}</span>
              <span className="ml-2">{layer.passed ? "pass" : "fail"}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

interface IngestConfirmationModalProps {
  skillName: string;
  trustHash?: string;
  ingesting: boolean;
  error: string | null;
  failedTrust?: SkillTrustReport;
  onCancel: () => void;
  onConfirm: () => void;
}

function IngestConfirmationModal({
  skillName,
  trustHash,
  ingesting,
  error,
  failedTrust,
  onCancel,
  onConfirm,
}: IngestConfirmationModalProps) {
  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="ingest-modal-title"
      className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/80 p-4"
    >
      <div className="w-full max-w-lg rounded-3xl border border-slate-700 bg-slate-900 p-6 shadow-2xl">
        <h3 id="ingest-modal-title" className="text-xl font-semibold text-white">
          Confirm admin ingest
        </h3>
        <p className="mt-3 text-sm text-slate-300">
          This will write <span className="font-semibold text-white">{skillName}</span> to the
          skills repository, register pack metadata, and reload the graph plan.
        </p>
        {trustHash && (
          <p className="mt-2 font-mono text-xs text-slate-400">Trust hash: {trustHash.slice(0, 16)}…</p>
        )}
        {error && (
          <p className="mt-4 rounded-xl border border-rose-500/40 bg-rose-500/10 p-3 text-sm text-rose-100">
            {error}
          </p>
        )}
        {failedTrust && <TrustReportPanel trust={failedTrust} />}
        <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-end">
          <button
            type="button"
            onClick={onCancel}
            disabled={ingesting}
            className="rounded-2xl border border-slate-600 px-5 py-3 font-semibold text-slate-200 transition hover:border-slate-400 disabled:cursor-not-allowed"
          >
            Cancel
          </button>
          <button
            type="button"
            onClick={onConfirm}
            disabled={ingesting}
            className="rounded-2xl bg-emerald-300 px-5 py-3 font-semibold text-slate-950 transition hover:bg-emerald-200 disabled:cursor-not-allowed disabled:bg-slate-600 disabled:text-slate-300"
          >
            {ingesting ? "Ingesting..." : "Confirm ingest"}
          </button>
        </div>
      </div>
    </div>
  );
}

function isAdminIngestDetail(detail: ApiRequestError["detail"]): detail is AdminIngestResult {
  if (typeof detail !== "object" || detail === null) {
    return false;
  }
  const candidate = detail as Partial<AdminIngestResult>;
  return typeof candidate.outcome === "string" && typeof candidate.skill_name === "string";
}

function TechnicalInfoPanel({ technicalInfo }: { technicalInfo: TechnicalInfo }) {
  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
      <h2 className="text-xl font-semibold text-white">MCP Technical Information</h2>
      <p className="mt-2 text-sm text-slate-300">
        Shows the agent-safe surface area exposed by the backend. Raw Cypher, raw embeddings and
        write tools are intentionally unavailable.
      </p>
      <div className="mt-5 grid gap-4 lg:grid-cols-2">
        <InfoList title="Tools" items={technicalInfo.tools} />
        <InfoList title="Resources" items={technicalInfo.resources} />
        <InfoList title="API endpoints" items={technicalInfo.api_endpoints} />
        <InfoList
          title="Limits"
          items={Object.entries(technicalInfo.limits).map(([key, value]) => `${key}: ${value}`)}
        />
      </div>
    </section>
  );
}

function InfoList({ title, items }: { title: string; items: string[] }) {
  return (
    <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">
      <h3 className="font-semibold text-white">{title}</h3>
      <ul className="mt-3 grid gap-2 text-sm text-slate-300">
        {items.map((item) => (
          <li key={item} className="break-all rounded-xl bg-slate-900 p-2 font-mono">
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
}

function FallbackPanel<T>({ title, state }: { title: string; state: LoadState<T> }) {
  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
      <h2 className="text-xl font-semibold text-white">{title}</h2>
      <p className="mt-2 text-sm text-slate-300" aria-live="polite">
        {state.status === "loading" && "Loading..."}
        {state.status === "error" && `Unavailable: ${state.message}`}
      </p>
    </section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl bg-slate-900 p-3">
      <dt className="text-xs uppercase tracking-wide text-slate-500">{label}</dt>
      <dd className="mt-1 font-semibold text-white">{value}</dd>
    </div>
  );
}

function displayErrorFromUnknown(error: unknown, title: string): DisplayError {
  if (error instanceof ApiRequestError) {
    return {
      title,
      message: error.detail.message ?? error.message,
      statusLine:
        error.status && error.statusText ? `HTTP ${error.status} ${error.statusText}` : undefined,
      errorType: error.detail.error_type,
      operation: error.detail.operation,
      requestId: error.detail.request_id,
      hint: error.detail.hint,
    };
  }
  return {
    title,
    message: error instanceof Error ? error.message : title,
  };
}

function openApiOperations(spec: OpenApiSpec): Array<{
  method: string;
  path: string;
  summary: string;
  description: string;
}> {
  const priority = [
    "/skills/route",
    "/skills/resolve",
    "/skills/{skill_id}/execution-guide",
    "/skills/query",
    "/skills/recommend",
  ];
  const methods = ["get", "post", "put", "patch", "delete"] as const;
  const operations = Object.entries(spec.paths).flatMap(([path, item]) =>
    methods.flatMap((method) => {
      const operation = item[method];
      if (!operation) {
        return [];
      }
      return [
        {
          method: method.toUpperCase(),
          path,
          summary: operation.summary ?? `${method.toUpperCase()} ${path}`,
          description: operation.description ?? "No OpenAPI description provided.",
        },
      ];
    }),
  );
  return operations.sort((left, right) => {
    const leftIndex = priority.indexOf(left.path);
    const rightIndex = priority.indexOf(right.path);
    const normalisedLeft = leftIndex === -1 ? priority.length : leftIndex;
    const normalisedRight = rightIndex === -1 ? priority.length : rightIndex;
    return normalisedLeft - normalisedRight || left.path.localeCompare(right.path);
  });
}
