# CALL OF NARIS — P0-BOSS-03 Ash Warden Unreal Import + Technical/Visual QA
# Candidate-only gate. Never replaces the gameplay proxy.
import unreal, json
from pathlib import Path

PROJECT_ROOT=Path(r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57")
BOSS_DIR=PROJECT_ROOT/"Production"/"Boss"/"AshWarden"
LOG2=BOSS_DIR/"P0-BOSS-02_rig_anim_pbr.json"
SOURCE=BOSS_DIR/"SK_AshWarden_Production.fbx"
REPORT=PROJECT_ROOT/"Reports"/"P0-BOSS-03_unreal_qa.json"

DEST="/Game/NARIS/Creatures/AshWardenProduction"
NAME="SK_NARIS_AshWarden_Production"
QA_MAP="/Game/NARIS/QA/L_AshWardenCandidate_QA"
BASELINE_PATHS=[
    "/Game/NARIS/Creatures/BoneBeast/SK_NARIS_BoneBeast_v1",
    "/Game/NARIS/Creatures/BoneBeast/SK_NARIS_BoneBeast",
    "/Game/NARIS/Creatures/BoneBeast_v1/SK_NARIS_BoneBeast_v1",
]
EXPECTED_ANIMS={
    "idle":"ashwarden_idle",
    "walk":"ashwarden_walk",
    "attack":"ashwarden_attack",
    "phase2":"ashwarden_phase2",
    "hitreact":"ashwarden_hitreact",
    "death":"ashwarden_death",
}

def fail(reason,extra=None):
    out={"status":"FAIL","candidate_only":True,"replacement_allowed":False,"reason":reason}
    if extra: out.update(extra)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    unreal.log_error("NARIS_P0_BOSS_03_FAIL "+json.dumps(out,ensure_ascii=False))
    raise RuntimeError(reason)

if not LOG2.is_file(): fail("missing_p0_boss_02_log")
g2=json.loads(LOG2.read_text(encoding="utf-8"))
if g2.get("status")!="PASS" or not g2.get("production_candidate"):
    fail("p0_boss_02_not_passed",{"gate":g2})
if not SOURCE.is_file(): fail("production_fbx_missing",{"source":str(SOURCE)})

unreal.EditorAssetLibrary.make_directory(DEST)

task=unreal.AssetImportTask()
task.set_editor_property("filename",str(SOURCE))
task.set_editor_property("destination_path",DEST)
task.set_editor_property("destination_name",NAME)
task.set_editor_property("automated",True)
task.set_editor_property("replace_existing",True)
task.set_editor_property("replace_existing_settings",True)
task.set_editor_property("save",True)

ui=unreal.FbxImportUI()
ui.set_editor_property("import_mesh",True)
ui.set_editor_property("import_as_skeletal",True)
ui.set_editor_property("import_animations",True)
ui.set_editor_property("import_materials",True)
ui.set_editor_property("import_textures",False)
ui.set_editor_property("mesh_type_to_import",unreal.FBXImportType.FBXIT_SKELETAL_MESH)
try: ui.set_editor_property("create_physics_asset",True)
except Exception: pass
try:
    sk=ui.get_editor_property("skeletal_mesh_import_data")
    sk.set_editor_property("preserve_smoothing_groups",True)
    sk.set_editor_property("update_skeleton_reference_pose",False)
    sk.set_editor_property("use_t0_as_ref_pose",False)
except Exception as exc:
    unreal.log_warning("NARIS_P0_BOSS_03_IMPORT_DATA "+str(exc))
task.set_editor_property("options",ui)

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])

assets=unreal.EditorAssetLibrary.list_assets(DEST,recursive=True,include_folder=False)
objects=[unreal.load_asset(p) for p in assets]
skeletal=[o for o in objects if isinstance(o,unreal.SkeletalMesh)]
anims=[o for o in objects if isinstance(o,unreal.AnimSequence)]
materials=[o for o in objects if isinstance(o,unreal.MaterialInterface)]

boss=unreal.load_asset(DEST+"/"+NAME)
if not boss or not isinstance(boss,unreal.SkeletalMesh):
    exact=[o for o in skeletal if o and NAME.lower() in o.get_name().lower()]
    boss=exact[0] if len(exact)==1 else None
if not boss:
    fail("production_skeletal_mesh_missing",{"skeletal":[o.get_path_name() for o in skeletal if o]})

skeleton=None; physics=None
try: skeleton=boss.get_editor_property("skeleton")
except Exception: pass
try: physics=boss.get_editor_property("physics_asset")
except Exception: pass

material_slots=[]
try:
    for slot in boss.get_editor_property("materials"):
        mi=slot.get_editor_property("material_interface")
        material_slots.append(mi.get_path_name() if mi else None)
except Exception as exc:
    unreal.log_warning("NARIS_P0_BOSS_03_MATERIAL_READ "+str(exc))

# Generate at least 3 LODs for the production candidate.
lod_count=None; lod_regenerated=False
try:
    ss=unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    if ss:
        lod_count=int(ss.get_lod_count(boss))
        if lod_count<3:
            lod_regenerated=bool(ss.regenerate_lod(boss,3,False,False))
            unreal.EditorAssetLibrary.save_loaded_asset(boss)
            lod_count=int(ss.get_lod_count(boss))
except Exception as exc:
    unreal.log_warning("NARIS_P0_BOSS_03_LOD "+str(exc))

# Resolve six expected animation actions by tolerant path/name matching.
resolved={}
for role,token in EXPECTED_ANIMS.items():
    match=next((a for a in anims if token in a.get_name().lower().replace("_","")),None)
    if not match:
        # Blender/FBX importers may preserve underscores or prepend the mesh name.
        simple=token.replace("ashwarden_","")
        match=next((a for a in anims if "ashwarden" in a.get_name().lower() and simple in a.get_name().lower()),None)
    resolved[role]=match

checks={
    "skeletal_mesh":boss is not None,
    "skeleton":skeleton is not None,
    "physics_asset":physics is not None,
    "material_slots_at_least_4":len(material_slots)>=4,
    "lod_count_at_least_3":lod_count is not None and lod_count>=3,
    "idle_animation":resolved["idle"] is not None,
    "walk_animation":resolved["walk"] is not None,
    "attack_animation":resolved["attack"] is not None,
    "phase2_animation":resolved["phase2"] is not None,
    "hitreact_animation":resolved["hitreact"] is not None,
    "death_animation":resolved["death"] is not None,
}
technical_pass=all(checks.values())

for obj in [boss,skeleton,physics]+[a for a in resolved.values() if a]:
    if not obj: continue
    try:
        unreal.EditorAssetLibrary.set_metadata_tag(obj,unreal.Name("NARIS.ProductionGate"),"P0-BOSS-03")
        unreal.EditorAssetLibrary.set_metadata_tag(obj,unreal.Name("NARIS.CandidateOnly"),"true")
        unreal.EditorAssetLibrary.set_metadata_tag(obj,unreal.Name("NARIS.VisualAcceptance"),"pending")
        unreal.EditorAssetLibrary.save_loaded_asset(obj)
    except Exception as exc:
        unreal.log_warning("NARIS_P0_BOSS_03_METADATA "+str(exc))

if not technical_pass:
    fail("technical_gate_failed",{
        "checks":checks,
        "animations":[a.get_path_name() for a in anims if a],
        "materials":material_slots,
        "lod_count":lod_count,
        "physics_asset":physics.get_path_name() if physics else None
    })

# ---------- Dedicated QA map ----------
level_sub=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
actor_sub=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
created=False
try:
    created=bool(level_sub.new_level(QA_MAP)) if hasattr(level_sub,"new_level") else bool(unreal.EditorLevelLibrary.new_level(QA_MAP))
except Exception:
    try: created=bool(unreal.EditorLevelLibrary.new_level(QA_MAP))
    except Exception as exc: fail("qa_map_creation_failed",{"error":str(exc)})

if not created:
    try:
        unreal.EditorLoadingAndSavingUtils.load_map(QA_MAP)
        for actor in list(actor_sub.get_all_level_actors()): actor_sub.destroy_actor(actor)
    except Exception as exc:
        fail("qa_map_load_failed",{"error":str(exc)})

def assign_mesh(comp,mesh):
    if hasattr(comp,"set_skeletal_mesh_asset"): comp.set_skeletal_mesh_asset(mesh)
    else: comp.set_editor_property("skeletal_mesh",mesh)

def spawn_sk(label,mesh,loc,anim=None):
    a=actor_sub.spawn_actor_from_class(unreal.SkeletalMeshActor,loc,unreal.Rotator(0,0,0))
    a.set_actor_label(label)
    comp=a.get_editor_property("skeletal_mesh_component")
    assign_mesh(comp,mesh)
    if anim:
        try: comp.set_animation_mode(unreal.AnimationMode.ANIMATION_SINGLE_NODE)
        except Exception: pass
        try: comp.play_animation(anim,True)
        except Exception as exc: unreal.log_warning("NARIS_P0_BOSS_03_PLAY "+label+" "+str(exc))
    return a

baseline=None
for path in BASELINE_PATHS:
    obj=unreal.load_asset(path)
    if obj and isinstance(obj,unreal.SkeletalMesh):
        baseline=obj;break

if baseline:
    spawn_sk("QA_PROXY_BoneBeast",baseline,unreal.Vector(0,-250,125),None)
spawn_sk("QA_ASHWARDEN_Idle",boss,unreal.Vector(0,0,125),resolved["idle"])
spawn_sk("QA_ASHWARDEN_Phase2",boss,unreal.Vector(0,250,125),resolved["phase2"])

cube=unreal.load_asset("/Engine/BasicShapes/Cube")
floor=actor_sub.spawn_actor_from_class(unreal.StaticMeshActor,unreal.Vector(0,0,-10),unreal.Rotator(0,0,0))
floor.set_actor_label("QA_BossFloor")
fcomp=floor.get_editor_property("static_mesh_component")
fcomp.set_editor_property("static_mesh",cube)
floor.set_actor_scale3d(unreal.Vector(10,8,.2))

sun=actor_sub.spawn_actor_from_class(unreal.DirectionalLight,unreal.Vector(0,0,600),unreal.Rotator(-36,-32,0))
sun.set_actor_label("QA_Key_Warm")
try:
    sc=sun.get_editor_property("directional_light_component")
    sc.set_editor_property("intensity",4.2)
    sc.set_editor_property("light_color",unreal.Color(255,174,108,255))
except Exception: pass

rim=actor_sub.spawn_actor_from_class(unreal.PointLight,unreal.Vector(-140,180,260),unreal.Rotator(0,0,0))
rim.set_actor_label("QA_Aether_Rim")
try:
    rc=rim.get_editor_property("point_light_component")
    rc.set_editor_property("intensity",3400.0)
    rc.set_editor_property("attenuation_radius",850.0)
    rc.set_editor_property("light_color",unreal.Color(74,216,255,255))
except Exception: pass

ember=actor_sub.spawn_actor_from_class(unreal.PointLight,unreal.Vector(160,-230,170),unreal.Rotator(0,0,0))
ember.set_actor_label("QA_Ember_Fill")
try:
    ec=ember.get_editor_property("point_light_component")
    ec.set_editor_property("intensity",2600.0)
    ec.set_editor_property("attenuation_radius",700.0)
    ec.set_editor_property("light_color",unreal.Color(255,74,28,255))
except Exception: pass

camera=actor_sub.spawn_actor_from_class(unreal.CameraActor,unreal.Vector(760,0,210),unreal.Rotator(0,0,0))
camera.set_actor_label("QA_Camera_AshWardenCompare")
camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera.get_actor_location(),unreal.Vector(0,0,135)),False)
try: camera.set_editor_property("auto_activate_for_player",unreal.AutoReceiveInput.PLAYER0)
except Exception: pass
try: camera.get_editor_property("camera_component").set_editor_property("field_of_view",48.0)
except Exception: pass

saved=False
try: saved=bool(level_sub.save_current_level())
except Exception:
    try: saved=bool(unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True,True))
    except Exception: saved=False

result={
    "status":"PASS" if saved else "FAIL_GATE",
    "candidate_only":True,
    "replacement_allowed":False,
    "technical_acceptance":technical_pass,
    "visual_acceptance":False,
    "asset":boss.get_path_name(),
    "skeleton":skeleton.get_path_name() if skeleton else None,
    "physics_asset":physics.get_path_name() if physics else None,
    "materials":material_slots,
    "lod_count":lod_count,
    "lod_regenerated":lod_regenerated,
    "animations":{k:(v.get_path_name() if v else None) for k,v in resolved.items()},
    "checks":checks,
    "qa_map":QA_MAP,
    "baseline_proxy":baseline.get_path_name() if baseline else None,
    "camera_actor":"QA_Camera_AshWardenCompare",
    "screenshot_target":"Saved/Screenshots/Windows/P0-BOSS-03_AshWardenCompare.png",
    "next_gate":"Render D3D12 boss QA, inspect silhouette/PBR/deformation/attack/phase2/death, then P0-BOSS-04 guarded replacement + packaged boss regression."
}
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
unreal.log("NARIS_P0_BOSS_03_RESULT="+json.dumps(result,ensure_ascii=False))
if not saved: raise RuntimeError("P0-BOSS-03 QA map save failed")
