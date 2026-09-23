"""Validate core W04 production meshes inside Unreal Editor.

Development reports unresolved assets. NARIS_PRODUCTION_ASSETS_STRICT=1 turns
missing/invalid core assets into a Shipping blocker.
"""
from __future__ import annotations
import json, os
from pathlib import Path
import unreal

RELATIVE = Path("NARIS")/"W04"/"Production"/"W04_ProductionAssetBindings.json"

def strict_mode():
    return os.environ.get("NARIS_PRODUCTION_ASSETS_STRICT","").strip().lower() in {"1","true","yes","on"}

def material_count(asset, kind):
    prop = "materials" if kind == "skeletal_mesh" else "static_materials"
    mats = list(asset.get_editor_property(prop))
    count = 0
    for mat in mats:
        try:
            iface = mat.get_editor_property("material_interface")
        except Exception:
            iface = None
        if iface is not None:
            count += 1
    return count

def main():
    path = Path(unreal.Paths.project_content_dir()) / RELATIVE
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != "naris.w04.production-assets.v1":
        raise RuntimeError("Unsupported production asset schema")

    registry = json.loads(
        (Path(unreal.Paths.project_dir()).parents[1] / "data" / "MASTER_ASSET_REGISTRY.json").read_text(encoding="utf-8")
    )
    registry_ids = {a.get("id") for a in registry.get("assets",[]) if isinstance(a,dict)}

    static_subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
    skeletal_subsystem = unreal.get_editor_subsystem(unreal.SkeletalMeshEditorSubsystem)
    unresolved=[]; validated=[]; errors=[]; details={}

    for item in data.get("assets",[]):
        aid=item.get("asset_id"); object_path=item.get("expected_unreal_object_path"); kind=item.get("kind")
        if aid not in registry_ids:
            errors.append(f"{aid}: not present in MASTER_ASSET_REGISTRY")
            continue
        if not unreal.EditorAssetLibrary.does_asset_exist(object_path):
            unresolved.append(aid); continue

        asset=unreal.load_asset(object_path)
        if kind=="skeletal_mesh":
            if not isinstance(asset, unreal.SkeletalMesh):
                errors.append(f"{aid}: expected SkeletalMesh"); continue
            lods=skeletal_subsystem.get_lod_count(asset)
            skeleton=asset.get_editor_property("skeleton")
            physics=asset.get_editor_property("physics_asset")
            mats=material_count(asset,kind)
            if lods < int(item.get("min_lods",1)): errors.append(f"{aid}: LOD count {lods} below minimum")
            if item.get("require_skeleton") and skeleton is None: errors.append(f"{aid}: missing Skeleton")
            if item.get("require_physics_asset") and physics is None: errors.append(f"{aid}: missing PhysicsAsset")
            if item.get("require_materials") and mats < 1: errors.append(f"{aid}: no assigned materials")
            details[aid]={"lod_count":lods,"material_count":mats,"has_skeleton":skeleton is not None,"has_physics_asset":physics is not None}
        elif kind=="static_mesh":
            if not isinstance(asset, unreal.StaticMesh):
                errors.append(f"{aid}: expected StaticMesh"); continue
            lods=asset.get_num_lods()
            mats=material_count(asset,kind)
            convex=static_subsystem.get_convex_collision_count(asset)
            customized=bool(asset.get_editor_property("customized_collision"))
            if lods < int(item.get("min_lods",1)): errors.append(f"{aid}: LOD count {lods} below minimum")
            if item.get("require_materials") and mats < 1: errors.append(f"{aid}: no assigned materials")
            if item.get("require_collision") and convex <= 0 and not customized:
                errors.append(f"{aid}: no authored/simple collision evidence")
            details[aid]={"lod_count":lods,"material_count":mats,"convex_collision_count":convex,"customized_collision":customized}
        else:
            errors.append(f"{aid}: unsupported kind {kind!r}"); continue

        if not any(e.startswith(f"{aid}:") for e in errors):
            validated.append(aid)

    report={"schema":"naris.w04.production-asset-validation.v1","status":"fail" if errors or (strict_mode() and unresolved) else "pass","strict":strict_mode(),"validated_asset_ids":sorted(validated),"unresolved_asset_ids":sorted(unresolved),"details":details,"errors":errors}
    out=Path(unreal.Paths.project_saved_dir())/"TestReports"; out.mkdir(parents=True,exist_ok=True)
    (out/"naris_production_asset_validation.json").write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    unreal.log("NARIS_PRODUCTION_ASSET_VALIDATION="+json.dumps(report,ensure_ascii=False,sort_keys=True))
    if errors: raise RuntimeError("Production asset validation found invalid assets")
    if strict_mode() and unresolved: raise RuntimeError(f"Strict production asset validation has {len(unresolved)} unresolved assets")

if __name__=="__main__":
    main()
