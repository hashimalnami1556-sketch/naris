"""ANIM-024: inventory expected W04 animation bindings WITHOUT claiming UE playback.

File presence is weaker than actual loading + montage notify validation inside UE.
This tool never creates montage assets or modifies content. Missing checked-in
assets are reported, not fabricated.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

EXPECTED_SCHEMA="naris.w04.animation-bindings.v1"
PATH_RE=re.compile(r"^/Game/(?:[A-Za-z0-9_]+/)*[A-Za-z0-9_]+\.[A-Za-z0-9_]+$")


def asset_to_file(content_root: Path, object_path: str) -> Path:
    if not isinstance(object_path,str) or not PATH_RE.fullmatch(object_path):
        raise ValueError("Invalid Unreal /Game/ object path")
    package,asset_name=object_path[6:].split(".",1)
    if package.split("/")[-1]!=asset_name:
        raise ValueError("Asset package name/object mismatch; review path manually")
    root=Path(content_root).resolve()
    candidate=(root/(package+".uasset")).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("Path escaped content root through symbolic link")
    return candidate


def evaluate_repo_assets(manifest: dict, content_root: Path) -> dict:
    if manifest.get("schema")!=EXPECTED_SCHEMA:
        raise ValueError("Unknown binding schema")
    assets=manifest.get("assets")
    if not isinstance(assets,list) or not assets:
        raise ValueError("Missing expected animation binding assets")
    roles=set();identifiers=set();paths=set();out=[]
    for item in assets:
        if not isinstance(item,dict):raise ValueError("Malformed asset entry")
        role=item.get("role");key=item.get("asset_id");obj=item.get("expected_unreal_object_path")
        if not isinstance(role,str) or not role or not isinstance(key,str) or not key:
            raise ValueError("Missing role or stable asset ID")
        if role in roles or key in identifiers or obj in paths:
            raise ValueError("Duplicate role, asset ID, or path")
        roles.add(role);identifiers.add(key);paths.add(obj)
        if item.get("expected_class")!="AnimMontage":
            raise ValueError("This W04 audit expects AnimMontage only")
        notifies=item.get("required_notify_classes")
        if not isinstance(notifies,list) or any(not isinstance(c,str) or not c for c in notifies):
            raise ValueError("Missing/invalid required notify class list")
        path=asset_to_file(content_root,obj)
        found=path.is_file()
        out.append({"role":role,"asset_id":key,"unreal_object_path":obj,
                    "repository_uasset_candidate_path":str(path),
                    "checked_in_uasset_file_present":found,
                    "editor_loaded_asset_validated":False,
                    "notify_classes_validated":False,
                    "required_notify_classes":notifies})
    missing=[r["role"] for r in out if not r["checked_in_uasset_file_present"]]
    return {"id":"ANIM-024-W04-ANIMATION-MANIFEST-GATE",
            "checked_in_file_scope_only":True,
            "expected_anim_montages":len(out),
            "present_file_candidates":len(out)-len(missing),
            "missing_checked_in_uassets":len(missing),
            "missing_roles":missing,
            "assets":out,
            "actual_unreal_load":"NOT_RUN",
            "montage_notify_runtime_test":"NOT_RUN",
            "production_ready":False,
            "merge_allowed":False,
            "warning":"No .uasset in source checkout is not proof it is absent from user's local Unreal Content directory. File presence alone would not prove playability.",
            "rollback":"Read-only analysis; no UE project assets were changed."}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--bindings",required=True,type=Path)
    p.add_argument("--content-root",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    a=p.parse_args()
    if a.output.exists():raise SystemExit("Refusing to overwrite prior report")
    manifest=json.loads(a.bindings.read_text(encoding="utf-8"))
    result=evaluate_repo_assets(manifest,a.content_root)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"expected":result["expected_anim_montages"],
                      "not_checked_in":result["missing_checked_in_uassets"],
                      "production_ready":False}))

if __name__=="__main__":
    main()
