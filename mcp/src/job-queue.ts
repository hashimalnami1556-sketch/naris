import { randomUUID } from "node:crypto";

export type NarisJobStatus = "QUEUED" | "RUNNING" | "SUCCEEDED" | "FAILED" | "CANCELLED" | "BLOCKED" | "REQUIRES_APPROVAL";

export interface NarisJob {
  jobId: string;
  assetId?: string;
  operation: string;
  parameters: Record<string, unknown>;
  status: NarisJobStatus;
  progress: number;
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
  result?: Record<string, unknown>;
  errors: string[];
  warnings: string[];
}

const jobs = new Map<string, NarisJob>();

export function createJob(operation: string, parameters: Record<string, unknown>, assetId?: string): NarisJob {
  const job: NarisJob = {
    jobId: `JOB-${new Date().toISOString().slice(0, 10).replaceAll("-", "")}-${randomUUID().slice(0, 8)}`,
    assetId,
    operation,
    parameters,
    status: "QUEUED",
    progress: 0,
    createdAt: new Date().toISOString(),
    errors: [],
    warnings: []
  };
  jobs.set(job.jobId, job);
  return job;
}

export function getJob(jobId: string): NarisJob | undefined {
  return jobs.get(jobId);
}

export function cancelJob(jobId: string): NarisJob | undefined {
  const job = jobs.get(jobId);
  if (!job) return undefined;
  if (job.status === "QUEUED" || job.status === "RUNNING" || job.status === "REQUIRES_APPROVAL") {
    job.status = "CANCELLED";
    job.completedAt = new Date().toISOString();
  }
  return job;
}
