"""Import a validated NARIS Blender exchange package into Unreal Engine 5.4."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

import unreal

ASSET_ID_RE = re.compile(
    r"^NARIS-(W\d{2})-(CHR|ENM|BOS|WPN|PRP|ENV|MAT|VFX|UI|MAP|CINE|AUD|QST)-[A-Z0-9_]+-\d{4}$"
)


def fail(message: str) -> None:
    unreal.log_error(f"NARIS import failed: {message}")
    raise RuntimeError(message)


def load_registry_entry(registry_path: Path, asset_id: str) -> dict:
    if not registry_path.is_file():
        fail(f"Master asset registry does not exist: {registry_path}")

    try:
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"Master asset registry is invalid JSON: {exc}")

    matches = [
        item
        for item in registry.get("assets", [])
        if isinstance(item, dict) and item.get("id") == asset_id
    ]
    if len(matches) != 1:
        fail(
            f"Asset ID must appear exactly once in master registry: "
            f"{asset_id} (matches={len(matches)})"
        )
    return matches[0]


def main() -> None:
    manifest_env = os.environ.get("NARIS_EXCHANGE_MANIFEST", "").strip()
    registry_env = os.environ.get("NARIS_MASTER_REGISTRY", "").strip()
    if not manifest_env:
        fail("NARIS_EXCHANGE_MANIFEST is not set")
    if not registry_env:
        fail("NARIS_MASTER_REGISTRY is not set")

    manifest_path = Path(manifest_env).resolve()
    registry_path = Path(registry_env).resolve()
    if not manifest_path.is_file():
        fail(f"Manifest does not exist: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "naris.blender.exchange.v1":
        fail(f"Unsupported manifest schema: {manifest.get('schema')!r}")
    if manifest.get("status") != "pass":
        fail("Blender validation status is not pass")
    if manifest.get("registry_status") != "registered":
        fail("Blender manifest is not registry-approved")

    asset_id = str(manifest.get("asset_id", ""))
    match = ASSET_ID_RE.match(asset_id)
    if not match:
        fail(f"Invalid NARIS asset ID: {asset_id!r}")

    world = match.group(1)
    registry_entry = load_registry_entry(registry_path, asset_id)
    if registry_entry.get("world") != world:
        fail(
            f"Master registry world mismatch for {asset_id}: "
            f"{registry_entry.get('world')!r} != {world!r}"
        )

    manifest_entry = manifest.get("registry_entry")
    if not isinstance(manifest_entry, dict) or manifest_entry.get("id") != asset_id:
        fail("Manifest registry_entry does not match asset_id")

    base = manifest_path.parent
    candidates = [base / f"{asset_id}.fbx", base / f"{asset_id}.glb"]
    source = next((p for p in candidates if p.is_file()), None)
    if source is None:
        fail(f"No exchange geometry found beside manifest: {candidates}")

    destination = f"/Game/NARIS/Imported/{world}/{asset_id}"

    task = unreal.AssetImportTask()
    task.set_editor_property("filename", str(source))
    task.set_editor_property("destination_path", destination)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", False)
    task.set_editor_property("replace_existing_settings", False)
    task.set_editor_property("save", True)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    asset_tools.import_asset_tasks([task])

    imported = list(task.get_objects())
    if not imported:
        fail(f"Import produced no Unreal objects for {asset_id}")

    for obj in imported:
        unreal.EditorAssetLibrary.set_metadata_tag(
            obj, unreal.Name("NARIS.AssetId"), asset_id
        )
        unreal.EditorAssetLibrary.set_metadata_tag(
            obj, unreal.Name("NARIS.SourceManifest"), str(manifest_path)
        )
        unreal.EditorAssetLibrary.set_metadata_tag(
            obj, unreal.Name("NARIS.SourceBlend"), str(manifest.get("blend_file", ""))
        )
        unreal.EditorAssetLibrary.set_metadata_tag(
            obj, unreal.Name("NARIS.ExchangeSchema"), str(manifest["schema"])
        )
        unreal.EditorAssetLibrary.set_metadata_tag(
            obj, unreal.Name("NARIS.RegistryStatus"), "registered"
        )

    if not unreal.EditorAssetLibrary.save_directory(
        destination, only_if_is_dirty=False, recursive=True
    ):
        fail(f"Could not save Unreal destination directory: {destination}")

    result = {
        "asset_id": asset_id,
        "source": str(source),
        "destination": destination,
        "registry": str(registry_path),
        "imported_objects": [obj.get_path_name() for obj in imported],
        "status": "pass",
    }
    unreal.log("NARIS_IMPORT_RESULT=" + json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
