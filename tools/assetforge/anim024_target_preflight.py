"""ANIM-024 read-only target SkeletalMesh snapshot and semantic retarget mapping.

No Unreal asset is created, updated, or saved. Real target IK Rig / Retargeter
cannot be authored until an imported target mesh and manually reviewed chain
mapping exist. NEVER infer target Manny/Quinn bones from the source GLB.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

SCHEMA = "naris.anim024.target-skeleton.v1"
MAP_SCHEMA = "naris.anim024.manual-retarget-map.v1"
REQUIRED_CHAINS = frozenset(("Root","Spine","Head","LeftArm","RightArm","LeftLeg","RightLeg"))
REQUIRED_PLUGINS = frozenset(("PythonScriptPlugin","IKRig","MeshModelingToolset"))
OBJECT_PATH = re.compile(r"^/Game/(?:[A-Za-z0-9_]+/)*[A-Za-z0-9_]+\.[A-Za-z0-9_]+$")


def _object_path(path: str) -> str:
    if not isinstance(path,str) or not OBJECT_PATH.fullmatch(path):
        raise ValueError("Require an existing named /Game/.../Asset.Asset object path; no Engine or filesystem paths")
    return path


def _parents(snapshot: dict):
    if snapshot.get("schema") != SCHEMA:
        raise ValueError("Unknown target-skeleton schema")
    _object_path(snapshot.get("skeletal_mesh_object_path"))
    ver = snapshot.get("engine_version")
    if not isinstance(ver,str) or not re.match(r"^5\.7(?:\.|$)",ver):
        raise ValueError("Only Unreal Engine 5.7 source capture is accepted")
    b = snapshot.get("bones")
    if not isinstance(b,list) or len(b) < 4:
        raise ValueError("No valid target skeleton bone array")
    names = [entry.get("name") for entry in b if isinstance(entry,dict)]
    if len(names)!=len(b) or any(not isinstance(n,str) or not n or not re.fullmatch(r"[A-Za-z0-9_.]+",n) for n in names):
        raise ValueError("Malformed bone name")
    if len(set(names)) != len(names):
        raise ValueError("Duplicate target bones")
    parents = {entry["name"]:entry.get("parent") for entry in b}
    for n,p in parents.items():
        if p is not None and (p not in parents or p==n):
            raise ValueError(f"Unknown or self-parent target bone: {n}")
    roots=[n for n,p in parents.items() if p is None]
    if len(roots)!=1:
        raise ValueError("Exactly one target skeleton root is required")
    for bone in parents:
        seen=set();q=bone
        while q is not None:
            if q in seen:raise ValueError("Cycle in target skeleton")
            seen.add(q);q=parents[q]
    return parents,roots[0]


def validate_snapshot(snapshot: dict) -> dict:
    parents,root=_parents(snapshot)
    is_engine=snapshot.get("is_unreal_editor_capture") is True
    if snapshot.get("asset_modified") is True:
        raise ValueError("Snapshot says source asset modified")
    return {"root":root,"bone_count":len(parents),"parents":parents,
            "claimed_editor_capture":is_engine,"engine_evidence":is_engine,
            "skeletal_mesh_object_path":snapshot["skeletal_mesh_object_path"],
            "engine_version":snapshot["engine_version"],
            "production_ready":False}


def _ancestor_path(parents: dict, start: str, end: str):
    if start not in parents or end not in parents:
        raise ValueError(f"Chain bone missing: {start} → {end}")
    seen=set();route=[end]
    while route[-1]!=start:
        if route[-1] in seen:raise ValueError("Parent cycle in chain")
        seen.add(route[-1])
        parent=parents[route[-1]]
        if parent is None:
            raise ValueError(f"Non-ancestral chain {start} → {end}")
        route.append(parent)
    return list(reversed(route))


def validate_manual_mapping(snapshot: dict, mapping: dict) -> dict:
    s=validate_snapshot(snapshot)
    if mapping.get("schema") != MAP_SCHEMA:
        raise ValueError("Unknown manually approved target-chain schema")
    chains=mapping.get("chains")
    if not isinstance(chains,dict) or set(chains)!=REQUIRED_CHAINS:
        raise ValueError("Exactly the seven source semantic chains must be mapped")
    parents=s["parents"]
    resolved={}
    for name in sorted(REQUIRED_CHAINS):
        spec=chains[name]
        if not isinstance(spec,dict) or not isinstance(spec.get("start"),str) or not isinstance(spec.get("end"),str):
            raise ValueError(f"Missing explicit target chain endpoints: {name}")
        start,end=spec["start"],spec["end"]
        path=_ancestor_path(parents,start,end)
        if len(path)<2:raise ValueError("Target retarget chain needs at least two bones")
        resolved[name]={"start":start,"end":end,"ancestral_path":path}
    rroot=mapping.get("target_retarget_root")
    if rroot not in parents or rroot!=resolved["Root"]["end"]:
        raise ValueError("Target retarget root does not agree with Root chain")
    if resolved["Root"]["start"]!=s["root"] or resolved["Spine"]["start"]!=rroot:
        raise ValueError("Root/Spine chain boundary inconsistent with target skeleton")
    # Manual labels are not trusted for simulation or approval; no automatic
    # semantic mapping inferred from bone name similarity or target brand.
    return {"target_root":s["root"],"retarget_root":rroot,
            "resolved_chains":resolved,"mapped_chain_count":7,
            "explicitly_approved":mapping.get("explicitly_approved") is True,
            "production_ready":False}


def build_target_review(snapshot: dict, mapping: dict) -> dict:
    s=validate_snapshot(snapshot)
    m=validate_manual_mapping(snapshot,mapping)
    return {"id":"ANIM-024-TARGET-PREFLIGHT",
            "status":"TARGET_MAPPING_STRUCTURE_VERIFIED_RUNTIME_NOT_APPROVED",
            "source":"7 source chains, 18-joint prototype from ANIM-024 pinned GLBs",
            "target_mesh_object_path":s["skeletal_mesh_object_path"],
            "target_bone_count":s["bone_count"],
            "target_retarget_root":m["retarget_root"],
            "verified_chain_count":m["mapped_chain_count"],
            "target_chain_paths":m["resolved_chains"],
            "verified_in_engine":False,
            "reported_editor_capture":s["claimed_editor_capture"],
            "capture_claim_only":True,
            "target_skeletal_mesh_runtime_test":"NOT_RUN",
            "target_ikrig_asset":"NOT_CREATED",
            "retargeter_asset":"NOT_CREATED",
            "target_pose_alignment":"NOT_RUN",
            "retarget_playback":"NOT_RUN",
            "network_gameplay":"NOT_RUN",
            "production_ready":False,
            "merge_allowed":False,
            "notes":"This verifies user-supplied snapshot structure only. The Editor capture flag can be forged; actual UE editor validation requires engine logs/screenshots."}


def required_plugin_settings(uproject: dict) -> dict:
    plugins=uproject.get("Plugins",[])
    states={}
    for item in plugins:
        if isinstance(item,dict) and isinstance(item.get("Name"),str):
            states[item["Name"]]=item.get("Enabled") is True
    missing=sorted(name for name in REQUIRED_PLUGINS if not states.get(name,False))
    return {"required_explicit_plugins":sorted(REQUIRED_PLUGINS),
            "missing_explicit_enablement":missing,
            "project_metadata_preflight_pass":not missing,
            "warning":"Missing .uproject entry does not prove engine plugin unavailable. Check Editor before enabling."}


def inspect_target_in_unreal(unreal,mesh_object_path: str) -> dict:
    # This only calls read accessors. No EditorAssetLibrary.save*, asset tools,
    # SkeletonModifier.commit, mesh edits or IK Rig authoring is allowed.
    _object_path(mesh_object_path)
    version=str(unreal.SystemLibrary.get_engine_version())
    if not re.match(r"^5\.7(?:\.|$)",version):
        raise RuntimeError("Target scan requires Unreal 5.7")
    mesh=unreal.load_asset(mesh_object_path)
    if mesh is None or not isinstance(mesh,unreal.SkeletalMesh):
        raise ValueError("Target SkeletalMesh not found; no guessing")
    mod=unreal.SkeletonModifier()
    if not mod.set_skeletal_mesh(mesh):
        raise RuntimeError("SkeletonModifier unavailable or cannot read selected mesh")
    names=[str(n) for n in mod.get_all_bone_names()]
    bones=[]
    for name in names:
        raw=str(mod.get_parent_name(name))
        parent=None if raw in ("None","NAME_None","") else raw
        bones.append({"name":name,"parent":parent})
    snapshot={"schema":SCHEMA,"skeletal_mesh_object_path":mesh_object_path,
              "engine_version":version,"bones":bones,
              "is_unreal_editor_capture":True,"asset_modified":False}
    validate_snapshot(snapshot)
    return snapshot


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--uproject",type=Path,required=True)
    p.add_argument("--target-snapshot",type=Path)
    p.add_argument("--manual-mapping",type=Path)
    p.add_argument("--mesh-asset")
    p.add_argument("--capture-unreal",action="store_true",
                   help="READ-ONLY capture inside Unreal 5.7 Python; does not edit assets")
    p.add_argument("--output",type=Path,required=True)
    args=p.parse_args()
    if args.output.exists():
        raise SystemExit("Refusing to overwrite existing report")
    if args.target_snapshot and args.capture_unreal:
        raise SystemExit("Cannot mix file snapshot and editor capture")
    if args.manual_mapping and not (args.target_snapshot or args.capture_unreal):
        raise SystemExit("Explicit manual mapping needs an actual target snapshot")
    uproject=json.loads(args.uproject.read_text(encoding="utf-8"))
    report={"id":"ANIM-024-UE-TARGET-READINESS",
            "plugin_metadata":required_plugin_settings(uproject),
            "target_asset_found_in_repo":False,
            "status":"BLOCKED_NO_IMPORTED_TARGET_MESH",
            "ikretargeter":"NOT_CREATED",
            "engine_build":"NOT_RUN","source_original_unchanged":True,
            "production_ready":False}
    if args.capture_unreal:
        if not args.mesh_asset:raise SystemExit("--capture-unreal needs --mesh-asset")
        import unreal
        snapshot=inspect_target_in_unreal(unreal,args.mesh_asset)
        report["target_snapshot"]=snapshot
        report["status"]="TARGET_SNAPSHOT_CAPTURED_NOT_APPROVED"
    elif args.target_snapshot:
        snapshot=json.loads(args.target_snapshot.read_text(encoding="utf-8"))
        report["target_snapshot_structure"]=validate_snapshot(snapshot)
        report["status"]="TARGET_SNAPSHOT_STRUCTURALLY_VALID_NOT_APPROVED"
    else:
        snapshot=None
    if args.manual_mapping and snapshot:
        m=json.loads(args.manual_mapping.read_text(encoding="utf-8"))
        report["review"]=build_target_review(snapshot,m)
        report["status"]="MANUAL_MAPPING_STRUCTURALLY_VALID_NOT_RUNTIME_APPROVED"
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":report["status"],"output":str(args.output)},ensure_ascii=False))


if __name__=="__main__":
    main()
