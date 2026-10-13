"""NARIS W04: import rigged Fiery Demon and place into Ash Gate Unreal map.

Run in Unreal Editor with Python Editor Script Plugin. Asset preparation:
 Blender: blender -b -P blender_export_demon.py -- <rigged.glb> <rigged.fbx>

Example:
 UnrealEditor-Cmd.exe <NARIS_W04.uproject> -ExecutePythonScript="<script_absolute_path>"
 Environment variables:
   NARIS_DEMON_FBX=<absolute_path_to_fbx>
   NARIS_ASH_GATE_UMAP=/Game/NARIS/Maps/L_AshGate [existing level, optional]
   NARIS_ALLOW_MAP_EDIT=1 [required to modify existing production level]
   NARIS_REPORT_JSON=<absolute_path_to_json>
 WARNING: never run on shipping level without taking a source-control snapshot.
"""
import json
import os
import traceback
from pathlib import Path
import unreal

DEST = "/Game/NARIS/Enemies/FieryDemon"
QA_LEVEL = "/Game/NARIS/W04/Maps/L_FieryDemon_QA"

def fail(message):
    unreal.log_error("[NARIS_DEMON] " + str(message))
    raise RuntimeError(message)

def import_demon(path):
    fbx = Path(path)
    if not fbx.is_file():
        fail("No skeletal FBX found: " + str(fbx))
    options = unreal.FbxImportUI()
    options.import_mesh = True
    options.import_as_skeletal = True
    options.import_animations = True
    options.import_materials = True
    options.import_textures = True
    options.mesh_type_to_import = unreal.FBXImportType.FBXIT_SKELETAL_MESH
    task = unreal.AssetImportTask()
    task.filename = str(fbx)
    task.destination_path = DEST
    task.automated = True
    task.save = True
    task.replace_existing = False
    task.options = options
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    assets = [unreal.load_asset(p) for p in task.imported_object_paths]
    skeletal = [x for x in assets if isinstance(x, unreal.SkeletalMesh)]
    animations = [x for x in assets if isinstance(x, unreal.AnimSequence)]
    if not skeletal:
        fail("Import did not produce SkeletalMesh; no map edited")
    unreal.EditorAssetLibrary.save_directory(DEST, only_if_is_dirty=True, recursive=True)
    return skeletal[0], animations, task.imported_object_paths

def open_or_create_level(level):
    if unreal.EditorAssetLibrary.does_asset_exist(level):
        if not unreal.EditorLoadingAndSavingUtils.load_map(level):
            fail("Could not load existing level: " + level)
    else:
        if level != QA_LEVEL:
            fail("Production level must already exist: " + level)
        if not unreal.EditorLevelLibrary.new_level(level):
            fail("Unable to create QA level")

def place_boss(mesh, animation, level):
    open_or_create_level(level)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    existing = [a for a in actors.get_all_level_actors() if a.get_actor_label() == "NARIS_FieryDemon_EliteBoss"]
    if existing:
        actor = existing[0]
    else:
        actor = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, unreal.Vector(1400, 0, 120), unreal.Rotator(0, 180, 0))
    actor.set_actor_label("NARIS_FieryDemon_EliteBoss")
    component = actor.get_editor_property("skeletal_mesh_component")
    if hasattr(component, "set_skeletal_mesh_asset"):
        component.set_skeletal_mesh_asset(mesh)
    else:
        component.set_editor_property("skeletal_mesh", mesh)
    if animation:
        component.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        component.set_animation(animation)
    unreal.EditorLevelLibrary.save_current_level()
    return actor.get_path_name()

def main():
    fbx = os.environ.get("NARIS_DEMON_FBX", "")
    if not fbx:
        fail("Set NARIS_DEMON_FBX to actual exported skeletal FBX")
    production_level = os.environ.get("NARIS_ASH_GATE_UMAP", "").strip()
    allow_prod = os.environ.get("NARIS_ALLOW_MAP_EDIT", "") == "1"
    level = QA_LEVEL
    if production_level:
        if not allow_prod:
            fail("Refusing to edit production map without NARIS_ALLOW_MAP_EDIT=1")
        level = production_level
    mesh, animations, imported = import_demon(fbx)
    idle = next((a for a in animations if "idle" in a.get_name().lower()), animations[0] if animations else None)
    actor_path = place_boss(mesh, idle, level)
    report = {
        "status":"mesh_placed_in_unreal_level",
        "level":level,"mesh":mesh.get_path_name(),
        "actor":actor_path,"imported_assets":imported,
        "animations_imported":len(animations),
        "animation_preview":idle.get_name() if idle else None,
        "boss_ai_active":False,"combat_validated":False,
        "pie_tested":False,"shipping_approved":False
    }
    target = os.environ.get("NARIS_REPORT_JSON", "")
    if target:
        Path(target).write_text(json.dumps(report,indent=2),encoding="utf-8")
    unreal.log("[NARIS_DEMON] " + json.dumps(report))
    return report

if __name__ == "__main__":
    try: main()
    except Exception:
        unreal.log_error(traceback.format_exc())
        raise
