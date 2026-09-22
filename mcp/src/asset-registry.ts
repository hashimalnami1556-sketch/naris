import fs from "node:fs/promises";
import path from "node:path";

export interface RegistryAsset {
  id: string;
  name: string;
  domain?: string;
  type?: string;
  world?: string;
  status?: string;
  source?: string;
  engine_target?: string;
  preview_engine?: string;
  notes?: string;
  runtime_path?: string;
}

export interface AssetRegistry {
  schema_version: string;
  project?: string;
  asset_id_format?: string;
  status_flow?: string[];
  worlds?: Array<{ id: string; name: string }>;
  assets: RegistryAsset[];
}

const repo = () => process.env.NARIS_REPO ?? process.cwd();
const canonical = /^NARIS-W(0[1-9]|10)-[A-Z]{2,5}-[A-Z0-9]+-\d{4}$/;

async function readJson(relative: string): Promise<any> {
  try { return JSON.parse(await fs.readFile(path.join(repo(), relative), "utf8")); }
  catch { return null; }
}

export async function loadRegistry(): Promise<AssetRegistry> {
  const data = await readJson("data/MASTER_ASSET_REGISTRY.json");
  if (data && Array.isArray(data.assets)) return data as AssetRegistry;
  return { schema_version: "unknown", assets: [] };
}

export async function registryStatus() {
  const manifest = await loadRegistry();
  const invalidIds = manifest.assets.filter(a => !canonical.test(a.id)).map(a => a.id);
  const duplicateIds = manifest.assets.map(a => a.id).filter((id, i, all) => all.indexOf(id) !== i);
  const statuses = [...new Set(manifest.assets.map(a => a.status ?? "unknown"))].sort();
  const byStatus = Object.fromEntries(statuses.map(s => [s, manifest.assets.filter(a => (a.status ?? "unknown") === s).length]));
  const byWorld = Object.fromEntries([..."01020304050607080910"].matchAll(/../g)].map(m => `W${m[0]}`).map(w => [w, manifest.assets.filter(a => a.world === w).length]));
  return { path: "data/MASTER_ASSET_REGISTRY.json", schemaVersion: manifest.schema_version, count: manifest.assets.length, byStatus, byWorld, invalidIds: [...new Set(invalidIds)], duplicateIds: [...new Set(duplicateIds)], healthy: invalidIds.length === 0 && duplicateIds.length === 0 };
}

export async function getRegistryAsset(assetId: string) {
  const manifest = await loadRegistry();
  return manifest.assets.find(a => a.id === assetId) ?? null;
}

export async function searchRegistry(query: string, limit = 50) {
  const q = query.toLowerCase();
  const manifest = await loadRegistry();
  return manifest.assets.filter(a => [a.id,a.name,a.domain ?? "",a.type ?? "",a.world ?? "",a.status ?? "",a.source ?? "",a.engine_target ?? "",a.notes ?? ""].some(v => v.toLowerCase().includes(q))).slice(0, limit);
}

export async function scanUnrealW04() {
  const root = path.join(repo(), "unreal", "NARIS_W04");
  const files: string[] = [];
  const walk = async (dir: string): Promise<void> => {
    try {
      for (const entry of await fs.readdir(dir, { withFileTypes: true })) {
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) await walk(full);
        else files.push(path.relative(repo(), full).replaceAll(path.sep, "/"));
      }
    } catch {}
  };
  await walk(root);
  const exts = [...new Set(files.map(f => path.extname(f).toLowerCase() || "(none)"))].sort();
  const extensions = Object.fromEntries(exts.map(ext => [ext, files.filter(f => (path.extname(f).toLowerCase() || "(none)") === ext).length]));
  const manifest = await readJson("unreal/NARIS_W04/Content/NARIS/W04/Data/W04_VerticalSliceManifest.json");
  return {
    project: "unreal/NARIS_W04/NARIS_W04.uproject",
    fileCount: files.length,
    extensions,
    verticalSlice: manifest,
    nativeCodeFiles: files.filter(f => /\/Source\/.*\.(h|cpp)$/.test(f)),
    contentContracts: files.filter(f => /\/Content\/.*\.(md|json)$/.test(f)),
    runtimeBinaryAssets: files.filter(f => /\.(uasset|umap)$/.test(f)),
    evidence: {
      projectDescriptor: files.includes("unreal/NARIS_W04/NARIS_W04.uproject"),
      verticalSliceManifest: files.includes("unreal/NARIS_W04/Content/NARIS/W04/Data/W04_VerticalSliceManifest.json"),
      hasRuntimeBinaryAssets: files.some(f => /\.(uasset|umap)$/.test(f))
    }
  };
}
