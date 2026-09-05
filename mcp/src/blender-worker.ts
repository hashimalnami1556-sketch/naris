import { NarisJob, getJob } from "./job-queue.js";
import { submitToWorker, validateWorkerEvent } from "./worker-runtime.js";
import type { NarisWorkerEvent } from "./worker-protocol.js";

/** Controlled execution boundary for Blender. Named operations only; never arbitrary Python. */
export type BlenderOperation =
  | "VALIDATE_ASSET"
  | "BUILD_ASSET"
  | "GENERATE_LOD"
  | "GENERATE_COLLISION"
  | "PROCESS_TEXTURES"
  | "RENDER_PREVIEW"
  | "EXPORT_ASSET";

const allowed = new Set<BlenderOperation>([
  "VALIDATE_ASSET",
  "BUILD_ASSET",
  "GENERATE_LOD",
  "GENERATE_COLLISION",
  "PROCESS_TEXTURES",
  "RENDER_PREVIEW",
  "EXPORT_ASSET"
]);

export function isBlenderOperation(value: string): value is BlenderOperation {
  return allowed.has(value as BlenderOperation);
}

export async function dispatchToBlender(job: NarisJob): Promise<Record<string, unknown>> {
  if (!isBlenderOperation(job.operation)) {
    throw new Error(`NARIS_PIPELINE_NOT_FOUND: unsupported Blender operation ${job.operation}`);
  }

  const url = process.env.NARIS_BLENDER_WORKER_URL;
  if (!url) {
    return {
      dispatched: false,
      status: "BLENDER_WORKER_NOT_CONNECTED",
      jobId: job.jobId,
      operation: job.operation,
      nextStep: "Set NARIS_BLENDER_WORKER_URL to the local Blender Worker HTTP endpoint."
    };
  }

  const request = await submitToWorker(job);
  const response = await fetch(url.replace(/\/$/, "") + "/v1/jobs", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(request),
    signal: AbortSignal.timeout(Number(process.env.NARIS_WORKER_TIMEOUT_MS ?? 10000))
  });
  if (!response.ok) throw new Error(`NARIS_WORKER_HTTP_${response.status}`);

  const event = validateWorkerEvent((await response.json()) as NarisWorkerEvent);
  return { dispatched: true, worker: event };
}

export function workerJobExists(jobId: string): boolean {
  return Boolean(getJob(jobId));
}
