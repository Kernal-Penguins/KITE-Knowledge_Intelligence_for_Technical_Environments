export interface HealthService {
  status: "connected" | "unreachable";
}

export interface HealthResponse {
  status: "ok" | "degraded";
  services: {
    neo4j: HealthService;
    qdrant: HealthService;
    postgres: HealthService;
  };
  timestamp: string;
}

export interface VersionResponse {
  version: string;
  build: string;
  environment: string;
}

export interface MetricsResponse {
  documents_ingested: number;
  graph_nodes: number;
  graph_edges: number;
  qdrant_vectors: number;
  queries_served: number;
  avg_response_ms: number;
  agent_invocations: {
    rca: number;
    compliance: number;
    lessons: number;
  };
}

export type DocType = string;

export interface IngestResponse {
  job_id: string;
  doc_id: string;
  filename: string;
  doc_type: DocType;
  status: string;
  message: string;
}

export interface QueryResponse {
  answer: string;
  confidence: number;
  citations: Record<string, unknown>;
}

// The RCA / lessons-clustering / compliance-audit response shapes,
// confirmed from rca_service.py, lessons_service.py, compliance_service.py.

export interface RcaResponse {
  equipment_id?: string;
  report?: string;
  evidence_count?: number;
  error?: string;
}

export interface LessonsClusterResponse {
  status?: "skipped";
  reason?: string;
  processed_failures?: number;
  similarity_threshold?: number;
  new_relationships_created?: number;
}

export interface ComplianceGap {
  gap: string;
  flag_hash: string;
  // remaining fields vary by rule: equipment_id, work_order_id, failure_id,
  // regulation_id, incident_id
  [key: string]: string;
}

export interface ComplianceAuditResponse {
  status: "passed" | "failed";
  total_gaps: number;
  details: Record<string, ComplianceGap[]>;
}

export interface ComplianceReviewResponse {
  status: string;
  flag_hash: string;
  new_status: string;
}
