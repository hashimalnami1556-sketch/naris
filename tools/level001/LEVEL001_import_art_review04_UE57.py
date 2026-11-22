"""LEVEL-001 V4 isolated Unreal 5.7 import. ONLY execute after machine gate.
Makes review04 copy, no production map changes, no network/shipping claims.
"""
import hashlib,json,os,shutil
from pathlib import Path
import unreal
ROOT=Path(unreal.Paths.project_dir()).resolve()
if ROOT!=Path(r"C:\Users\Admin\NARIS").resolve():raise RuntimeError("LEVEL001_WRONG_PROJECT")
if not unreal.SystemLibrary.get_engine_version().startswith("5.7"):
    raise RuntimeError("LEVEL001_WRONG_ENGINE_NOT_57")
BASE=ROOT/"Saved/GIS/Jeddah/LEVEL001_AlBalad_Footprints_Review04"
SOURCE=BASE/"JED_AlBalad_ArchitecturalDetails_V4.glb"
MAN=BASE/"JED_AlBalad_ArchitecturalDetails_V4_manifest.json"
OLD_MAP="/Game/NARIS_GIS/Jeddah/Maps/L_Jeddah_AlBalad_Footprints_Review03"
NEW_MAP="/Game/NARIS_GIS/Jeddah/Maps/L_Jeddah_AlBalad_ArtReview04"
DEST="/Game/NARIS_GIS/Jeddah/Review/ArchitecturalDetailsV4"
OLD_FILE=ROOT/"Content/NARIS_GIS/Jeddah/Maps/L_Jeddah_AlBalad_Footprints_Review03.umap"
SOURCE_V2=ROOT/"Content/NARIS_GIS/Jeddah/Maps/L_Jeddah_GIS_V2.umap"
REPORT=BASE/"LEVEL001_V4_Unreal_Import_Report.json"
BACKUP=BASE/"L_Jeddah_AlBalad_Review03_before_V4_import.umap"
if not SOURCE.is_file() or not MAN.is_file() or not OLD_FILE.is_file() or not SOURCE_V2.is_file():
    raise RuntimeError("LEVEL001_REQUIRED_INPUT_MISSING")
if REPORT.exists() or BACKUP.exists():raise RuntimeError("LEVEL001_ALREADY_ATTEMPTED_NO_OVERWRITE")
if os.environ.get("NARIS_LEVEL001_REVIEW_IMPORT_APPROVE")!="1":
    raise RuntimeError("LEVEL001_MANUAL_REVIEW_APPROVAL_FLAG_MISSING")
if shutil.disk_usage(ROOT).free < 30*(1024**3):
    raise RuntimeError("LEVEL001_C_DRIVE_FREE_BELOW_30_GIB")
meta=json.loads(MAN.read_text(encoding="utf-8"))
if hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=meta["glb_sha256"]:
    raise RuntimeError("LEVEL001_SOURCE_HASH_MISMATCH")
if not(meta["decorated_buildings"]>=150 and meta["window_modules"]>=900
       and meta["detail_triangles"]<=250000 and meta["max_outward_projection_m"]<=0.35
       and meta["production_approved"] is False):
    raise RuntimeError("LEVEL001_V4_INVALID_ART_REVIEW_MANIFEST")
if unreal.EditorAssetLibrary.does_asset_exist(NEW_MAP):
    raise RuntimeError("LEVEL001_REVIEW04_MAP_EXISTS_NO_OVERWRITE")
if unreal.EditorAssetLibrary.does_directory_exist(DEST):
    raise RuntimeError("LEVEL001_REVIEW04_DEST_EXISTS_NO_OVERWRITE")
before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (OLD_FILE,SOURCE_V2)}
shutil.copy2(OLD_FILE,BACKUP)
asset_sub=unreal.get_editor_subsystem(unreal.EditorAssetSubsystem)
world=asset_sub.duplicate_asset(OLD_MAP,NEW_MAP)
if not world or not unreal.EditorAssetLibrary.does_asset_exist(NEW_MAP):
    raise RuntimeError("LEVEL001_REVIEW04_DUPLICATE_MAP_FAILED")
editor=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not editor.load_level(NEW_MAP):raise RuntimeError("LEVEL001_REVIEW04_LOAD_FAILED")
actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
anchors=[a for a in actor_sub.get_all_level_actors()
         if a.get_actor_label()=="JED_GIS_V3_OSM_Building_Walls"]
if len(anchors)!=1:raise RuntimeError("LEVEL001_BASE_ANCHOR_NOT_FOUND_ON_REVIEW_COPY")
base=anchors[0]
task=unreal.AssetImportTask()
for prop,val in {
    "filename":str(SOURCE),"destination_path":DEST,"automated":True,
    "replace_existing":False,"replace_existing_settings":False,
    "save":True,"async_":False
}.items():task.set_editor_property(prop,val)
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
items=list(task.get_objects())
if not items:
    items=[unreal.EditorAssetLibrary.load_asset(p)
           for p in unreal.EditorAssetLibrary.list_assets(DEST,True,False)]
meshes=[i for i in items if isinstance(i,unreal.StaticMesh)]
if len(meshes)!=3:raise RuntimeError("LEVEL001_V4_EXPECTED_THREE_STATIC_MESHES")
spawned=[]
for mesh in meshes:
    actor=actor_sub.spawn_actor_from_object(mesh,base.get_actor_location(),base.get_actor_rotation())
    if not actor:raise RuntimeError("LEVEL001_SPAWN_FAILED_"+mesh.get_name())
    actor.set_actor_scale3d(base.get_actor_scale3d())
    actor.set_actor_label("LEVEL001_V4_ART_REVIEW_"+mesh.get_name())
    spawned.append(actor.get_actor_label())
saved=bool(editor.save_current_level())
after={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (OLD_FILE,SOURCE_V2)}
if before!=after:raise RuntimeError("LEVEL001_CANONICAL_OR_REVIEW03_MODIFIED")
report={
 "schema":"naris.level001.review04.unreal_import",
 "map":NEW_MAP,"saved":saved,"art_meshes":len(meshes),
 "spawned_labels":spawned,"source_sha256":meta["glb_sha256"],
 "gis_v2_and_review03_unchanged":True,
 "source_photomatch_verified":False,"collision_tested":False,
 "navigation_tested":False,"multiplayer_tested":False,
 "performance_measured":False,"production_approved":False,
 "rollback_backup":str(BACKUP),
 "note":"Isolated review map only; collision, streaming, high-resolution Lit QA, and build/cook required."}
REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
unreal.log("LEVEL001_REVIEW04_IMPORT="+json.dumps(report))
if not saved:raise RuntimeError("LEVEL001_REVIEW04_SAVE_FAILED")
