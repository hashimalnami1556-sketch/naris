"""CALL OF NARIS UI-001: Non-destructive reference texture importer for UE5.7 Editor.

Requires downloaded UI-001 handoff package unpacked with manifest.json next to SourceReferences/.
Does NOT create interactive UMG widgets or replace any existing game assets.
"""
from pathlib import Path
import json
import unreal

ROOT = Path(__file__).resolve().parent.parent
manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
if manifest.get("approval") != "OWNER_APPROVED_VISUAL_REFERENCE":
    raise ValueError("UI-001 owner approval manifest required")

target_dir = "/Game/NARIS/UI/ApprovedReferences"
asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
for item in manifest["assets"]:
    source = ROOT / item["reference_image"]
    if not source.is_file():
        raise FileNotFoundError(source)
    target_asset = target_dir + "/" + source.stem
    if unreal.EditorAssetLibrary.does_asset_exist(target_asset):
        unreal.log_warning("UI-001 preserving existing asset: " + target_asset)
        continue
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", str(source))
    task.set_editor_property("destination_path", target_dir)
    task.set_editor_property("destination_name", source.stem)
    task.set_editor_property("automated", True)
    task.set_editor_property("replace_existing", False)
    task.set_editor_property("save", True)
    asset_tools.import_asset_tasks([task])
    if not unreal.EditorAssetLibrary.does_asset_exist(target_asset):
        raise RuntimeError("UI-001 failed to import " + target_asset)
    unreal.log("UI-001 reference import OK: " + target_asset)

unreal.log_warning("UI-001 reference textures imported. Live UMG bindings and PIE QA remain REQUIRED.")
