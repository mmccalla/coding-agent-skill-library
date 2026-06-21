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
