export interface GraphNode {
  id: string;
  label: string;
  name: string;
  category?: string;
  source_path?: string;
}

export interface GraphLink {
  source: string;
  target: string;
  type: string;
}

export interface GraphResponse {
  status: "ok";
  nodes: GraphNode[];
  links: GraphLink[];
  node_count: number;
  link_count: number;
}

export interface TechnicalInfo {
  status: "ok";
  server_name: string;
  read_only: boolean;
  tools: string[];
  resources: string[];
  limits: Record<string, number>;
  api_endpoints: string[];
}

export interface OpenApiOperation {
  summary?: string;
  description?: string;
}

export interface OpenApiPathItem {
  get?: OpenApiOperation;
  post?: OpenApiOperation;
  put?: OpenApiOperation;
  patch?: OpenApiOperation;
  delete?: OpenApiOperation;
}

export interface OpenApiSpec {
  openapi: string;
  info: {
    title: string;
    version: string;
  };
  paths: Record<string, OpenApiPathItem>;
}

export interface ReadyResponse {
  status: string;
  read_only?: boolean;
  ready?: boolean;
  vector_query_ok?: boolean;
  errors?: string[];
}

export interface UploadPreview {
  status: "ok" | "warning";
  filename: string;
  name: string;
  description: string;
  line_count: number;
  word_count: number;
  warnings: string[];
  persisted: boolean;
  message: string;
}

export interface GraphQueryRequest {
  query: string;
  ollama_endpoint: string;
  model: string;
}

export interface OllamaModel {
  name: string;
  running: boolean;
}

export interface OllamaModelsResponse {
  status: "ok";
  ollama_endpoint: string;
  models: OllamaModel[];
}

export interface GraphQueryResponse {
  status: "ok";
  answer: string;
  model: string;
  ollama_endpoint: string;
  evidence: {
    route?: string;
    routing?: {
      route?: string;
      confidence?: number;
      suggested_tool?: string;
      resolved_skill_id?: string;
      rationale?: string;
    };
    recommendations?: Array<{
      skill_id: string;
      skill_name: string;
      rationale: string;
      source_paths: string[];
      evidence_snippets: string[];
      evidence_anchors?: Array<{
        retrieval_unit_id: string;
        source_path: string;
        heading_path: string;
        section_id: string;
        line_start: number;
        line_end: number;
      }>;
      evidence_paths?: string[];
    }>;
    skill?: {
      skill_id: string;
      skill_name: string;
      aliases?: string[];
      retrieval_units?: Array<{
        retrieval_unit_id: string;
        text: string;
        source_path: string;
        heading_path?: string;
        section_id: string;
        line_start?: number;
        line_end?: number;
      }>;
    };
    context?: {
      skill_id?: string;
      skill_name?: string;
      related_skill_ids?: string[];
      evidence_paths?: string[];
    };
    execution_guide?: {
      skill_id?: string;
      skill_name?: string;
      when_to_use?: string;
      objective?: string;
      procedure?: string;
      rules?: string;
      related_skill_ids?: string[];
      evidence_paths?: string[];
    };
  };
}
