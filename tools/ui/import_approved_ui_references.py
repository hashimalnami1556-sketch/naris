"""Import exact owner-approved UI-002 reference PNGs into UE5.7 as Texture2D.

Run inside Unreal Editor Python with NARIS_UI_REFERENCE_ROOT pointing to the
unzipped NARIS_UI_002_REAL_IMAGES directory. Does NOT build UMG widgets.
No replacements, no guessed source images, no changes to live HUD.
"""
import hashlib
import json
import os
import struct
from pathlib import Path

import unreal


def verified_sources(root):
    data = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    if len(data["images"]) != 3:
        raise RuntimeError("Exactly three official references required")
    seen = set()
    items = []
    for item in data["images"]:
        name = item["file"]
        if Path(name).name != name or not name.endswith(".png"):
            raise RuntimeError("Invalid image file name")
        img = root / "References" / name
        buf = img.read_bytes()
        if not buf.startswith(b"\x89PNG\r\n\x1a\n") or buf[12:16] != b"IHDR":
            raise RuntimeError("Invalid PNG source: " + name)
        width, height = struct.unpack(">II", buf[16:24])
        if (width, height) != (item["width"], item["height"]):
            raise RuntimeError("Wrong dimensions: " + name)
        if hashlib.sha256(buf).hexdigest() != item["sha256"]:
            raise RuntimeError("Original reference digest mismatch: " + name)
        if item["asset_name"] in seen:
            raise RuntimeError("Duplicate Unreal texture name")
        seen.add(item["asset_name"])
        items.append((img, item["asset_name"]))
    return items


def main():
    env_root = os.getenv("NARIS_UI_REFERENCE_ROOT")
    if not env_root:
        raise RuntimeError("Set NARIS_UI_REFERENCE_ROOT to extracted UI-002 package root")
    root = Path(env_root).resolve()
    files = verified_sources(root)
    dst = "/Game/NARIS/UI/ApprovedReferences"
    for _, asset in files:
        if unreal.EditorAssetLibrary.does_asset_exist(f"{dst}/{asset}"):
            raise RuntimeError("Refusing to overwrite existing Unreal asset: " + asset)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    imported = []
    for img, asset in files:
        task = unreal.AssetImportTask()
        task.set_editor_property("filename", str(img))
        task.set_editor_property("destination_path", dst)
        task.set_editor_property("destination_name", asset)
        task.set_editor_property("automated", True)
        task.set_editor_property("save", True)
        task.set_editor_property("replace_existing", False)
        tools.import_asset_tasks([task])
        obj = unreal.EditorAssetLibrary.load_asset(f"{dst}/{asset}")
        if not obj or not obj.is_a(unreal.Texture2D):
            raise RuntimeError("Texture2D import failed: " + asset)
        unreal.EditorAssetLibrary.save_loaded_asset(obj)
        imported.append(f"{dst}/{asset}")
    report = {"imported_texture_paths": imported, "widget_blueprints_built": False,
              "unreal_build_tested": False}
    (root / "UE5_Import_Result.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("[NARIS/UI-002] ORIGINAL approved reference images imported as texture assets.")

if __name__ == "__main__":
    main()
