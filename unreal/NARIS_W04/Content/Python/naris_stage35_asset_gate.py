"""Stage35: non-destructive UE5.7 editor audit and opt-in material setup.
Run in Unreal Editor Python; creates only new /Game/NARIS/_Import/Stage35 paths.
Never claims to build a playable map or import missing binaries.
"""
import json
from pathlib import Path
import unreal

DEST = "/Game/NARIS/_Import/Stage35"
SAVED = Path(unreal.Paths.project_saved_dir()) / "TestReports" / "stage35_asset_gate.json"
ASSET_LABELS = {
    "hero": "/Game/NARIS/Characters",
    "maps": "/Game/NARIS/W04/Maps",
    "animations": "/Game/NARIS/Animations",
    "materials": "/Game/NARIS/Materials",
}
report = {"stage": 35, "engine": str(unreal.SystemLibrary.get_engine_version()),
          "assets": {}, "material_created": False, "blockers": []}
for name, folder in ASSET_LABELS.items():
    exists = unreal.EditorAssetLibrary.does_directory_exist(folder)
    assets = unreal.EditorAssetLibrary.list_assets(folder, recursive=True, include_folder=False) if exists else []
    report["assets"][name] = {"folder": folder, "exists": bool(exists), "count": len(assets)}
    if not assets:
        report["blockers"].append("Missing or empty asset folder: " + folder)
# Author a baseline UE material asset without replacing anything.
unreal.EditorAssetLibrary.make_directory(DEST)
mat_path = DEST + "/M_NarisStage35_Preview"
if unreal.EditorAssetLibrary.does_asset_exist(mat_path):
    report["blockers"].append("Preview material already exists; preserving it")
else:
    factory = unreal.MaterialFactoryNew()
    material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "M_NarisStage35_Preview", DEST, unreal.Material, factory)
    if material is None:
        report["blockers"].append("Could not create preview material")
    else:
        unreal.MaterialEditingLibrary.set_material_property(material, unreal.MaterialProperty.MP_ROUGHNESS, 0.78)
        unreal.MaterialEditingLibrary.recompile_material(material)
        unreal.EditorAssetLibrary.save_loaded_asset(material)
        report["material_created"] = True
report["status"] = "audit_complete_with_blockers" if report["blockers"] else "audit_complete"
SAVED.parent.mkdir(parents=True, exist_ok=True)
SAVED.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
unreal.log("NARIS Stage35 report: " + str(SAVED))
