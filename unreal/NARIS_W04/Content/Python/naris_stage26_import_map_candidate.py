"""Import the Stage26 Ashen Forest GLB into Unreal quarantine only.
Run with Unreal Editor Python plugin on W04 UE5.7; never overwrites production maps.
"""
from pathlib import Path
import json
import unreal

project = Path(unreal.Paths.project_dir()).resolve()
source = project / "NARIS_Stage26_External" / "NARIS_W04_AshenForest_Candidate.glb"
report_path = Path(unreal.Paths.project_saved_dir()) / "TestReports" / "naris_stage26_candidate_import.json"
report_path.parent.mkdir(parents=True, exist_ok=True)
report = {"schema": "naris.w04.stage26.import.v1", "status": "fail",
          "input": str(source), "destination": "/Game/NARIS/_Import/Stage26_W04",
          "assets": [], "errors": []}
try:
    if not source.is_file():
        raise FileNotFoundError("Copy candidate GLB into " + str(source))
    task = unreal.AssetImportTask()
    task.filename = str(source)
    task.destination_path = report["destination"]
    task.automated = True
    task.replace_existing = False
    task.save = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    report["assets"] = [str(p) for p in task.imported_object_paths]
    if not report["assets"]:
        raise RuntimeError("No imported assets; verify Interchange glTF import support")
    report["status"] = "imported_quarantine_unverified"
except Exception as exc:
    report["errors"].append(str(exc))
finally:
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    unreal.log("NARIS_STAGE26_IMPORT=" + json.dumps(report))
if report["errors"]:
    raise RuntimeError(report["errors"][0])
