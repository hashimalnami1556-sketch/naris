"""Import real rigged FBX villain prototypes and bind to W04 development actors.

Run from Unreal 5.7 Editor with NARIS_VILLAIN_FBX_DIR set to an existing folder.
Does NOT fabricate/approve finished assets or replace Bone Beast.
Expected SK_<VillainId>.fbx inputs from Blender conversion.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import unreal

MAP = "/Game/NARIS/W04/Maps/W04_AshenForest_Blockout"
DEST_ROOT = "/Game/NARIS/W04/Characters/Villains"


def asset_import_task(path, destination):
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", str(path))
    task.set_editor_property("destination_path", destination)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", True)
    task.set_editor_property("replace_existing", False)
    options = unreal.FbxImportUI()
    options.set_editor_property("import_mesh", True)
    options.set_editor_property("import_as_skeletal", True)
    options.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    options.set_editor_property("import_animations", True)
    options.set_editor_property("create_physics_asset", True)
    options.set_editor_property("import_materials", False)
    options.set_editor_property("import_textures", False)
    task.set_editor_property("options", options)
    return task


def main():
    root = os.environ.get("NARIS_VILLAIN_FBX_DIR", "")
    folder = Path(root).expanduser().resolve() if root else None
    if not folder or not folder.is_dir():
        raise RuntimeError("NARIS_VILLAIN_FBX_DIR must point to converted FBX directory")
    roster_file = (Path(unreal.Paths.project_content_dir()) / "NARIS/W04/Data/W04_VillainEncounterRoster.json")
    roster = json.loads(roster_file.read_text(encoding="utf-8"))
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    tools = unreal.AssetToolsHelpers.get_asset_tools()
    if not unreal.EditorAssetLibrary.does_asset_exist(MAP):
        raise RuntimeError("Development blockout map is missing. Run authoring first.")
    if not levels.load_level(MAP):
        raise RuntimeError("Unable to load development blockout map")
    all_actors = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
    result = {"map": MAP, "stage": "DEVELOPMENT_ONLY", "imported": {}, "blocked": {}}
    cache = {}
    for item in roster["encounters"]:
        key = item["villain_id"]
        if key not in cache:
            source = folder / ("SK_" + key + ".fbx")
            if not source.is_file():
                result["blocked"][key] = "FBX source missing"
                continue
            path = DEST_ROOT + "/" + key
            unreal.EditorAssetLibrary.make_directory(path)
            task = asset_import_task(source, path)
            tools.import_asset_tasks([task])
            imported_paths = list(task.get_editor_property("imported_object_paths") or [])
            meshes = [unreal.load_asset(p) for p in imported_paths]
            meshes = [m for m in meshes if isinstance(m, unreal.SkeletalMesh)]
            if not meshes:
                result["blocked"][key] = "Importer returned no SkeletalMesh; inspect FBX/Unreal log"
                continue
            cache[key] = meshes[0]
            result["imported"][key] = {"asset_path": meshes[0].get_path_name(),
                                        "imported_paths": imported_paths}
        actor = all_actors.get(item["label"])
        if actor is None:
            result["blocked"][item["label"]] = "Enemy actor not found: run naris_author_w04_villains.py"
            continue
        if key in cache:
            actor.set_editor_property("visual_mesh", cache[key])
    if not levels.save_current_level():
        raise RuntimeError("Failed to save development map after mesh binding")
    report_path = Path(unreal.Paths.project_saved_dir()) / "TestReports" / "naris_villain_fbx_intake.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    unreal.log("NARIS_VILLAIN_FBX_INTAKE=" + json.dumps(result, ensure_ascii=False, sort_keys=True))
    if result["blocked"]:
        raise RuntimeError(f"Villain intake has {len(result['blocked'])} blockers; inspect {report_path}")


if __name__ == "__main__":
    main()
