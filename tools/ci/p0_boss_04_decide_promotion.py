# CALL OF NARIS — P0-BOSS-04 Promotion Decision Gate
# Pure Python, read-only. Consumes local evidence and emits a deterministic decision.
import argparse
import hashlib
import json
from pathlib import Path

DEFAULT_PROJECT=Path(r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57")

REQUIRED_CRITERIA=(
    "silhouette_unique_vs_proxy",
    "blackened_steel_bronze_burgundy_ember_language",
    "scale_and_proportion",
    "deformation_idle",
    "deformation_attack",
    "deformation_phase2",
    "deformation_death",
    "weapon_readability",
    "clipping_intersections",
    "boss_readability_at_camera_distance",
)
CANDIDATE="/Game/NARIS/Creatures/AshWardenProduction/SK_NARIS_AshWarden_Production"
QA_MAP="/Game/NARIS/QA/L_AshWardenCandidate_QA"

def load_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

def sha256_file(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",default=str(DEFAULT_PROJECT))
    ap.add_argument("--repo-root",default=str(Path(__file__).resolve().parents[2]))
    args=ap.parse_args()
    project=Path(args.project_root)
    repo=Path(args.repo_root)

    approval_path=repo/"data"/"P0_ASH_WARDEN_VISUAL_APPROVAL.json"
    evidence_path=project/"Reports"/"P0-BOSS-03_render_evidence.json"
    discovery_path=project/"Reports"/"P0-BOSS-04_integration_discovery.json"
    report_path=project/"Reports"/"P0-BOSS-04_decision.json"

    result={
        "status":"BLOCKED",
        "decision":"BLOCKED_MISSING_EVIDENCE",
        "replacement_allowed":False,
        "mutation_performed":False,
        "project_root":str(project),
        "inputs":{
            "approval":str(approval_path),
            "render_evidence":str(evidence_path),
            "integration_discovery":str(discovery_path),
        },
        "reasons":[],
    }

    missing=[str(p) for p in (approval_path,evidence_path,discovery_path) if not p.is_file()]
    if missing:
        result["reasons"].append({"missing_files":missing})
        report_path.parent.mkdir(parents=True,exist_ok=True)
        report_path.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
        print(json.dumps(result,indent=2,ensure_ascii=False))
        return 10

    approval=load_json(approval_path)
    evidence=load_json(evidence_path)
    discovery=load_json(discovery_path)

    # --- Visual approval gate ---
    visual_errors=[]
    if approval.get("approved") is not True:
        visual_errors.append("approved_not_true")
    if approval.get("decision") not in ("APPROVE","APPROVED","PASS"):
        visual_errors.append("decision_not_approved")
    if approval.get("replacement_allowed") is not False:
        # Approval itself is evidence only; it must never pre-authorize mutation.
        visual_errors.append("approval_file_must_keep_replacement_allowed_false")
    if approval.get("candidate")!=CANDIDATE:
        visual_errors.append("approval_candidate_mismatch")
    if approval.get("qa_map")!=QA_MAP:
        visual_errors.append("approval_qa_map_mismatch")
    if not str(approval.get("approved_by") or "").strip():
        visual_errors.append("approved_by_missing")
    if not str(approval.get("approved_at") or "").strip():
        visual_errors.append("approved_at_missing")

    criteria=approval.get("criteria") or {}
    failed_criteria={
        key:criteria.get(key)
        for key in REQUIRED_CRITERIA
        if str(criteria.get(key,"")).lower() not in ("pass","approved","ok")
    }
    if failed_criteria:
        visual_errors.append({"criteria_not_passed":failed_criteria})

    expected_hash=str(approval.get("screenshot_sha256") or "").lower().strip()
    expected_bytes=int(approval.get("screenshot_bytes") or 0)
    if len(expected_hash)!=64:
        visual_errors.append("approval_sha256_invalid")
    if expected_bytes<=0:
        visual_errors.append("approval_byte_count_invalid")

    # --- Exact render evidence binding ---
    evidence_errors=[]
    if evidence.get("status")!="PASS":
        evidence_errors.append("render_evidence_not_passed")
    if evidence.get("candidate")!=CANDIDATE:
        evidence_errors.append("evidence_candidate_mismatch")
    if evidence.get("qa_map")!=QA_MAP:
        evidence_errors.append("evidence_qa_map_mismatch")
    if str(evidence.get("pipeline_revision") or "")!=str(approval.get("pipeline_revision") or ""):
        evidence_errors.append("pipeline_revision_mismatch")
    if str(evidence.get("git_sha") or "")!=str(approval.get("evidence_git_sha") or ""):
        evidence_errors.append("git_sha_mismatch")
    if str(evidence.get("workflow_run_id") or "")!=str(approval.get("evidence_workflow_run_id") or ""):
        evidence_errors.append("workflow_run_id_mismatch")
    if str(evidence.get("screenshot_sha256") or "").lower()!=expected_hash:
        evidence_errors.append("evidence_sha256_mismatch")
    if int(evidence.get("screenshot_bytes") or 0)!=expected_bytes:
        evidence_errors.append("evidence_byte_count_mismatch")

    screenshot_ref=evidence.get("screenshot_path")
    screenshot=Path(str(screenshot_ref)) if screenshot_ref else None
    if screenshot and not screenshot.is_absolute():
        screenshot=project/screenshot
    if not screenshot or not screenshot.is_file():
        evidence_errors.append("screenshot_file_missing")
    else:
        actual_hash=sha256_file(screenshot)
        actual_bytes=screenshot.stat().st_size
        if actual_hash.lower()!=expected_hash:
            evidence_errors.append("actual_screenshot_sha256_mismatch")
        if actual_bytes!=expected_bytes:
            evidence_errors.append("actual_screenshot_byte_count_mismatch")
        result["screenshot"]={
            "path":str(screenshot),
            "sha256":actual_hash,
            "bytes":actual_bytes,
        }

    # --- Integration discovery gate ---
    discovery_errors=[]
    if discovery.get("status")!="PASS":
        discovery_errors.append("discovery_not_passed")
    if discovery.get("read_only") is not True:
        discovery_errors.append("discovery_not_read_only")
    if discovery.get("replacement_allowed") is not False:
        discovery_errors.append("discovery_must_not_allow_replacement")
    if not discovery.get("target"):
        discovery_errors.append("target_missing")
    if not discovery.get("recommended_integration_strategy"):
        discovery_errors.append("integration_strategy_missing")

    result["visual_errors"]=visual_errors
    result["evidence_errors"]=evidence_errors
    result["discovery_errors"]=discovery_errors
    result["candidate"]=CANDIDATE
    result["qa_map"]=QA_MAP
    result["integration_target"]=discovery.get("target")
    result["current_proxy_meshes"]=discovery.get("current_proxy_meshes",[])
    result["bonebeast_proxy_confirmed"]=bool(discovery.get("bonebeast_proxy_confirmed"))
    result["native_skeletal_component"]=bool(discovery.get("native_skeletal_component"))
    result["recommended_integration_strategy"]=discovery.get("recommended_integration_strategy")

    if visual_errors:
        result["decision"]="BLOCKED_VISUAL_APPROVAL"
        result["reasons"].append({"visual":visual_errors})
        code=20
    elif evidence_errors:
        result["decision"]="BLOCKED_RENDER_EVIDENCE"
        result["reasons"].append({"render_evidence":evidence_errors})
        code=21
    elif discovery_errors:
        result["decision"]="BLOCKED_INTEGRATION_DISCOVERY"
        result["reasons"].append({"discovery":discovery_errors})
        code=22
    elif bool(discovery.get("native_skeletal_component")):
        result["decision"]="BLOCKED_NATIVE_CXX"
        result["reasons"].append(
            "Skeletal component is Native; inspect local NarisAshWarden C++ constructor/BeginPlay before authoring any override."
        )
        code=30
    elif not discovery.get("target",{}).get("skeletal_components"):
        result["decision"]="BLOCKED_CLASS_INSPECTION"
        result["reasons"].append(
            "Target actor has no discoverable skeletal component; class/Blueprint ownership must be inspected."
        )
        code=31
    else:
        result["status"]="READY"
        result["decision"]="READY_INSTANCE_OVERRIDE"
        result["replacement_allowed"]=True
        result["reasons"].append(
            "All evidence matches and discovered skeletal component is non-native. Author a reversible instance/Blueprint override, then require packaged regression."
        )
        code=0

    report_path.parent.mkdir(parents=True,exist_ok=True)
    report_path.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return code

if __name__=="__main__":
    raise SystemExit(main())
