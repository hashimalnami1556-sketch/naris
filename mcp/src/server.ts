import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fs from "node:fs/promises";
import path from "node:path";
import { createJob, getJob, updateJob, cancelJob } from "./job-queue.js";
import { dispatchToBlender, isBlenderOperation } from "./blender-worker.js";
import { hasPermission, NarisPermission } from "./permissions.js";

const REPO = process.env.NARIS_REPO ?? process.cwd();
const app = new McpServer({ name: "naris-mcp", version: "1.0.0" });
const out = (value: unknown) => ({ content: [{ type: "text" as const, text: JSON.stringify(value, null, 2) }] });
const has = async (relative: string) => { try { await fs.access(path.join(REPO, relative)); return true; } catch { return false; } };
const readJson = async (relative: string) => { try { return JSON.parse(await fs.readFile(path.join(REPO, relative), "utf8")); } catch { return null; } };

const permissions = (): NarisPermission[] => (process.env.NARIS_PERMISSIONS ?? "project.read,asset.read,validation.run")
  .split(",").map(v => v.trim()).filter(Boolean) as NarisPermission[];
const requirePermission = (p: NarisPermission) => { if (!hasPermission(permissions(), p)) throw new Error(`NARIS_PERMISSION_DENIED: requires ${p}`); };

const enqueue = async (operation: string, parameters: Record<string, unknown>, assetId: string | undefined, permission: NarisPermission) => {
  requirePermission(permission);
  if (!isBlenderOperation(operation)) throw new Error(`NARIS_PIPELINE_NOT_FOUND: unsupported operation ${operation}`);
  const job = createJob(operation, parameters, assetId);
  updateJob(job.jobId, { status: "RUNNING", startedAt: new Date().toISOString(), progress: 1 });
  try {
    const handoff = await dispatchToBlender(job);
    const worker = handoff.worker as { status?: string; progress?: number; result?: Record<string, unknown>; errors?: string[]; warnings?: string[] } | undefined;
    if (!handoff.dispatched) {
      updateJob(job.jobId, { status: "BLOCKED", result: handoff, warnings: ["Blender Worker transport is not connected; no runtime success is claimed."] });
    } else if (worker?.status === "SUCCEEDED") {
      updateJob(job.jobId, { status: "SUCCEEDED", progress: worker.progress ?? 100, completedAt: new Date().toISOString(), result: worker.result, errors: worker.errors ?? [], warnings: worker.warnings ?? [] });
    } else if (worker?.status === "FAILED") {
      updateJob(job.jobId, { status: "FAILED", progress: worker.progress ?? 0, completedAt: new Date().toISOString(), errors: worker.errors ?? ["Blender Worker reported failure"], warnings: worker.warnings ?? [] });
    } else {
      updateJob(job.jobId, { status: "RUNNING", progress: worker?.progress ?? 1, result: handoff, warnings: worker?.warnings ?? [] });
    }
  } catch (error) {
    updateJob(job.jobId, { status: "FAILED", completedAt: new Date().toISOString(), errors: [error instanceof Error ? error.message : String(error)] });
  }
  return getJob(job.jobId);
};

app.registerTool("naris.project.status", { description: "Read-only CALL OF NARIS project status.", inputSchema: {} }, async () => out({ repository: "hashimalnami1556-sketch/naris", mcp_version: "1.0.0", runtime: "Unreal Engine", asset_runtime: "Blender 4.x", milestone: "v2.0 Unified Master / W04 Ashen Forest Vertical Slice", worker_transport: process.env.NARIS_BLENDER_WORKER_URL ? "HTTP_CONFIGURED" : "NOT_CONFIGURED", repository_available_locally: await has("README.md") }));
app.registerTool("naris.project.get_settings", { description: "Return non-sensitive NARIS production settings.", inputSchema: {} }, async () => out({ asset_id_format: "NARIS-W<world>-<domain>-<type>-<sequence>", worlds: ["W01","W02","W03","W04","W05","W06","W07","W08","W09","W10"], domains: ["ENV","CHR","WPN","PROP","MAT","VFX","SFX","UI","CINE","QUEST"], export_formats: ["glb","gltf","fbx","obj"], texture_resolution_default: 4096, uv_margin_default: 0.02, auto_smooth_angle_default: 60, collision_mode_default: "CONVEX" }));

app.registerTool("naris.asset.list", { description: "List repository asset files.", inputSchema: { prefix: z.string().optional(), limit: z.number().int().min(1).max(200).default(50) } }, async ({ prefix, limit }) => {
  const root = path.join(REPO, prefix ?? "assets"); const files: string[] = [];
  const walk = async (dir: string): Promise<void> => { if (files.length >= limit) return; try { for (const e of await fs.readdir(dir, { withFileTypes: true })) { if (files.length >= limit) break; const full = path.join(dir, e.name); if (e.isDirectory()) await walk(full); else files.push(path.relative(REPO, full).replaceAll(path.sep, "/")); } } catch {} };
  await walk(root); return out({ root: prefix ?? "assets", count: files.length, files });
});
app.registerTool("naris.asset.search", { description: "Search asset paths by text.", inputSchema: { query: z.string().min(1), prefix: z.string().optional(), limit: z.number().int().min(1).max(100).default(50) } }, async ({ query, prefix, limit }) => {
  const root = path.join(REPO, prefix ?? "assets"); const files: string[] = []; const needle = query.toLowerCase();
  const walk = async (dir: string): Promise<void> => { if (files.length >= limit) return; try { for (const e of await fs.readdir(dir, { withFileTypes: true })) { if (files.length >= limit) break; const full = path.join(dir, e.name); const rel = path.relative(REPO, full).replaceAll(path.sep, "/"); if (rel.toLowerCase().includes(needle)) files.push(rel); if (e.isDirectory()) await walk(full); } } catch {} };
  await walk(root); return out({ query, count: files.length, files });
});
app.registerTool("naris.asset.get", { description: "Read asset metadata from known registries.", inputSchema: { assetId: z.string().min(1) } }, async ({ assetId }) => {
  const candidates = ["data/MASTER_ASSET_REGISTRY.json", "data/assets.json", "assets/registry.json"];
  for (const file of candidates) { const data = await readJson(file); const items = Array.isArray(data) ? data : Array.isArray(data?.assets) ? data.assets : []; const found = items.find((x: any) => x?.asset_id === assetId || x?.assetId === assetId || x?.id === assetId); if (found) return out({ found: true, registry: file, asset: found }); }
  return out({ found: false, assetId, searched_registries: candidates });
});
app.registerTool("naris.asset.inspect", { description: "Read-only repository inspection; geometry runtime requires Blender Worker.", inputSchema: { assetId: z.string().min(1), relativePath: z.string().optional() } }, async ({ assetId, relativePath }) => out({ assetId, relativePath: relativePath ?? null, inspection_mode: "repository_metadata_only", blender_runtime_required_for_geometry: true, unrestricted_blender_python: false }));
app.registerTool("naris.asset.validate", { description: "Validate canonical NARIS Asset ID and filename prefix.", inputSchema: { assetId: z.string(), filename: z.string().optional() } }, async ({ assetId, filename }) => { const canonical = /^NARIS-W(0[1-9]|10)-[A-Z]{3,5}-[A-Z0-9]+-\d{4}$/.test(assetId); const match = !filename || filename.startsWith(`${assetId}_`); return out({ valid: canonical && match, assetId, filename: filename ?? null, canonical_id: canonical, filename_prefix_matches_asset_id: match }); });
app.registerTool("naris.validation.run", { description: "Run repository evidence checks; runtime geometry/UV/material QA requires Blender Worker.", inputSchema: { assetId: z.string().optional() } }, async ({ assetId }) => { requirePermission("validation.run"); return out({ assetId: assetId ?? null, validation_scope: "repository_contract", checks: { master_spec: await has("docs/NARIS_V2_MASTER_EXECUTION.md"), integration_contract: await has("docs/INTEGRATION_ARCHITECTURE.md"), asset_naming: await has("docs/ASSET_NAMING.md"), mcp_spec: await has("mcp/SPEC.md") }, geometry_uv_material_runtime_validation: "REQUIRES_BLENDER_WORKER", status: "EVIDENCE_BOUND" }); });
app.registerTool("naris.validation.get_report", { description: "Retrieve validation report metadata.", inputSchema: { reportPath: z.string().optional() } }, async ({ reportPath }) => out({ reportPath: reportPath ?? null, available: reportPath ? await has(reportPath) : false }));

app.registerTool("naris.asset.build", { description: "Queue controlled BUILD_ASSET.", inputSchema: { assetId: z.string().min(1), parameters: z.record(z.string(), z.unknown()).default({}) } }, async ({ assetId, parameters }) => out(await enqueue("BUILD_ASSET", parameters, assetId, "asset.build")));
app.registerTool("naris.asset.generate_lod", { description: "Queue controlled LOD generation.", inputSchema: { assetId: z.string().min(1), ratios: z.array(z.number().positive()).optional() } }, async ({ assetId, ratios }) => out(await enqueue("GENERATE_LOD", { ratios: ratios ?? [1, .5, .25, .1] }, assetId, "asset.build")));
app.registerTool("naris.asset.generate_collision", { description: "Queue controlled collision generation.", inputSchema: { assetId: z.string().min(1), mode: z.enum(["CONVEX","BOX","CAPSULE","MESH"]).default("CONVEX") } }, async ({ assetId, mode }) => out(await enqueue("GENERATE_COLLISION", { mode }, assetId, "asset.build")));
app.registerTool("naris.texture.process", { description: "Queue controlled texture processing.", inputSchema: { assetId: z.string().min(1), resolution: z.number().int().positive().max(16384).default(4096) } }, async ({ assetId, resolution }) => out(await enqueue("PROCESS_TEXTURES", { resolution }, assetId, "asset.build")));
app.registerTool("naris.asset.export", { description: "Queue controlled asset export; runtime completion is evidence-bound.", inputSchema: { assetId: z.string().min(1), format: z.enum(["glb","gltf","fbx","obj"]), profile: z.enum(["UNREAL_GAME_READY","UNITY_GAME_READY","GODOT_GAME_READY","GENERIC_GLTF","ARCHIVE_SOURCE"]).default("UNREAL_GAME_READY") } }, async ({ assetId, format, profile }) => out(await enqueue("EXPORT_ASSET", { format, profile }, assetId, "asset.export")));

app.registerTool("naris.job.status", { description: "Return a NARIS job record.", inputSchema: { jobId: z.string().min(1) } }, async ({ jobId }) => out(getJob(jobId) ?? { jobId, found: false }));
app.registerTool("naris.job.cancel", { description: "Cancel a queued/running/approval-required job.", inputSchema: { jobId: z.string().min(1) } }, async ({ jobId }) => { requirePermission("asset.build"); return out(cancelJob(jobId) ?? { jobId, found: false }); });
app.registerTool("naris.report.generate", { description: "Generate repository evidence summary.", inputSchema: { assetId: z.string().optional() } }, async ({ assetId }) => out({ report_type: "repository_evidence", assetId: assetId ?? null, generated_at: new Date().toISOString(), evidence: { readme: await has("README.md"), integration: await has("docs/INTEGRATION_ARCHITECTURE.md"), naming: await has("docs/ASSET_NAMING.md"), mcp_spec: await has("mcp/SPEC.md") }, runtime_claims: "NOT_VERIFIED" }));

app.registerTool("naris_project_status", { description: "Compatibility alias.", inputSchema: {} }, async () => out({ alias_for: "naris.project.status" }));
app.registerTool("naris_asset_validate", { description: "Compatibility alias.", inputSchema: { assetId: z.string(), filename: z.string().optional() } }, async ({ assetId, filename }) => out({ alias_for: "naris.asset.validate", assetId, filename: filename ?? null }));
app.registerTool("naris_vertical_slice_status", { description: "W04 Ashen Forest evidence status.", inputSchema: {} }, async () => out({ world: "W04", name: "Ashen Forest", status: "SPEC_READY / RUNTIME_VALIDATION_REQUIRED" }));
app.registerTool("naris_qa_report", { description: "Evidence-backed QA metadata.", inputSchema: {} }, async () => out({ runtime_validation_required: true, mcp_spec: await has("mcp/SPEC.md") }));
app.registerTool("naris_build_status", { description: "Build status without invented success.", inputSchema: {} }, async () => out({ production_runtime: "Unreal Engine", build_claim: "NOT_VERIFIED" }));

await app.connect(new StdioServerTransport());
