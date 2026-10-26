"""Strictly validate the production W04 Ashen Forest map for Shipping.

Development continues to use W04_Prototype. Shipping reads the production map
requirements contract and rejects smoke/blockout content or missing world gates.
"""
from __future__ import annotations
import json
from pathlib import Path
import unreal
from naris_shipping_map_rules import evaluate_snapshot

REQUIREMENTS_RELATIVE = (
    Path("NARIS") / "W04" / "Maps" / "W04_ProductionMapRequirements.json"
)

def collect_snapshot(requirements):
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    names = set(requirements.get("required_actor_classes", []))
    names.update(requirements.get("required_actor_label_classes", {}).values())
    result = []
    for actor in actors.get_all_level_actors():
        class_names = {actor.get_class().get_name()}
        for name in names:
            cls = getattr(unreal, name, None)
            if cls is not None and isinstance(actor, cls):
                class_names.add(name)
        paths = []
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            mesh = component.get_editor_property("static_mesh")
            if mesh is not None:
                paths.append(mesh.get_path_name())
        result.append({"label": actor.get_actor_label(), "class_names": sorted(class_names), "static_mesh_paths": paths})
    return result


def main():
    content_dir = Path(unreal.Paths.project_content_dir())
    requirements_path = content_dir / REQUIREMENTS_RELATIVE
    if not requirements_path.is_file():
        raise RuntimeError(f"Production map requirements missing: {requirements_path}")

    requirements = json.loads(requirements_path.read_text(encoding="utf-8"))
    if requirements.get("schema") != "naris.w04.production-map-requirements.v1":
        raise RuntimeError("Unsupported W04 production map requirements schema")

    production_map = requirements["production_map"]
    required_labels = set(requirements.get("required_actor_labels", []))
    required_labels.update(
        zone["label"]
        for zone in requirements.get("zones", [])
        if isinstance(zone, dict) and zone.get("label")
    )
    forbidden_labels = set(requirements.get("forbidden_actor_labels", []))
    forbidden_prefixes = tuple(requirements.get("forbidden_label_prefixes", []))
    required_classes = set(requirements.get("required_actor_classes", []))

    report = {
        "schema": "naris.w04.shipping-map-validation.v1",
        "status": "fail",
        "production_map": production_map,
        "required_labels": sorted(required_labels),
        "missing_labels": [],
        "required_actor_classes": sorted(required_classes),
        "missing_actor_classes": [],
        "forbidden_labels_found": [],
        "forbidden_prefix_labels_found": [],
        "errors": [],
    }

    if not unreal.EditorAssetLibrary.does_asset_exist(production_map):
        report["errors"].append(f"Production map missing: {production_map}")
    else:
        levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
        if levels.is_in_play_in_editor() or unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
            report["errors"].append("Unsaved map or active PIE preserved; stop and save before validation")
        elif not levels.load_level(production_map):
            report["errors"].append(f"Could not load production map: {production_map}")
        else:
            report.update(evaluate_snapshot(requirements, collect_snapshot(requirements)))
            if report["forbidden_labels_found"] or report["forbidden_prefix_labels_found"]:
                report["errors"].append("Development/smoke/blockout actors exist in production map")

    if not report["errors"]:
        report["status"] = "pass"

    out = Path(unreal.Paths.project_saved_dir()) / "TestReports"
    out.mkdir(parents=True, exist_ok=True)
    path = out / "naris_shipping_map_validation.json"
    path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    unreal.log(
        "NARIS_SHIPPING_MAP_VALIDATION="
        + json.dumps(report, ensure_ascii=False, sort_keys=True)
    )
    if report["status"] != "pass":
        raise RuntimeError("W04 production shipping map validation failed")

if __name__ == "__main__":
    main()
