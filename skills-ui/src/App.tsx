import { Activity, FileUp, Network, ShieldCheck } from "lucide-react";
import type React from "react";
import { FormEvent, useEffect, useState } from "react";

import { apiBaseUrl, fetchGraph, fetchReadiness, fetchTechnicalInfo, uploadSkillPreview } from "./api";
import { GraphView } from "./components/GraphView";
import type { GraphResponse, ReadyResponse, TechnicalInfo, UploadPreview } from "./types";

type LoadState<T> =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; data: T };

export function App() {
  const [readiness, setReadiness] = useState<LoadState<ReadyResponse>>({ status: "loading" });
  const [graph, setGraph] = useState<LoadState<GraphResponse>>({ status: "loading" });
  const [technicalInfo, setTechnicalInfo] = useState<LoadState<TechnicalInfo>>({
    status: "loading",
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadPreview, setUploadPreview] = useState<UploadPreview | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    void loadDashboard();
  }, []);

  async function loadDashboard() {
    setReadiness({ status: "loading" });
    setGraph({ status: "loading" });
    setTechnicalInfo({ status: "loading" });
    try {
      const [readyResponse, graphResponse, technicalResponse] = await Promise.all([
        fetchReadiness(),
        fetchGraph(),
        fetchTechnicalInfo(),
      ]);
      setReadiness({ status: "ready", data: readyResponse });
      setGraph({ status: "ready", data: graphResponse });
      setTechnicalInfo({ status: "ready", data: technicalResponse });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unknown API error";
      setReadiness({ status: "error", message });
      setGraph({ status: "error", message });
      setTechnicalInfo({ status: "error", message });
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
    try {
      const preview = await uploadSkillPreview(selectedFile);
      setUploadPreview(preview);
    } catch (error) {
      setUploadError(error instanceof Error ? error.message : "Upload preview failed");
    } finally {
      setUploading(false);
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

        <section className="grid gap-6 lg:grid-cols-[0.8fr_1.2fr]">
          <UploadPanel
            selectedFile={selectedFile}
            uploading={uploading}
            preview={uploadPreview}
            error={uploadError}
            onFileChange={(file) => setSelectedFile(file)}
            onSubmit={handleUpload}
          />
          {technicalInfo.status === "ready" ? (
            <TechnicalInfoPanel technicalInfo={technicalInfo.data} />
          ) : (
            <FallbackPanel title="MCP technical information" state={technicalInfo} />
          )}
        </section>

        {graph.status === "ready" ? (
          <GraphView nodes={graph.data.nodes} links={graph.data.links} />
        ) : (
          <FallbackPanel title="Skills graph" state={graph} />
        )}
      </section>
    </main>
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
  onFileChange: (file: File | null) => void;
  onSubmit: (event: FormEvent<HTMLFormElement>) => void;
}

function UploadPanel({
  selectedFile,
  uploading,
  preview,
  error,
  onFileChange,
  onSubmit,
}: UploadPanelProps) {
  return (
    <section className="rounded-3xl border border-slate-800 bg-slate-900/80 p-5 shadow-xl">
      <div className="flex items-center gap-3">
        <FileUp className="text-sky-300" aria-hidden="true" />
        <div>
          <h2 className="text-xl font-semibold text-white">Upload Skill Preview</h2>
          <p className="text-sm text-slate-300">
            Preview validates a candidate file; it does not persist or write to Neo4j.
          </p>
        </div>
      </div>
      <form className="mt-5 grid gap-4" onSubmit={onSubmit}>
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
        </div>
      )}
    </section>
  );
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
