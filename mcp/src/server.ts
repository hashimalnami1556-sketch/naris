import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import fs from "node:fs/promises";
import path from "node:path";

const REPO = process.env.NARIS_REPO ?? process.cwd();
const app = new McpServer({ name: "naris-mcp", version: "0.1.0" });
const out = (value: unknown) => ({ content: [{ type: "text" as const, text: JSON.stringify(value, null, 2) }] });
const has = async (relative: string) => { try { await fs.access(path.join(REPO, relative)); return true; } catch { return false; } };

app.registerTool("naris_project_status", {
  description: "Read-only CALL OF NARIS project status and production gates.",
  inputSchema: {}
}, async () => out({
  repository: "hashimalnami1556-sketch/naris",
  runtime: "Unreal Engine",
  milestone: "v2.0 Unified Master / W04 Ashen Forest Vertical Slice",
  evidence: ["docs/NARIS_V2_MASTER_EXECUTION.md", "docs/INTEGRATION_ARCHITECTURE.md", "docs/ASSET_NAMING.md"],
  gates: ["Functional", "Visual", "Collision/Interaction", "Performance", "Save/Load", "Regression", "QA"],
  repository_available_locally: await has("README.md")
}));

app.registerTool("naris_asset_validate", {
  description: "Validate canonical NARIS Asset ID and filename.",
  inputSchema: { assetId: z.string(), filename: z.string().optional() }
}, async ({ assetId, filename }) => {
  const canonical = /^NARIS-W(0[1-9]|10)-[A-Z]{3,5}-[A-Z0-9]+-\\d{4}$/.test(assetId);
  const filenameMatches = !filename || filename.startsWith(`${assetId}_`);
  return out({ valid: canonical && filenameMatches, assetId, filename: filename ?? null, canonical_id: canonical, filename_prefix_matches_asset_id: filenameMatches });
});

app.registerTool("naris_vertical_slice_status", {
  description: "Report W04 Ashen Forest vertical-slice evidence status.",
  inputSchema: {}
}, async () => out({
  world: "W04",
  name: "Ashen Forest",
  sequence: ["MAIN MENU", "INTRO", "WAKE AREA", "MOVEMENT", "COMBAT", "MEMORY CRYSTAL", "NARIS WHISPER", "BONE BEAST", "ASH GATE", "CELESTIAL WOLF", "ASH GIANT / MIST GUARDIAN", "DEMO END"],
  evidence: {
    master: await has("docs/NARIS_V2_MASTER_EXECUTION.md"),
    integration: await has("docs/INTEGRATION_ARCHITECTURE.md"),
    naming: await has("docs/ASSET_NAMING.md")
  },
  status: "SPEC_READY / RUNTIME_VALIDATION_REQUIRED"
}));

app.registerTool("naris_qa_report", {
  description: "Generate an evidence-backed QA report. Documentation presence is not a runtime pass.",
  inputSchema: {}
}, async () => out({
  checks: {
    specification: await has("docs/NARIS_V2_MASTER_EXECUTION.md"),
    integration_contract: await has("docs/INTEGRATION_ARCHITECTURE.md"),
    asset_naming: await has("docs/ASSET_NAMING.md"),
    mcp_spec: await has("mcp/SPEC.md")
  },
  runtime_validation_required: true
}));

app.registerTool("naris_build_status", {
  description: "Report build/release status without inventing success.",
  inputSchema: {}
}, async () => out({
  production_runtime: "Unreal Engine",
  build_claim: "NOT VERIFIED",
  required_evidence: ["Packaged Unreal build", "automated tests", "playtest evidence", "performance capture", "QA approval"]
}));

await app.connect(new StdioServerTransport());
