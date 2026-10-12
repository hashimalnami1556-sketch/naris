# CALL OF NARIS — P0-05 Hero Promotion
# Requires explicit P0-04B visual approval. Creates reversible asset swap.
import unreal, json
from pathlib import Path

PROJECT_ROOT=Path(r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57")
REPO_ROOT=Path(__file__).resolve().parents[2] if "__file__" in globals() else None
APPROVAL_CANDIDATES=[
    PROJECT_ROOT/"data"/"P0_HERO_VISUAL_APPROVAL.json",
]
if REPO_ROOT:
    APPROVAL_CANDIDATES.insert(0,REPO_ROOT/"data"/"P0_HERO_VISUAL_APPROVAL.json")
REPORT_A=PROJECT_ROOT/"Reports"/"P0-04A_hero_technical_qa.json"
REPORT_B=PROJECT_ROOT/"Reports"/"P0-04B_visual_scene.json"
REPORT=PROJECT_ROOT/"Reports"/"P0-05_promotion.json"

CANDIDATE="/Game/NARIS/Characters/HeroProduction/SK_NARIS_AshenVessel_Production"
ACTIVE="/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3"
ARCHIVE="/Game/NARIS/Characters/HeroV3/Archive/SK_NARIS_AshenVessel_v3_PreP0"

def fail(reason,extra=None):
    out={"status":"FAIL","promoted":False,"reason":reason}
    if extra: out.update(extra)
    REPORT.parent.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    unreal.log_error("NARIS_P0_05_FAIL "+json.dumps(out,ensure_ascii=False))
    raise RuntimeError(reason)

approval_path=next((p for p in APPROVAL_CANDIDATES if p.is_file()),None)
if not approval_path:
    fail("visual_approval_file_missing")
approval=json.loads(approval_path.read_text(encoding="utf-8"))
if approval.get("approved") is not True:
    fail("visual_approval_not_granted",{"decision":approval.get("decision")})
if approval.get("decision") not in ("APPROVE","APPROVED","PASS"):
    fail("visual_approval_decision_invalid",{"decision":approval.get("decision")})
if not approval.get("screenshot"):
    fail("visual_approval_missing_screenshot_reference")

for p,label in ((REPORT_A,"P0-04A"),(REPORT_B,"P0-04B")):
    if not p.is_file():
        fail(label.lower()+"_report_missing")
p4a=json.loads(REPORT_A.read_text(encoding="utf-8"))
p4b=json.loads(REPORT_B.read_text(encoding="utf-8"))
if p4a.get("status")!="PASS" or not p4a.get("technical_acceptance"):
    fail("p0_04a_not_passed")
if p4b.get("status")!="PASS" or not p4b.get("visual_scene_prepared"):
    fail("p0_04b_scene_not_passed")

candidate=unreal.load_asset(CANDIDATE)
active=unreal.load_asset(ACTIVE)
if not candidate or not isinstance(candidate,unreal.SkeletalMesh):
    fail("candidate_missing")
if not active or not isinstance(active,unreal.SkeletalMesh):
    fail("active_hero_missing")

cand_skel=candidate.get_editor_property("skeleton")
active_skel=active.get_editor_property("skeleton")
if cand_skel != active_skel:
    fail("skeleton_mismatch_at_promotion",{
        "candidate_skeleton":cand_skel.get_path_name() if cand_skel else None,
        "active_skeleton":active_skel.get_path_name() if active_skel else None
    })

if unreal.EditorAssetLibrary.does_asset_exist(ARCHIVE):
    fail("archive_path_already_exists",{"archive":ARCHIVE})

unreal.EditorAssetLibrary.make_directory("/Game/NARIS/Characters/HeroV3/Archive")

if not unreal.EditorAssetLibrary.rename_asset(ACTIVE,ARCHIVE):
    fail("failed_to_archive_working_hero")
if not unreal.EditorAssetLibrary.rename_asset(CANDIDATE,ACTIVE):
    # Immediate rollback if candidate rename fails.
    unreal.EditorAssetLibrary.rename_asset(ARCHIVE,ACTIVE)
    fail("failed_to_promote_candidate_rolled_back")

promoted=unreal.load_asset(ACTIVE)
if not promoted:
    # Best effort rollback.
    unreal.EditorAssetLibrary.rename_asset(ACTIVE,CANDIDATE)
    unreal.EditorAssetLibrary.rename_asset(ARCHIVE,ACTIVE)
    fail("promoted_asset_not_loadable_rolled_back")

for key,value in {
    "NARIS.ProductionGate":"P0-05",
    "NARIS.Promoted":"true",
    "NARIS.VisualEvidence":str(approval.get("screenshot")),
    "NARIS.PreviousHero":ARCHIVE,
}.items():
    try:
        unreal.EditorAssetLibrary.set_metadata_tag(promoted,unreal.Name(key),str(value))
    except Exception:
        pass
unreal.EditorAssetLibrary.save_loaded_asset(promoted)
unreal.EditorAssetLibrary.save_directory("/Game/NARIS/Characters/HeroV3",False,True)

result={
    "status":"PASS",
    "promoted":True,
    "active_path":ACTIVE,
    "archive_path":ARCHIVE,
    "candidate_original_path":CANDIDATE,
    "skeleton":cand_skel.get_path_name() if cand_skel else None,
    "visual_approval":approval,
    "next_gate":"Win64 build + cook/stage/pak + packaged D3D12 NARISCOMBATQA. Roll back on any failure."
}
REPORT.parent.mkdir(parents=True,exist_ok=True)
REPORT.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
unreal.log("NARIS_P0_05_PROMOTION="+json.dumps(result,ensure_ascii=False))
