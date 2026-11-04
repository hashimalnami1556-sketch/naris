"""UI-001: import approved *reference PNGs*, never functional UMG widgets.

Execute inside Unreal Editor Python after unpacking NARIS_UI_001_OFFICIAL_REFERENCES.zip.
Set NARIS_UI_REFERENCE_ROOT to its extracted NARIS_UI_001_OFFICIAL folder.
Never overwrite assets. Import and report are fail-closed.
"""
import hashlib
import json
import os
from pathlib import Path
import unreal


def run():
    root = Path(os.environ["NARIS_UI_REFERENCE_ROOT"]).resolve()
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    destination = "/Game/NARIS/UI/ApprovedReferences"
    report = []
    for item in manifest["artifacts"]:
        source = (root / item["file"]).resolve()
        if not source.is_relative_to(root) or source.suffix.lower() != ".png" or not source.is_file():
            raise RuntimeError(f"Missing/unsafe file: {source}")
        if hashlib.sha256(source.read_bytes()).hexdigest() != item["sha256"]:
            raise RuntimeError(f"SHA256 mismatch: {source}")
        name = "T_NARIS_UI_" + item["id"] + "_Reference"
        path = f"{destination}/{name}"
        if unreal.EditorAssetLibrary.does_asset_exist(path):
            report.append({"asset": path, "status": "SKIPPED_ALREADY_EXISTS"})
            continue
        task = unreal.AssetImportTask()
        task.filename = str(source)
        task.destination_path = destination
        task.destination_name = name
        task.automated = True
        task.replace_existing = False
        task.save = False
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        objects = list(task.imported_object_paths)
        if not objects:
            raise RuntimeError(f"Import failed: {source}")
        for obj in objects:
            unreal.EditorAssetLibrary.save_asset(obj, only_if_is_dirty=True)
        report.append({"asset": path, "status": "IMPORTED_REFERENCE_ONLY", "objects": objects})
    (root / "ue_import_report.json").write_text(
        json.dumps({"status": "REFERENCES_ONLY", "functional_widgets_created": 0, "results": report}, indent=2),
        encoding="utf-8")
    return report


if __name__ == "__main__":
    run()
