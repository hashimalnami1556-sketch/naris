"""Strictly validate the production W04 Ashen Forest map for Shipping.

Development continues to use W04_Prototype. Shipping must use W04_AshenForest
and must not contain smoke/dev-only actors.
"""
from __future__ import annotations
import json
from pathlib import Path
import unreal

PRODUCTION_MAP="/Game/NARIS/W04/Maps/W04_AshenForest"
REQUIRED_LABELS={
    "PlayerStart",
    "NARIS_Waystone_0001",
    "NARIS_MemoryCrystal_0001",
    "NARIS_AshGate_0001",
    "NARIS_CelestialWolf_0001",
    "NARIS_BoneBeastBoss_0001",
    "NARIS_BossArenaController",
}
FORBIDDEN_LABELS={"NARIS_RuntimeSmokeDirector"}
FORBIDDEN_PREFIXES=("DEV_",)

def main():
    report={
        "schema":"naris.w04.shipping-map-validation.v1",
        "status":"fail",
        "production_map":PRODUCTION_MAP,
        "required_labels":sorted(REQUIRED_LABELS),
        "missing_labels":[],
        "forbidden_labels_found":[],
        "forbidden_prefix_labels_found":[],
        "errors":[],
    }

    if not unreal.EditorAssetLibrary.does_asset_exist(PRODUCTION_MAP):
        report["errors"].append(f"Production map missing: {PRODUCTION_MAP}")
    else:
        levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        if not levels.load_level(PRODUCTION_MAP):
            report["errors"].append(f"Could not load production map: {PRODUCTION_MAP}")
        else:
            labels={a.get_actor_label() for a in actors.get_all_level_actors()}
            report["missing_labels"]=sorted(REQUIRED_LABELS-labels)
            report["forbidden_labels_found"]=sorted(FORBIDDEN_LABELS & labels)
            report["forbidden_prefix_labels_found"]=sorted(
                label for label in labels
                if any(label.startswith(prefix) for prefix in FORBIDDEN_PREFIXES)
            )
            if report["missing_labels"]:
                report["errors"].append("Required production actors are missing")
            if report["forbidden_labels_found"] or report["forbidden_prefix_labels_found"]:
                report["errors"].append("Development/smoke actors exist in production map")

    if not report["errors"]:
        report["status"]="pass"

    out=Path(unreal.Paths.project_saved_dir())/"TestReports"
    out.mkdir(parents=True,exist_ok=True)
    path=out/"naris_shipping_map_validation.json"
    path.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
    unreal.log("NARIS_SHIPPING_MAP_VALIDATION="+json.dumps(report,ensure_ascii=False,sort_keys=True))
    if report["status"]!="pass":
        raise RuntimeError("W04 production shipping map validation failed")

if __name__=="__main__":
    main()
