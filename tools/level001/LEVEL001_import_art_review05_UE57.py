"""LEVEL-001 V5 — fail-closed UE5.7 editor importer for isolated Review05 level.
Import V4 architectural details + V5 projected rawashin over preserved GIS V3.
Never imports to canonical GIS V2, production, or Review03 and never auto-approves.
"""
import os,json,hashlib,shutil
from pathlib import Path
import unreal

ROOT=Path(unreal.Paths.project_dir()).resolve()
EXPECTED=Path(r"C:\Users\Admin\NARIS").resolve()
if ROOT!=EXPECTED:raise RuntimeError("LEVEL001_INCORRECT_PROJECT")
if not unreal.SystemLibrary.get_engine_version().startswith("5.7"):
    raise RuntimeError("LEVEL001_ENGINE_NOT_5_7")
if os.environ.get("NARIS_LEVEL001_REVIEW_IMPORT_APPROVE")!="1":
    raise RuntimeError("LEVEL001_REQUIRE_EXPLICIT_REVIEW_APPROVAL")
FREE=shutil.disk_usage(ROOT).free
if FREE < 30*(1024**3):
    raise RuntimeError("LEVEL001_DISK_RESOURCE_GATE_FAILED")
BASE=ROOT/"Saved/GIS/Jeddah"
V4=BASE/"LEVEL001_AlBalad_Footprints_Review04"
V5=BASE/"LEVEL001_AlBalad_Footprints_Review05"
OLD_MAP="/Game/NARIS_GIS/Jeddah/Maps/L_Jeddah_AlBalad_Footprints_Review03"
NEW_MAP="/Game/NARIS_GIS/Jeddah/Maps/L_Jeddah_AlBalad_ArtReview05"
DESTS=(
 (V4/"JED_AlBalad_ArchitecturalDetails_V4.glb",
  V4/"JED_AlBalad_ArchitecturalDetails_V4_manifest.json",
  "/Game/NARIS_GIS/Jeddah/Review/ArchitectureV4"),
 (V5/"JED_AlBalad_ProjectedRawashin_V5.glb",
  V5/"JED_AlBalad_ProjectedRawashin_V5_manifest.json",
  "/Game/NARIS_GIS/Jeddah/Review/ProjectedRawashinV5")
)
ORIGINALS=[
 ROOT/"Content/NARIS_GIS/Jeddah/Maps/L_Jeddah_GIS_V2.umap",
 ROOT/"Content/NARIS_GIS/Jeddah/Maps/L_Jeddah_AlBalad_Footprints_Review03.umap"
]
REPORT=V5/"LEVEL001_V5_Unreal_Import_Report.json"
BACKUP=V5/"L_Jeddah_Review03_before_V5_duplicate.umap"
if REPORT.exists() or BACKUP.exists():
    raise RuntimeError("LEVEL001_IMPORT_ALREADY_ATTEMPTED")
if not all(p.is_file() for p in ORIGINALS):
    raise RuntimeError("LEVEL001_ORIGINAL_MAPS_MISSING")
for glb,manifest,dest in DESTS:
    if not glb.is_file() or not manifest.is_file():
        raise RuntimeError("LEVEL001_REVIEW_SOURCE_MISSING")
    data=json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("glb_sha256")!=hashlib.sha256(glb.read_bytes()).hexdigest():
        raise RuntimeError("LEVEL001_REVIEW_SOURCE_HASH_MISMATCH")
    if data.get("production_approved") is not False:
        raise RuntimeError("LEVEL001_UNEXPECTED_APPROVAL_IN_SOURCE")
    if unreal.EditorAssetLibrary.does_directory_exist(dest):
        raise RuntimeError("LEVEL001_ASSET_DEST_ALREADY_EXISTS")
if unreal.EditorAssetLibrary.does_asset_exist(NEW_MAP):
    raise RuntimeError("LEVEL001_MAP_DEST_ALREADY_EXISTS")
asset=unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
editor=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in ORIGINALS}
shutil.copy2(ORIGINALS[1],BACKUP)
created=asset.duplicate_asset(OLD_MAP,NEW_MAP)
if not created or not unreal.EditorAssetLibrary.does_asset_exist(NEW_MAP):
    raise RuntimeError("LEVEL001_DUPLICATE_REVIEW_LEVEL_FAILED")
if not editor.load_level(NEW_MAP):
    raise RuntimeError("LEVEL001_REVIEW05_LEVEL_LOAD_FAILED")
base=[a for a in actors.get_all_level_actors() if a.get_actor_label()=="JED_GIS_V3_OSM_Building_Walls"]
if len(base)!=1:
    raise RuntimeError("LEVEL001_EXPECTED_BASE_MESH_ANCHOR")
b=base[0]
spawned=[]
for glb,manifest,dest in DESTS:
    task=unreal.AssetImportTask()
    for key,val in {
      "filename":str(glb),"destination_path":dest,"automated":True,
      "replace_existing":False,"replace_existing_settings":False,
      "save":True,"async_":False
    }.items():task.set_editor_property(key,val)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported=list(task.get_objects())
    if not imported:
        imported=[unreal.EditorAssetLibrary.load_asset(p)
                  for p in unreal.EditorAssetLibrary.list_assets(dest,True,False)]
    meshes=[i for i in imported if isinstance(i,unreal.StaticMesh)]
    if len(meshes)!=3:
        raise RuntimeError("LEVEL001_EXPECTED_THREE_MESHES_EACH_LAYER")
    for mesh in meshes:
        obj=actors.spawn_actor_from_object(mesh,b.get_actor_location(),b.get_actor_rotation())
        if not obj:raise RuntimeError("LEVEL001_FAILED_TO_SPAWN_"+mesh.get_name())
        obj.set_actor_scale3d(b.get_actor_scale3d())
        obj.set_actor_label("LEVEL001_ART_REVIEW05_"+mesh.get_name())
        spawned.append(obj.get_actor_label())
if not editor.save_current_level():
    raise RuntimeError("LEVEL001_REVIEW05_SAVE_FAILED")
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in ORIGINALS}
if before!=after:
    raise RuntimeError("LEVEL001_ORIGINAL_MAP_MUTATED_ABORT")
report={
  "schema":"naris.level001.review05.unreal.import",
  "map":NEW_MAP,"imported_mesh_actor_count":len(spawned),
  "actor_labels":spawned,"original_maps_unchanged":True,
  "source_v4_hash":json.loads(DESTS[0][1].read_text())["glb_sha256"],
  "source_v5_hash":json.loads(DESTS[1][1].read_text())["glb_sha256"],
  "manual_visual_qa_completed":False,"collision_tested":False,
  "navmesh_tested":False,"multiplayer_tested":False,
  "runtime_lit_screenshot_captured":False,"fps_measured":False,
  "production_approved":False,"rollback_backup":str(BACKUP)
}
REPORT.write_text(json.dumps(report,indent=2),encoding="utf-8")
unreal.log("LEVEL001_REVIEW05_IMPORT="+json.dumps(report))
