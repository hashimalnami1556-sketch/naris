# CALL OF NARIS — P0-03 Unreal Hero Import Candidate Gate
# Run with UnrealEditor-Cmd.exe NARIS.uproject -ExecutePythonScript=...
import unreal, json, os
from pathlib import Path

PROJECT_ROOT=Path(r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57")
HERO_DIR=PROJECT_ROOT/"Production"/"Hero"
LOG2=HERO_DIR/"P0-02_rig_pbr_log.json"
REPORT=PROJECT_ROOT/"Reports"/"P0-03_unreal_hero_import.json"
DEST="/Game/NARIS/Characters/HeroProduction"
NAME="SK_NARIS_AshenVessel_Production"
BASELINE_HERO_PATHS=[
    "/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3",
    "/Game/NARIS/W04/Characters/Hero/SK_AshenVessel",
    "/Game/NARIS/Characters/Hero/SK_NARIS_Hero_v1",
]

def fail(reason, extra=None):
    result={"status":"FAIL","reason":reason}
    if extra: result.update(extra)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    unreal.log_error("NARIS_P0_03_FAIL "+json.dumps(result,ensure_ascii=False))
    raise RuntimeError(reason)

if not LOG2.is_file():
    fail("missing_p0_02_log",{"path":str(LOG2)})

p2=json.loads(LOG2.read_text(encoding="utf-8"))
p0_02_ready=bool(p2.get("production_grade") or p2.get("import_candidate_ready"))
if not p0_02_ready:
    fail("p0_02_not_import_ready",{"p0_02_status":p2.get("status")})

source_candidates=[
    p2.get("output_fbx"),
    p2.get("output_glb"),
    str(HERO_DIR/"SK_AshenVessel_PBR.fbx"),
    str(HERO_DIR/"SK_AshenVessel_Production.glb"),
]
source=None
for raw in source_candidates:
    if not raw:
        continue
    candidate=Path(raw)
    if candidate.is_file():
        source=candidate
        break
if source is None:
    fail("missing_p0_02_source",{"candidates":[str(x) for x in source_candidates if x]})
source_format=source.suffix.lower()
if source_format not in (".fbx",".glb",".gltf"):
    fail("unsupported_p0_02_source_format",{"path":str(source),"format":source_format})

# Keep candidate import isolated from the current working HeroV3.
unreal.EditorAssetLibrary.make_directory(DEST)

task=unreal.AssetImportTask()
task.set_editor_property("filename",str(source))
task.set_editor_property("destination_path",DEST)
task.set_editor_property("destination_name",NAME)
task.set_editor_property("automated",True)
task.set_editor_property("replace_existing",True)
task.set_editor_property("replace_existing_settings",True)
task.set_editor_property("save",True)

baseline_hero=None
baseline_skeleton=None
for candidate_path in BASELINE_HERO_PATHS:
    candidate=unreal.load_asset(candidate_path)
    if candidate and isinstance(candidate,unreal.SkeletalMesh):
        baseline_hero=candidate
        try:
            baseline_skeleton=candidate.get_editor_property("skeleton")
        except Exception:
            baseline_skeleton=None
        if baseline_skeleton:
            break

if source_format==".fbx":
    ui=unreal.FbxImportUI()
    ui.set_editor_property("import_mesh",True)
    ui.set_editor_property("import_as_skeletal",True)
    ui.set_editor_property("import_animations",False)
    ui.set_editor_property("import_materials",True)
    ui.set_editor_property("import_textures",False)
    ui.set_editor_property("mesh_type_to_import",unreal.FBXImportType.FBXIT_SKELETAL_MESH)
    if baseline_skeleton:
        ui.set_editor_property("skeleton",baseline_skeleton)
    try:
        ui.set_editor_property("create_physics_asset",True)
    except Exception:
        pass

    # Preserve normals/tangents generated in Blender where possible.
    try:
        sk=ui.get_editor_property("skeletal_mesh_import_data")
        sk.set_editor_property("import_mesh_lo_ds",False)
        sk.set_editor_property("update_skeleton_reference_pose",False)
        sk.set_editor_property("use_t0_as_ref_pose",False)
        sk.set_editor_property("preserve_smoothing_groups",True)
    except Exception as exc:
        unreal.log_warning("NARIS_P0_03_IMPORT_DATA_WARNING "+str(exc))
    task.set_editor_property("options",ui)
else:
    # UE5.7 Interchange handles glTF/GLB. Keep it candidate-only and validate
    # the resulting SkeletalMesh/Skeleton below instead of forcing FBX settings.
    unreal.log("NARIS_P0_03_INTERCHANGE_SOURCE "+str(source))
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

objects=list(task.get_objects())
if not objects:
    fail("unreal_import_produced_no_objects")

skeletal=[o for o in objects if isinstance(o,unreal.SkeletalMesh)]
skeletons=[o for o in objects if isinstance(o,unreal.Skeleton)]
materials=[o for o in objects if isinstance(o,unreal.MaterialInterface)]

if not skeletal:
    # Some importer versions return only the primary asset from get_objects;
    # inspect destination for generated assets as a fallback.
    assets=unreal.EditorAssetLibrary.list_assets(DEST,recursive=True,include_folder=False)
    for path in assets:
        obj=unreal.load_asset(path)
        if isinstance(obj,unreal.SkeletalMesh) and obj not in skeletal: skeletal.append(obj)
        elif isinstance(obj,unreal.Skeleton) and obj not in skeletons: skeletons.append(obj)
        elif isinstance(obj,unreal.MaterialInterface) and obj not in materials: materials.append(obj)

if len(skeletal)!=1:
    fail("skeletal_mesh_count_not_one",{
        "skeletal_meshes":[o.get_path_name() for o in skeletal],
        "imported_objects":[o.get_path_name() for o in objects]
    })

hero=skeletal[0]
hero_skeleton=None
try:
    hero_skeleton=hero.get_editor_property("skeleton")
except Exception:
    pass
if hero_skeleton and hero_skeleton not in skeletons:
    skeletons.append(hero_skeleton)

# Generic runtime-safe checks available to Python without assuming internal reference skeleton APIs.
physics_asset=None
try:
    physics_asset=hero.get_editor_property("physics_asset")
except Exception:
    pass

same_skeleton=(baseline_skeleton is None) or (hero_skeleton==baseline_skeleton)

lod_count=None
lod_regenerated=False
try:
    skel_editor=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    if skel_editor:
        lod_count=int(skel_editor.get_lod_count(hero))
        if lod_count < 3:
            lod_regenerated=bool(skel_editor.regenerate_lod(hero,3,False,False))
            unreal.EditorAssetLibrary.save_loaded_asset(hero)
            lod_count=int(skel_editor.get_lod_count(hero))
except Exception as exc:
    unreal.log_warning("NARIS_P0_03_LOD_WARNING "+str(exc))

material_slots=[]
try:
    for smat in hero.get_editor_property("materials"):
        mat=smat.get_editor_property("material_interface")
        material_slots.append(mat.get_path_name() if mat else None)
except Exception as exc:
    unreal.log_warning("NARIS_P0_03_MATERIAL_READ_WARNING "+str(exc))

checks={
    "skeletal_mesh":hero is not None,
    "skeleton":hero_skeleton is not None or len(skeletons)>0,
    "source_file":source.is_file(),
    "p0_02_gate":p0_02_ready,
    "material_slots_non_null":sum(1 for x in material_slots if x)>=1,
}
diagnostics={
    "baseline_skeleton_reused":same_skeleton,
    "physics_asset":physics_asset is not None,
    "lod_count_at_least_3":lod_count is not None and lod_count>=3,
}

# P0-03 is an import gate, not the final retarget/LOD/physics gate.
# P0-04A evaluates those diagnostics before any promotion.
passed=all(checks.values())

for obj in [hero]+skeletons+materials:
    if not obj: continue
    try:
        unreal.EditorAssetLibrary.set_metadata_tag(obj,unreal.Name("NARIS.ProductionGate"),"P0-03")
        unreal.EditorAssetLibrary.set_metadata_tag(obj,unreal.Name("NARIS.SourceAsset"),str(source))
        unreal.EditorAssetLibrary.set_metadata_tag(obj,unreal.Name("NARIS.P0_01Status"),str(p2.get("source","")))
        unreal.EditorAssetLibrary.set_metadata_tag(obj,unreal.Name("NARIS.CandidateOnly"),"true")
        unreal.EditorAssetLibrary.save_loaded_asset(obj)
    except Exception as exc:
        unreal.log_warning("NARIS_P0_03_METADATA_WARNING "+str(exc))

unreal.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=False,recursive=True)

result={
    "status":"PASS" if passed else "FAIL_GATE",
    "candidate_only":True,
    "source_asset":str(source),
    "source_format":source_format,
    "destination":DEST,
    "skeletal_mesh":hero.get_path_name(),
    "skeletons":[o.get_path_name() for o in skeletons if o],
    "materials":material_slots,
    "baseline_hero":baseline_hero.get_path_name() if baseline_hero else None,
    "baseline_skeleton":baseline_skeleton.get_path_name() if baseline_skeleton else None,
    "physics_asset":physics_asset.get_path_name() if physics_asset else None,
    "lod_count":lod_count,
    "lod_regenerated":lod_regenerated,
    "checks":checks,
    "diagnostics":diagnostics,
    "next_gate":"P0-04A technical LOD/skeleton/material QA, then P0-04B D3D12 visual/combat QA before swapping HeroV3"
}
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
unreal.log("NARIS_P0_03_RESULT="+json.dumps(result,ensure_ascii=False))
if not passed:
    raise RuntimeError("P0-03 import gate failed")
