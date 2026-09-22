import fs from "node:fs/promises";
import path from "node:path";

export interface RegistryAsset {
  assetId: string;
  name: string;
  type: string;
  sourcePath: string;
  status: "planned" | "source" | "processing" | "validated" | "integrated" | "blocked";
  runtimePath?: string;
  validation?: Record<string, unknown>;
}

export interface AssetManifest {
  schemaVersion: "1.0.0";
  generatedAt: string;
  assets: RegistryAsset[];
}

const repo = () => process.env.NARIS_REPO ?? process.cwd();
const registryPath = () => path.join(repo(), "data", "MASTER_ASSET_REGISTRY.json");
const canonical = /^NARIS-W(0[1-9]|10)-(ENV|CHR|WPN|PROP|MAT|VFX|SFX|UI|CINE|QUEST)-[A-Z0-9]+-\d{4}$/;

async function readJson(relative: string): Promise<any> {
  try { return JSON.parse(await fs.readFile(path.join(repo(), relative), "utf8")); }
  catch { return null; }
}

export async function loadRegistry(): Promise<AssetManifest> {
  const data = await readJson("data/MASTER_ASSET_REGISTRY.json");
  if (data?.schemaVersion === "1.0.0" && Array.isArray(data.assets)) return data;
  return { schemaVersion: "1.0.0", generatedAt: new Date(0).toISOString(), assets: [] };
}

export async function registryStatus() {
  const manifest = await loadRegistry();
  const invalidIds = manifest.assets.filter(a => !canonical.test(a.assetId)).map(a => a.assetId);
  const duplicateIds = manifest.assets.map(a => a.assetId).filter((id, i, all) => all.indexOf(id) !== i);
  const byStatus = Object.fromEntries(["planned","source","processing","validated","integrated","blocked"].map(s => [s, manifest.assets.filter(a => a.status === s).length]));
  return { path: "data/MASTER_ASSET_REGISTRY.json", count: manifest.assets.length, byStatus, invalidIds: [...new Set(invalidIds)], duplicateIds: [...new Set(duplicateIds)], healthy: invalidIds.length === 0 && duplicateIds.length === 0 };
}

export async function getRegistryAsset(assetId: string) {
  const manifest = await loadRegistry();
  return manifest.assets.find(a => a.assetId === assetId) ?? null;
}

export async function searchRegistry(query: string, limit = 50) {
  const q = query.toLowerCase();
  const manifest = await loadRegistry();
  return manifest.assets.filter(a => [a.assetId,a.name,a.type,a.sourcePath,a.runtimePath ?? ""].some(v => v.toLowerCase().includes(q))).slice(0, limit);
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
  const extensions = Object.fromEntries([...new Set(files.map(f => path.extname(f).toLowerCase() || "(none)"))].sort().map(ext => [ext, files.filter(f => (path.extname(f).toLowerCase() || "(none)") === ext).length]));
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
