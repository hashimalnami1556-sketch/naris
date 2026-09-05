export interface NarisWorkerRequest {
  protocol: "naris-worker/v1";
  jobId: string;
  operation: string;
  assetId?: string;
  parameters: Record<string, unknown>;
}

export interface NarisWorkerEvent {
  protocol: "naris-worker/v1";
  jobId: string;
  status: "RUNNING" | "SUCCEEDED" | "FAILED" | "CANCELLED";
  progress: number;
  message?: string;
  result?: Record<string, unknown>;
  errors?: string[];
  warnings?: string[];
}

/** Stable transport boundary. Implementations may use stdio, localhost HTTP, or a named pipe.
 * The payload deliberately contains operation names only; arbitrary Blender Python is forbidden.
 */
export const WORKER_PROTOCOL = "naris-worker/v1" as const;
