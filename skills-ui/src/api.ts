import type {
  AdminIngestResult,
  AdminIngestsListResponse,
  GraphQueryRequest,
  GraphQueryResponse,
  GraphResponse,
  OllamaModelsResponse,
  OpenApiSpec,
  ReadyResponse,
  TechnicalInfo,
  UploadPreview,
} from "./types";

const DEFAULT_API_BASE_URL = "http://localhost:8000";

export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL;

export interface ApiErrorDetail {
  error_type?: string;
  message?: string;
  hint?: string;
  operation?: string;
  request_id?: string;
}

export class ApiRequestError extends Error {
  readonly status?: number;
  readonly statusText?: string;
  readonly path: string;
  readonly detail: ApiErrorDetail;

  constructor({
    message,
    path,
    status,
    statusText,
    detail = {},
  }: {
    message: string;
    path: string;
    status?: number;
    statusText?: string;
    detail?: ApiErrorDetail;
  }) {
    super(message);
    this.name = "ApiRequestError";
    this.path = path;
    this.status = status;
    this.statusText = statusText;
    this.detail = detail;
  }
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${apiBaseUrl}${path}`, init);
  } catch (error) {
    throw new ApiRequestError({
      message: `Could not reach the Skills API at ${apiBaseUrl}${path}.`,
      path,
      detail: {
        error_type: "network_error",
        hint:
          "Check that the Docker stack is running, the API port is exposed, and the browser can reach the API base URL.",
        message: error instanceof Error ? error.message : "Network request failed.",
        operation: httpOperation(path, init),
      },
    });
  }
  if (!response.ok) {
    let detail = `${response.status} ${response.statusText}`;
    let structuredDetail: ApiErrorDetail = {};
    try {
      const payload = (await response.json()) as { detail?: unknown };
      if (typeof payload.detail === "string") {
        detail = payload.detail;
      }
      if (isApiErrorDetail(payload.detail)) {
        structuredDetail = payload.detail;
        detail = payload.detail.message ?? detail;
      }
    } catch {
      detail = `${response.status} ${response.statusText}`;
    }
    throw new ApiRequestError({
      message: detail,
      path,
      status: response.status,
      statusText: response.statusText,
      detail: structuredDetail,
    });
  }
  return (await response.json()) as T;
}

function isApiErrorDetail(value: unknown): value is ApiErrorDetail {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function httpOperation(path: string, init?: RequestInit): string {
  return `${init?.method ?? "GET"} ${path}`;
}

export function fetchReadiness(): Promise<ReadyResponse> {
  return requestJson<ReadyResponse>("/health/ready");
}

export function fetchGraph(): Promise<GraphResponse> {
  return requestJson<GraphResponse>("/skills/graph");
}

export function fetchTechnicalInfo(): Promise<TechnicalInfo> {
  return requestJson<TechnicalInfo>("/mcp/technical-info");
}

export function fetchOpenApiSpec(): Promise<OpenApiSpec> {
  return requestJson<OpenApiSpec>("/openapi.json");
}

export function fetchOllamaModels(ollamaEndpoint: string): Promise<OllamaModelsResponse> {
  const params = new URLSearchParams({ ollama_endpoint: ollamaEndpoint });
  return requestJson<OllamaModelsResponse>(`/ollama/models?${params.toString()}`);
}

export function uploadSkillPreview(file: File): Promise<UploadPreview> {
  const formData = new FormData();
  formData.append("file", file);
  return requestJson<UploadPreview>("/skills/upload/preview", {
    method: "POST",
    body: formData,
  });
}

function adminRequestHeaders(adminKey: string): HeadersInit {
  return { "X-Skills-Admin-Key": adminKey };
}

export function ingestSkill(file: File, adminKey: string): Promise<AdminIngestResult> {
  const formData = new FormData();
  formData.append("file", file);
  return requestJson<AdminIngestResult>("/skills/admin/ingest", {
    method: "POST",
    headers: adminRequestHeaders(adminKey),
    body: formData,
  });
}

export function listRecentIngests(
  adminKey: string,
  limit = 20,
): Promise<AdminIngestsListResponse> {
  const params = new URLSearchParams({ limit: String(limit) });
  return requestJson<AdminIngestsListResponse>(`/skills/admin/ingests?${params.toString()}`, {
    headers: adminRequestHeaders(adminKey),
  });
}

export function queryGraph(request: GraphQueryRequest): Promise<GraphQueryResponse> {
  return requestJson<GraphQueryResponse>("/skills/query", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
}
