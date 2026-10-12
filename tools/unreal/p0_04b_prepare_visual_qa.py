# CALL OF NARIS — P0-04B Visual QA Scene Preparation
# Unreal Editor Python. Produces a side-by-side QA level; does not promote candidate.
import unreal, json
from pathlib import Path

PROJECT_ROOT=Path(r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57")
REPORT_A=PROJECT_ROOT/"Reports"/"P0-04A_hero_technical_qa.json"
REPORT_B=PROJECT_ROOT/"Reports"/"P0-04B_visual_scene.json"
QA_MAP="/Game/NARIS/QA/L_HeroCandidate_QA"
CANDIDATE="/Game/NARIS/Characters/HeroProduction/SK_NARIS_AshenVessel_Production"
BASELINES=[
    "/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3",
    "/Game/NARIS/W04/Characters/Hero/SK_AshenVessel",
    "/Game/NARIS/Characters/Hero/SK_NARIS_Hero_v1",
]

def fail(reason,extra=None):
    out={"status":"FAIL","visual_acceptance":False,"replacement_allowed":False,"reason":reason}
    if extra: out.update(extra)
    REPORT_B.parent.mkdir(parents=True,exist_ok=True)
    REPORT_B.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    unreal.log_error("NARIS_P0_04B_FAIL "+json.dumps(out,ensure_ascii=False))
    raise RuntimeError(reason)

if not REPORT_A.is_file():
    fail("missing_p0_04a_report")
p4a=json.loads(REPORT_A.read_text(encoding="utf-8"))
if p4a.get("status")!="PASS" or not p4a.get("technical_acceptance"):
    fail("p0_04a_not_passed",{"p0_04a":p4a})
candidate_source_sha256=str(p4a.get("candidate_source_sha256") or "").lower().strip()
if len(candidate_source_sha256)!=64 or any(c not in "0123456789abcdef" for c in candidate_source_sha256):
    fail("p0_04a_candidate_source_sha256_missing_or_invalid",{"candidate_source_sha256":p4a.get("candidate_source_sha256")})

candidate=unreal.load_asset(CANDIDATE)
if not candidate or not isinstance(candidate,unreal.SkeletalMesh):
    fail("candidate_missing")

baseline=None
for path in BASELINES:
    obj=unreal.load_asset(path)
    if obj and isinstance(obj,unreal.SkeletalMesh):
        baseline=obj
        break
if not baseline:
    fail("baseline_hero_missing")

anim=None
for path in p4a.get("compatible_animation_assets",[]):
    obj=unreal.load_asset(path)
    if isinstance(obj,unreal.AnimSequence):
        anim=obj
        break

# Create/reset dedicated QA map.
level_sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
created=False
try:
    if hasattr(level_sub,"new_level"):
        created=bool(level_sub.new_level(QA_MAP))
    else:
        created=bool(unreal.EditorLevelLibrary.new_level(QA_MAP))
except Exception as exc:
    unreal.log_warning("NARIS_P0_04B_NEW_LEVEL_PRIMARY "+str(exc))
    try:
        created=bool(unreal.EditorLevelLibrary.new_level(QA_MAP))
    except Exception as exc2:
        fail("qa_map_creation_failed",{"error":str(exc2)})

if not created:
    # Some engine builds return False if level already exists; load and clear it.
    try:
        unreal.EditorLoadingAndSavingUtils.load_map(QA_MAP)
        for actor in list(actor_sub.get_all_level_actors()):
            actor_sub.destroy_actor(actor)
    except Exception as exc:
        fail("qa_map_load_failed",{"error":str(exc)})

def set_mesh(actor,mesh):
    comp=actor.get_editor_property("skeletal_mesh_component")
    if hasattr(comp,"set_skeletal_mesh_asset"):
        comp.set_skeletal_mesh_asset(mesh)
    else:
        comp.set_editor_property("skeletal_mesh",mesh)
    return comp

def spawn_skeletal(label,mesh,location):
    actor=actor_sub.spawn_actor_from_class(unreal.SkeletalMeshActor,location,unreal.Rotator(0,0,0))
    actor.set_actor_label(label)
    comp=set_mesh(actor,mesh)
    if anim:
        try:
            comp.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        except Exception:
            pass
        try:
            comp.play_animation(anim,True)
        except Exception as exc:
            unreal.log_warning("NARIS_P0_04B_PLAY_ANIM "+label+" "+str(exc))
    return actor

baseline_actor=spawn_skeletal("QA_BASELINE_HeroV3",baseline,unreal.Vector(0,-115,95))
candidate_actor=spawn_skeletal("QA_CANDIDATE_Production",candidate,unreal.Vector(0,115,95))

# Floor
cube=unreal.load_asset("/Engine/BasicShapes/Cube")
floor=actor_sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-10),unreal.Rotator(0,0,0))
floor.set_actor_label("QA_Floor")
fcomp=floor.get_editor_property("static_mesh_component")
fcomp.set_editor_property("static_mesh",cube)
floor.set_actor_scale3d(unreal.Vector(8,6,.2))

# Key light
sun=actor_sub.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,500),unreal.Rotator(-38,-32,0))
sun.set_actor_label("QA_Key_Warm")
scomp=sun.get_editor_property("directional_light_component")
try:
    scomp.set_editor_property("intensity",4.0)
    scomp.set_editor_property("light_color",unreal.Color(255,181,117,255))
except Exception:
    pass

# Cyan rim
rim=actor_sub.spawn_actor_from_class(unreal.PointLight,unreal.Vector(-120,0,220),unreal.Rotator(0,0,0))
rim.set_actor_label("QA_Rim_Aether")
rcomp=rim.get_editor_property("point_light_component")
try:
    rcomp.set_editor_property("intensity",2600.0)
    rcomp.set_editor_property("attenuation_radius",650.0)
    rcomp.set_editor_property("light_color",unreal.Color(74,216,255,255))
except Exception:
    pass

# Ember fill
fill=actor_sub.spawn_actor_from_class(unreal.PointLight,unreal.Vector(160,-250,140),unreal.Rotator(0,0,0))
fill.set_actor_label("QA_Fill_Ember")
fcl=fill.get_editor_property("point_light_component")
try:
    fcl.set_editor_property("intensity",1800.0)
    fcl.set_editor_property("attenuation_radius",550.0)
    fcl.set_editor_property("light_color",unreal.Color(255,74,28,255))
except Exception:
    pass

# Camera
camera=actor_sub.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(540,0,165),unreal.Rotator(0,0,0))
camera.set_actor_label("QA_Camera_HeroCompare")
look=unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),unreal.Vector(0,0,105))
camera.set_actor_rotation(look,False)
# Force the dedicated comparison camera to own Player 0 at runtime. Without
# this, a -game screenshot can silently come from the default pawn/camera.
try:
    camera.set_editor_property("auto_activate_for_player",unreal.AutoReceiveInput.PLAYER0)
except Exception as exc:
    unreal.log_warning("NARIS_P0_04B_CAMERA_AUTOACTIVATE "+str(exc))
try:
    ccomp=camera.get_editor_property("camera_component")
    ccomp.set_editor_property("field_of_view",46.0)
except Exception:
    pass

# Save dedicated map.
saved=False
try:
    saved=bool(level_sub.save_current_level())
except Exception:
    try:
        saved=bool(unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True))
    except Exception:
        saved=False

result={
    "status":"PASS" if saved else "FAIL_GATE",
    "visual_scene_prepared":saved,
    "visual_acceptance":False,
    "runtime_combat_acceptance":False,
    "replacement_allowed":False,
    "qa_map":QA_MAP,
    "baseline":baseline.get_path_name(),
    "candidate":candidate.get_path_name(),
    "candidate_source_sha256":candidate_source_sha256,
    "preview_animation":anim.get_path_name() if anim else None,
    "camera_actor":"QA_Camera_HeroCompare",
    "screenshot_target":"Saved/Screenshots/Windows/P0-04B_HeroCompare.png",
    "next_gate":"Render D3D12 screenshot, inspect silhouette/material/deformation/scale, then P0-05 promotion + packaged combat regression."
}
REPORT_B.parent.mkdir(parents=True,exist_ok=True)
REPORT_B.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
unreal.log("NARIS_P0_04B_SCENE_RESULT="+json.dumps(result,ensure_ascii=False))
if not saved:
    raise RuntimeError("P0-04B QA scene save failed")
