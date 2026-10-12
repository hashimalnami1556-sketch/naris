# CALL OF NARIS — P0-BOSS-04 Guarded Native Ash Warden Patch
# Pure Python. Mutates ONLY ANarisAshWarden constructor after exact source fingerprint verification.
import argparse, hashlib, json, re, shutil
from pathlib import Path

DEFAULT_PROJECT=Path(r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57")
SIGNATURE="ANarisAshWarden::ANarisAshWarden()"
REPORT_NAME="P0-BOSS-04_native_patch.json"
DECISION_NAME="P0-BOSS-04_decision.json"
DISCOVERY_NAME="P0-BOSS-04_integration_discovery.json"
BOSS03_NAME="P0-BOSS-03_unreal_qa.json"

def sha_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def read_text(path):
    return path.read_text(encoding="utf-8-sig")

def write_json(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding="utf-8")

def extract_block(source,signature):
    pos=source.find(signature)
    if pos<0:return None,None,None
    brace=source.find("{",pos)
    if brace<0:return None,None,None
    depth=0
    for i in range(brace,len(source)):
        ch=source[i]
        if ch=="{":depth+=1
        elif ch=="}":
            depth-=1
            if depth==0:
                return pos,i+1,source[pos:i+1]
    return None,None,None

def asset_ref(path):
    path=str(path or "").strip()
    if not path:return ""
    if "." in path.rsplit("/",1)[-1]:
        return path
    name=path.rsplit("/",1)[-1]
    return path+"."+name

def classify_proxy_path(path):
    low=path.lower()
    if "bonebeast" not in low and "bone_beast" not in low:
        return None
    leaf=low.rsplit("/",1)[-1]
    if "idle" in leaf:return "idle"
    if "run" in leaf or "walk" in leaf:return "walk"
    if "attack" in leaf:return "attack"
    if "sk_" in leaf or "skeletal" in leaf:return "mesh"
    return "unknown"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--project-root",default=str(DEFAULT_PROJECT))
    ap.add_argument("--mode",choices=("apply","rollback"),default="apply")
    args=ap.parse_args()

    project=Path(args.project_root)
    reports=project/"Reports"
    backups=reports/"Backups"
    patch_report=reports/REPORT_NAME
    source=project/"Source"/"NARIS"/"NarisCreature.cpp"

    if args.mode=="rollback":
        if not patch_report.is_file():
            raise SystemExit("rollback_report_missing")
        rep=json.loads(patch_report.read_text(encoding="utf-8-sig"))
        backup=Path(rep.get("backup_path") or "")
        if not source.is_file() or not backup.is_file():
            raise SystemExit("rollback_source_or_backup_missing")
        current=read_text(source)
        current_sha=sha_text(current)
        expected_after=rep.get("after_cpp_sha256")
        if current_sha!=expected_after:
            raise SystemExit("rollback_refused_source_changed_after_patch")
        restored=read_text(backup)
        if sha_text(restored)!=rep.get("before_cpp_sha256"):
            raise SystemExit("rollback_backup_hash_mismatch")
        source.write_text(restored,encoding="utf-8")
        final=read_text(source)
        ok=sha_text(final)==rep.get("before_cpp_sha256")
        rollback={
            "status":"PASS" if ok else "FAIL",
            "restored":ok,
            "source":str(source),
            "restored_sha256":sha_text(final),
            "expected_sha256":rep.get("before_cpp_sha256"),
            "from_backup":str(backup),
        }
        write_json(reports/"P0-BOSS-04_native_rollback.json",rollback)
        if not ok:raise SystemExit("rollback_verification_failed")
        print(json.dumps(rollback,indent=2))
        return 0

    required=[
        reports/DECISION_NAME,
        reports/DISCOVERY_NAME,
        reports/BOSS03_NAME,
        source,
    ]
    missing=[str(p) for p in required if not p.is_file()]
    if missing:
        raise SystemExit("missing_inputs:"+json.dumps(missing))

    decision=json.loads((reports/DECISION_NAME).read_text(encoding="utf-8-sig"))
    discovery=json.loads((reports/DISCOVERY_NAME).read_text(encoding="utf-8-sig"))
    boss03=json.loads((reports/BOSS03_NAME).read_text(encoding="utf-8-sig"))

    if decision.get("status")!="READY" or decision.get("decision")!="READY_NATIVE_CXX_PATCH":
        raise SystemExit("native_patch_not_authorized_by_decision")
    if decision.get("replacement_allowed") is not True:
        raise SystemExit("decision_replacement_not_allowed")
    if discovery.get("native_skeletal_component") is not True:
        raise SystemExit("discovery_not_native")
    if discovery.get("bonebeast_proxy_confirmed") is not True:
        raise SystemExit("runtime_bonebeast_proxy_not_confirmed")
    if boss03.get("status")!="PASS" or boss03.get("technical_acceptance") is not True:
        raise SystemExit("boss03_not_passed")

    evidence=discovery.get("source_evidence") or {}
    current=read_text(source)
    current_sha=sha_text(current)
    if current_sha!=evidence.get("cpp_sha256"):
        raise SystemExit("source_cpp_sha256_changed_since_discovery")

    start,end,ctor=extract_block(current,SIGNATURE)
    if ctor is None:
        raise SystemExit("ashwarden_constructor_missing")
    if sha_text(ctor)!=evidence.get("ashwarden_constructor_sha256"):
        raise SystemExit("constructor_sha256_changed_since_discovery")

    candidate_mesh=asset_ref(boss03.get("asset"))
    anims=boss03.get("animations") or {}
    targets={
        "mesh":candidate_mesh,
        "idle":asset_ref(anims.get("idle")),
        "walk":asset_ref(anims.get("walk")),
        "attack":asset_ref(anims.get("attack")),
    }
    missing_targets=[k for k,v in targets.items() if not v]
    if missing_targets:
        raise SystemExit("candidate_asset_paths_missing:"+",".join(missing_targets))

    string_re=re.compile(r'(?P<q>["\'])(?P<path>/Game/[^"\']+)(?P=q)')
    replacements=[]
    seen_roles=set()

    def replace_match(m):
        old=m.group("path")
        role=classify_proxy_path(old)
        if role in targets:
            new=targets[role]
            seen_roles.add(role)
            replacements.append({"role":role,"old":old,"new":new})
            return m.group("q")+new+m.group("q")
        return m.group(0)

    patched_ctor=string_re.sub(replace_match,ctor)
    required_roles={"mesh","idle","walk","attack"}
    if not required_roles.issubset(seen_roles):
        raise SystemExit("constructor_proxy_roles_incomplete:"+json.dumps({
            "required":sorted(required_roles),
            "found":sorted(seen_roles),
            "constructor":ctor
        }))

    if "NARIS_BOSS_ART_READY" not in patched_ctor:
        if not all(token in patched_ctor for token in ("IdleAnimation","RunAnimation","AttackAnimation")):
            raise SystemExit("constructor_animation_fields_not_found_for_runtime_marker")
        close=patched_ctor.rfind("}")
        marker=r'''
#if !UE_BUILD_SHIPPING
 UE_LOG(LogTemp,Display,TEXT("NARIS_BOSS_ART_READY Mesh=%s Idle=%s Run=%s Attack=%s"),
  *GetNameSafe(GetMesh()->GetSkeletalMeshAsset()),
  *GetNameSafe(IdleAnimation),
  *GetNameSafe(RunAnimation),
  *GetNameSafe(AttackAnimation));
#endif
'''
        patched_ctor=patched_ctor[:close]+marker+patched_ctor[close:]

    patched=current[:start]+patched_ctor+current[end:]
    after_sha=sha_text(patched)
    if after_sha==current_sha:
        raise SystemExit("patch_produced_no_change")

    backups.mkdir(parents=True,exist_ok=True)
    backup=backups/f"NarisCreature_pre_p0_boss04_{current_sha[:12]}.cpp"
    if backup.exists():
        if sha_text(read_text(backup))!=current_sha:
            raise SystemExit("existing_backup_hash_conflict")
    else:
        shutil.copy2(source,backup)

    source.write_text(patched,encoding="utf-8")
    verify=read_text(source)
    if sha_text(verify)!=after_sha:
        source.write_text(current,encoding="utf-8")
        raise SystemExit("patch_write_verification_failed_restored")

    result={
        "status":"PASS",
        "mutation_performed":True,
        "source":str(source),
        "backup_path":str(backup),
        "before_cpp_sha256":current_sha,
        "after_cpp_sha256":after_sha,
        "before_constructor_sha256":sha_text(ctor),
        "after_constructor_sha256":sha_text(patched_ctor),
        "candidate_mesh":targets["mesh"],
        "candidate_animations":{
            "idle":targets["idle"],
            "walk":targets["walk"],
            "attack":targets["attack"],
            "phase2":asset_ref(anims.get("phase2")),
            "hitreact":asset_ref(anims.get("hitreact")),
            "death":asset_ref(anims.get("death")),
        },
        "replacements":replacements,
        "runtime_marker":"NARIS_BOSS_ART_READY",
        "rollback_command":"python tools/ci/p0_boss_04_patch_native_source.py --mode rollback",
    }
    write_json(patch_report,result)
    print(json.dumps(result,indent=2,ensure_ascii=False))
    return 0

if __name__=="__main__":
    raise SystemExit(main())
