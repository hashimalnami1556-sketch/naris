import fs from "node:fs/promises";
import path from "node:path";
import { createHash } from "node:crypto";
import type { NarisJob } from "./job-queue.js";

export interface NarisArtifact {
  artifactId: string;
  jobId: string;
  assetId?: string;
  kind: "EXPORT" | "PREVIEW" | "VALIDATION" | "BUILD" | "OTHER";
  path: string;
  sizeBytes?: number;
  sha256?: string;
  createdAt: string;
  verified: boolean;
}

export interface NarisAuditRecord {
  auditId: string;
  timestamp: string;
  action: string;
  jobId?: string;
  assetId?: string;
  status: string;
  artifactIds: string[];
  evidence: string[];
}

const root = () => path.join(process.env.NARIS_REPO ?? process.cwd(), "data");
const artifactsFile = () => path.join(root(), "artifacts.json");
const auditFile = () => path.join(root(), "audit.json");

async function readArray<T>(file: string): Promise<T[]> {
  try {
    const value = JSON.parse(await fs.readFile(file, "utf8"));
    return Array.isArray(value) ? value : [];
  } catch { return []; }
}

async function append<T>(file: string, value: T): Promise<void> {
  await fs.mkdir(path.dirname(file), { recursive: true });
  const items = await readArray<T>(file);
  items.push(value);
  await fs.writeFile(file, JSON.stringify(items, null, 2) + "\n", "utf8");
}

function artifactKind(operation: string): NarisArtifact["kind"] {
  if (operation === "EXPORT_ASSET") return "EXPORT";
  if (operation === "RENDER_PREVIEW") return "PREVIEW";
  if (operation === "VALIDATE_ASSET") return "VALIDATION";
  if (operation === "BUILD_ASSET" || operation === "GENERATE_LOD" || operation === "GENERATE_COLLISION") return "BUILD";
  return "OTHER";
}

async function sha256(file: string): Promise<string | undefined> {
  try {
    const data = await fs.readFile(file);
    return createHash("sha256").update(data).digest("hex");
  } catch { return undefined; }
}

export async function recordJobEvidence(job: NarisJob): Promise<NarisArtifact[]> {
  const result = job.result ?? {};
  const candidates = [result.path, result.output, result.artifact_path, result.export_path]
    .filter((v): v is string => typeof v === "string" && v.length > 0);
  const artifacts: NarisArtifact[] = [];
  for (const candidate of candidates) {
    const resolved = path.isAbsolute(candidate) ? candidate : path.join(process.env.NARIS_REPO ?? process.cwd(), candidate);
    try {
      const stat = await fs.stat(resolved);
      if (!stat.isFile()) continue;
      const artifact: NarisArtifact = {
        artifactId: `ART-${job.jobId.replace(/^JOB-/, "")}-${artifacts.length + 1}`,
        jobId: job.jobId,
        assetId: job.assetId,
        kind: artifactKind(job.operation),
        path: path.relative(process.env.NARIS_REPO ?? process.cwd(), resolved).replaceAll(path.sep, "/"),
        sizeBytes: stat.size,
        sha256: await sha256(resolved),
        createdAt: new Date().toISOString(),
        verified: true
      };
      artifacts.push(artifact);
      await append(artifactsFile(), artifact);
    } catch { /* Missing artifact means no runtime success evidence. */ }
  }
  return artifacts;
}

export async function recordAudit(job: NarisJob, artifacts: NarisArtifact[]): Promise<NarisAuditRecord> {
  const record: NarisAuditRecord = {
    auditId: `AUD-${job.jobId.replace(/^JOB-/, "")}`,
    timestamp: new Date().toISOString(),
    action: job.operation,
    jobId: job.jobId,
    assetId: job.assetId,
    status: job.status,
    artifactIds: artifacts.map(a => a.artifactId),
    evidence: [
      `job:${job.jobId}`,
      `operation:${job.operation}`,
      `status:${job.status}`,
      ...(artifacts.length ? ["artifact:verified"] : ["artifact:none"])
    ]
  };
  await append(auditFile(), record);
  return record;
}

export async function getArtifacts(jobId?: string, assetId?: string): Promise<NarisArtifact[]> {
  const items = await readArray<NarisArtifact>(artifactsFile());
  return items.filter(a => (!jobId || a.jobId === jobId) && (!assetId || a.assetId === assetId));
}

export async function getAudit(jobId?: string, assetId?: string): Promise<NarisAuditRecord[]> {
  const items = await readArray<NarisAuditRecord>(auditFile());
  return items.filter(a => (!jobId || a.jobId === jobId) && (!assetId || a.assetId === assetId));
}
