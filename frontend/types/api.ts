export interface TemplateResponse {
  template_id: string;
  design_system: Record<string, unknown>;
  confidence: number;
  patterns_count: number;
}

export interface ContentResponse {
  content_id: string;
  size: number;
}

export interface GenerateRequest {
  template_id: string;
  content_id: string;
  brief: string;
  variants: number;
}

export interface GenerateResponse {
  job_id: string;
  status: string;
  estimated_seconds: number;
}

export interface PresentationVariant {
  variant_id: number;
  variant_name: string;
  pptx_url: string;
  pdf_url?: string;
  html_url?: string;
}

export interface AuditProblem {
  slide_id: number;
  rule_id: string;
  severity: "error" | "warning" | "info";
  message: string;
}

export interface AuditReport {
  total_problems: number;
  by_severity: Record<string, number>;
  problems: AuditProblem[];
}

export interface JobStatusResponse {
  job_id: string;
  status: "processing" | "done" | "error";
  progress: number;
  stage?: string;
  message?: string;
  result?: {
    presentations: PresentationVariant[];
    audit_report: AuditReport;
  };
  error?: string;
}
