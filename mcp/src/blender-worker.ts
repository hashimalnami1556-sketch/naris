import { getJob, NarisJob } from "./job-queue.js";

/**
 * Controlled execution boundary for Blender.
 * v1 deliberately supports only named operations; it never accepts arbitrary Python.
 */
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

  // Adapter boundary: the actual Blender IPC/worker transport is implemented separately.
  // Returning a deterministic queued handoff prevents the MCP server from falsely claiming execution.
  return {
    dispatched: false,
    status: "BLENDER_WORKER_NOT_CONNECTED",
    jobId: job.jobId,
    operation: job.operation,
    nextStep: "Connect the NARIS Blender Worker transport."
  };
}

export function workerJobExists(jobId: string): boolean {
  return Boolean(getJob(jobId));
}
