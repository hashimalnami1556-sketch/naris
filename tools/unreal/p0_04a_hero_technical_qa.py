# CALL OF NARIS — P0-04A Hero Technical QA
# Unreal Editor Python. This is NOT visual acceptance.
import unreal, json
from pathlib import Path

PROJECT_ROOT=Path(r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57")
P003=PROJECT_ROOT/"Reports"/"P0-03_unreal_hero_import.json"
REPORT=PROJECT_ROOT/"Reports"/"P0-04A_hero_technical_qa.json"
CANDIDATE="/Game/NARIS/Characters/HeroProduction/SK_NARIS_AshenVessel_Production"
BASELINES=[
    "/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3",
    "/Game/NARIS/Characters/Hero/SK_NARIS_Hero_v1",
]

def fail(reason,extra=None):
    out={"status":"FAIL","visual_acceptance":False,"reason":reason}
    if extra: out.update(extra)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    unreal.log_error("NARIS_P0_04A_FAIL "+json.dumps(out,ensure_ascii=False))
    raise RuntimeError(reason)

if not P003.is_file():
    fail("missing_p0_03_report")
p3=json.loads(P003.read_text(encoding="utf-8"))
if p3.get("status")!="PASS":
    fail("p0_03_not_passed",{"p0_03":p3})

hero=unreal.load_asset(CANDIDATE)
if not hero or not isinstance(hero,unreal.SkeletalMesh):
    fail("candidate_skeletal_mesh_missing",{"candidate":CANDIDATE})

def safe_prop(obj,name,default=None):
    try: return obj.get_editor_property(name)
    except Exception: return default

skeleton=safe_prop(hero,"skeleton")
mats=[]
for slot in safe_prop(hero,"materials",[]) or []:
    try:
        mi=slot.get_editor_property("material_interface")
        mats.append(mi.get_path_name() if mi else None)
    except Exception:
        mats.append(None)

# Bounds differ slightly by engine API, so record what is available without
# turning Python wrapper variation into a false failure.
bounds={}
for prop in ("imported_bounds","positive_bounds_extension","negative_bounds_extension"):
    value=safe_prop(hero,prop)
    if value is not None:
        bounds[prop]=str(value)

lod_count=None
try:
    subsystem=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    if subsystem:
        # API differs across minor releases; probe supported methods.
        for method in ("get_lod_count","get_num_lods"):
            if hasattr(subsystem,method):
                lod_count=int(getattr(subsystem,method)(hero))
                break
except Exception as exc:
    unreal.log_warning("NARIS_P0_04A_LOD_PROBE "+str(exc))

baseline=None
for path in BASELINES:
    obj=unreal.load_asset(path)
    if obj and isinstance(obj,unreal.SkeletalMesh):
        baseline=obj
        break

comparison={}
if baseline:
    bmats=safe_prop(baseline,"materials",[]) or []
    comparison={
        "baseline":baseline.get_path_name(),
        "candidate_material_slots":len(mats),
        "baseline_material_slots":len(bmats),
        "same_skeleton_object":safe_prop(baseline,"skeleton")==skeleton,
    }

compatible_animation_assets=[]
animation_candidates=[
    "/Game/NARIS/Characters/HeroV3",
    "/Game/NARIS/W04/Characters/Hero/Animations",
]
for folder in animation_candidates:
    if not unreal.EditorAssetLibrary.does_directory_exist(folder):
        continue
    for asset_path in unreal.EditorAssetLibrary.list_assets(folder,recursive=True,include_folder=False):
        obj=unreal.load_asset(asset_path)
        if not isinstance(obj,(unreal.AnimSequence,unreal.AnimMontage)):
            continue
        try:
            anim_skeleton=obj.get_editor_property("skeleton")
        except Exception:
            anim_skeleton=None
        if anim_skeleton==skeleton:
            compatible_animation_assets.append(obj.get_path_name())

physics_asset=safe_prop(hero,"physics_asset")
same_skeleton=True
if baseline:
    same_skeleton=(safe_prop(baseline,"skeleton")==skeleton)

# Production registry requires >=3 LODs. Python API differs by UE minor release;
# fail closed if we can query it and it is insufficient, otherwise report unresolved.
lod_gate=(lod_count is not None and lod_count>=3)

non_null_materials=[x for x in mats if x]
baseline_present=baseline is not None
animation_compatible_or_retargeted=(
    baseline_present
    and (same_skeleton or len(compatible_animation_assets)>=2)
)

checks={
    "candidate_is_skeletal_mesh":isinstance(hero,unreal.SkeletalMesh),
    "has_skeleton":skeleton is not None,
    "baseline_present":baseline_present,
    "same_skeleton_as_working_hero":same_skeleton,
    "physics_asset":physics_asset is not None,
    "material_slots_non_null":len(non_null_materials)>=1,
    "lod_count_at_least_3":lod_gate,
    "compatible_animation_assets":len(compatible_animation_assets)>=2,
    "animation_compatible_or_retargeted":animation_compatible_or_retargeted,
    "p0_03_candidate_only":bool(p3.get("candidate_only")),
}
passed=all(checks.values())

try:
    unreal.EditorAssetLibrary.set_metadata_tag(hero,unreal.Name("NARIS.ProductionGate"),"P0-04A")
    unreal.EditorAssetLibrary.set_metadata_tag(hero,unreal.Name("NARIS.TechnicalQAPass"),"true" if passed else "false")
    unreal.EditorAssetLibrary.set_metadata_tag(hero,unreal.Name("NARIS.VisualAcceptance"),"pending")
    unreal.EditorAssetLibrary.save_loaded_asset(hero)
except Exception as exc:
    unreal.log_warning("NARIS_P0_04A_METADATA_WARNING "+str(exc))

result={
    "status":"PASS" if passed else "FAIL_GATE",
    "technical_acceptance":passed,
    "visual_acceptance":False,
    "runtime_combat_acceptance":False,
    "candidate":hero.get_path_name(),
    "skeleton":skeleton.get_path_name() if skeleton else None,
    "materials":mats,
    "material_policy":"at least one real assigned material; do not fabricate unused style slots",
    "lod_count":lod_count,
    "physics_asset":physics_asset.get_path_name() if physics_asset else None,
    "compatible_animation_count":len(compatible_animation_assets),
    "compatible_animation_assets":compatible_animation_assets,
    "bounds_if_available":bounds,
    "comparison":comparison,
    "checks":checks,
    "next_gate":"P0-04B D3D12 visual + deformation + weapon socket + combat regression on AsusRog",
    "replacement_allowed":False
}
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
unreal.log("NARIS_P0_04A_RESULT="+json.dumps(result,ensure_ascii=False))
if not passed:
    raise RuntimeError("P0-04A technical gate failed")
