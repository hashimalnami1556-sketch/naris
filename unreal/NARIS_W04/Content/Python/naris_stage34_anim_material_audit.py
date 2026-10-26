"""UE5.7 editor-side asset inspection. Never modifies production maps.
Run with UnrealEditor-Cmd.exe <uproject> -run=pythonscript -script=<this file>.
"""
import json
from pathlib import Path
import unreal

ASSET_ROOTS = ["/Game/NARIS", "/Game/NARIS/_Import"]
OUT = Path(unreal.Paths.project_saved_dir()) / "TestReports" / "naris_stage34_anim_material_audit.json"

def inspect():
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    findings = {"skeletal_meshes": [], "animation_sequences": [], "montages": [],
                "animation_blueprints": [], "materials": [], "textures": [], "missing": [],
                "status": "audit_only"}
    for root in ASSET_ROOTS:
        for asset in registry.get_assets_by_path(unreal.Name(root), recursive=True):
            name = str(asset.asset_name)
            cls = str(asset.asset_class_path.asset_name)
            record = {"name": name, "path": str(asset.package_name), "class": cls}
            if cls == "SkeletalMesh":
                findings["skeletal_meshes"].append(record)
            elif cls == "AnimSequence":
                findings["animation_sequences"].append(record)
            elif cls == "AnimMontage":
                findings["montages"].append(record)
            elif cls == "AnimBlueprint":
                findings["animation_blueprints"].append(record)
            elif cls in ("Material", "MaterialInstanceConstant"):
                findings["materials"].append(record)
            elif cls == "Texture2D":
                findings["textures"].append(record)
    if not findings["animation_blueprints"]:
        findings["missing"].append("AnimBlueprint not found under /Game/NARIS")
    if not findings["montages"]:
        findings["missing"].append("AnimMontage not found under /Game/NARIS")
    if not findings["skeletal_meshes"]:
        findings["missing"].append("SkeletalMesh not found under /Game/NARIS")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(findings, indent=2, ensure_ascii=False), encoding="utf-8")
    unreal.log("Stage34 audit written: " + str(OUT))
    if findings["missing"]:
        raise RuntimeError("Stage34 animation readiness BLOCKED: " + "; ".join(findings["missing"]))
inspect()
