import { NarisWorkerRequest, NarisWorkerEvent, WORKER_PROTOCOL } from "./worker-protocol.js";
import { NarisJob } from "./job-queue.js";
import { isBlenderOperation } from "./blender-worker.js";

export function toWorkerRequest(job: NarisJob): NarisWorkerRequest {
  if (!isBlenderOperation(job.operation)) {
    throw new Error(`NARIS_PIPELINE_NOT_FOUND: unsupported operation ${job.operation}`);
  }
  return {
    protocol: WORKER_PROTOCOL,
    jobId: job.jobId,
    operation: job.operation,
    assetId: job.assetId,
    parameters: job.parameters,
  };
}

export function validateWorkerEvent(event: NarisWorkerEvent): NarisWorkerEvent {
  if (event.protocol !== WORKER_PROTOCOL) throw new Error("NARIS_WORKER_PROTOCOL_MISMATCH");
  if (!Number.isFinite(event.progress) || event.progress < 0 || event.progress > 100) {
    throw new Error("NARIS_WORKER_INVALID_PROGRESS");
  }
  return event;
}

/** Transport-neutral runtime adapter. A real transport can implement send() and feed events back. */
export interface WorkerTransport {
  send(request: NarisWorkerRequest): Promise<void>;
}

export async function submitToWorker(job: NarisJob, transport?: WorkerTransport): Promise<NarisWorkerRequest> {
  const request = toWorkerRequest(job);
  if (transport) await transport.send(request);
  return request;
}
