import type { GraphResponse, ReadyResponse, TechnicalInfo, UploadPreview } from "./types";

const DEFAULT_API_BASE_URL = "http://localhost:8000";

export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? DEFAULT_API_BASE_URL;

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, init);
  if (!response.ok) {
    throw new Error(`${response.status} ${response.statusText}`);
  }
  return (await response.json()) as T;
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

export function uploadSkillPreview(file: File): Promise<UploadPreview> {
  const formData = new FormData();
  formData.append("file", file);
  return requestJson<UploadPreview>("/skills/upload/preview", {
    method: "POST",
    body: formData,
  });
}
