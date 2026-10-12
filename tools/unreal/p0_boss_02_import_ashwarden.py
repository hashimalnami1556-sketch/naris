# CALL OF NARIS — P0-BOSS-02 Unreal Ash Warden Candidate Import
import unreal, json
from pathlib import Path

PROJECT_ROOT=Path(r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57")
BOSS_DIR=PROJECT_ROOT/"Production"/"Boss"/"AshWarden"
SOURCE=BOSS_DIR/"SK_AshWarden_Candidate.fbx"
LOG1=BOSS_DIR/"P0-BOSS_AshWarden_log.json"
REPORT=PROJECT_ROOT/"Reports"/"P0-BOSS-02_unreal_import.json"
DEST="/Game/NARIS/Creatures/AshWardenProduction"
NAME="SK_NARIS_AshWarden_Candidate"

def fail(reason,extra=None):
    out={"status":"FAIL","reason":reason,"candidate_only":True}
    if extra: out.update(extra)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    unreal.log_error("NARIS_P0_BOSS_02_FAIL "+json.dumps(out,ensure_ascii=False))
    raise RuntimeError(reason)

if not LOG1.is_file(): fail("missing_blender_gate_log")
gate=json.loads(LOG1.read_text(encoding="utf-8"))
if gate.get("status")!="PASS_CANDIDATE": fail("blender_candidate_gate_not_passed",{"gate":gate})
if not SOURCE.is_file(): fail("candidate_fbx_missing",{"source":str(SOURCE)})

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
ui.set_editor_property("import_animations",False)
ui.set_editor_property("import_materials",True)
ui.set_editor_property("import_textures",False)
ui.set_editor_property("mesh_type_to_import",unreal.FBXImportType.FBXIT_SKELETAL_MESH)
task.set_editor_property("options",ui)

unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
objs=list(task.get_objects())
skeletal=[o for o in objs if isinstance(o,unreal.SkeletalMesh)]
if not skeletal:
    for path in unreal.EditorAssetLibrary.list_assets(DEST,recursive=True,include_folder=False):
        o=unreal.load_asset(path)
        if isinstance(o,unreal.SkeletalMesh): skeletal.append(o)
if len(skeletal)!=1:
    fail("skeletal_mesh_count_not_one",{"objects":[o.get_path_name() for o in objs],"skeletal":[o.get_path_name() for o in skeletal]})

boss=skeletal[0]
skel=boss.get_editor_property("skeleton")
mats=[]
for slot in boss.get_editor_property("materials"):
    try:
        mi=slot.get_editor_property("material_interface")
        mats.append(mi.get_path_name() if mi else None)
    except Exception:
        mats.append(None)

checks={
 "skeletal_mesh":True,
 "skeleton":skel is not None,
 "material_slots_at_least_3":len(mats)>=3,
 "source_gate_candidate_only":gate.get("production_grade") is False
}
passed=all(checks.values())
for key,val in {
 "NARIS.ProductionGate":"P0-BOSS-02",
 "NARIS.CandidateOnly":"true",
 "NARIS.SourceFBX":str(SOURCE),
 "NARIS.VisualAcceptance":"pending"
}.items():
    try: unreal.EditorAssetLibrary.set_metadata_tag(boss,unreal.Name(key),str(val))
    except Exception: pass
unreal.EditorAssetLibrary.save_loaded_asset(boss)
unreal.EditorAssetLibrary.save_directory(DEST,only_if_is_dirty=False,recursive=True)

result={
 "status":"PASS" if passed else "FAIL_GATE",
 "candidate_only":True,
 "asset":boss.get_path_name(),
 "skeleton":skel.get_path_name() if skel else None,
 "materials":mats,
 "checks":checks,
 "source_gate":gate,
 "next_gate":"P0-BOSS-03 boss rig/animation/PBR + D3D12 arena QA before replacing BoneBeast proxy."
}
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
unreal.log("NARIS_P0_BOSS_02_RESULT="+json.dumps(result,ensure_ascii=False))
if not passed: raise RuntimeError("P0-BOSS-02 gate failed")
