export type NarisJobStatus = "QUEUED" | "RUNNING" | "WAITING" | "SUCCEEDED" | "FAILED" | "CANCELLED" | "BLOCKED" | "REQUIRES_APPROVAL";

export interface NarisJob {
  job_id: string;
  asset_id?: string;
  operation: string;
  pipeline?: string;
  status: NarisJobStatus;
  progress: number;
  created_at: string;
  started_at?: string;
  completed_at?: string;
  result?: unknown;
  errors?: string[];
  warnings?: string[];
  artifacts?: string[];
}

export type ValidationSeverity = "INFO" | "WARNING" | "ERROR" | "BLOCKER";
export type ValidationStatus = "PASS" | "FAIL" | "SKIPPED" | "NOT_APPLICABLE";

export interface ValidationCheck {
  check_id: string;
  category: string;
  severity: ValidationSeverity;
  status: ValidationStatus;
  message: string;
  auto_fixable?: boolean;
  evidence?: string[];
}
