"""Idempotent placement of NARIS villain gameplay actors into W04 blockout.

Run in Unreal Editor after naris_author_w04_production_blockout.py.
This does not create, claim, or bind production skeletal meshes.
"""
from __future__ import annotations

import json
from pathlib import Path
import unreal

BLOCKOUT_MAP = "/Game/NARIS/W04/Maps/W04_AshenForest_Blockout"
CM_PER_METER = 100.0


def find_actor(actors, label):
    for actor in actors.get_all_level_actors():
        if actor.get_actor_label() == label:
            return actor
    return None


def main():
    data_path = (
        Path(unreal.Paths.project_content_dir())
        / "NARIS" / "W04" / "Data" / "W04_VillainEncounterRoster.json"
    )
    roster = json.loads(data_path.read_text(encoding="utf-8"))
    if roster["developmentMap"] != BLOCKOUT_MAP:
        raise RuntimeError("Refusing to spawn villains in an unexpected map")

    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if not unreal.EditorAssetLibrary.does_asset_exist(BLOCKOUT_MAP):
        raise RuntimeError("W04 blockout missing. Author the blockout before placing enemies.")
    if not levels.load_level(BLOCKOUT_MAP):
        raise RuntimeError("Unable to load W04 blockout")
    cls = getattr(unreal, "NarisVillainCharacter", None)
    if cls is None:
        raise RuntimeError("Native NarisVillainCharacter unavailable. Build C++ editor first.")

    repo_root = Path(unreal.Paths.project_dir()).resolve().parents[1]
    level_data = json.loads(
        (repo_root / "NARIS_MASTER" / "09_WORLD" / "Ashen_Forest"
         / "LEVEL_LAYOUT.json").read_text(encoding="utf-8")
    )
    centers = {z["id"]: z["center"] for z in level_data["zones"]}

    result = {"schema": roster["schema"], "development_map": BLOCKOUT_MAP,
              "encounters": {}, "production_ready": False}
    for entry in roster["encounters"]:
        if entry["zone"] not in centers:
            raise RuntimeError(f"Unknown W04 zone: {entry['zone']}")
        center = centers[entry["zone"]]
        offset = entry["offset_m"]
        location = unreal.Vector(
            (center[0] + offset[0]) * CM_PER_METER,
            (center[1] + offset[1]) * CM_PER_METER,
            (center[2] + offset[2]) * CM_PER_METER,
        )
        actor = find_actor(actors, entry["label"])
        status = "updated"
        if actor is None:
            actor = actors.spawn_actor_from_class(cls, location, unreal.Rotator(0.0, 0.0, 0.0))
            if actor is None:
                raise RuntimeError(f"Failed to spawn {entry['label']}")
            actor.set_actor_label(entry["label"])
            status = "created"
        actor.set_actor_location(location, False, False)
        actor.set_editor_property("villain_id", entry["villain_id"])
        result["encounters"][entry["label"]] = {
            "status": status, "villain_id": entry["villain_id"],
            "zone": entry["zone"], "development_only": entry.get("development_only", False)
        }

    # Author development navigation bounds per active zone. Brush bounds are
    # measured after spawn so scaling is independent of default brush size.
    nav_class = getattr(unreal, "NavMeshBoundsVolume", None)
    nav_result = {}
    used_zones = {entry["zone"] for entry in roster["encounters"]}
    if nav_class is None:
        unreal.log_warning("NARIS: NavMeshBoundsVolume Python class unavailable")
    else:
        for zone in level_data["zones"]:
            if zone["id"] not in used_zones:
                continue
            nav_label = "BLOCKOUT_NAV_" + zone["id"]
            center = zone["center"]
            nav_location = unreal.Vector(
                center[0] * CM_PER_METER,
                center[1] * CM_PER_METER,
                center[2] * CM_PER_METER,
            )
            volume = find_actor(actors, nav_label)
            if volume is None:
                volume = actors.spawn_actor_from_class(
                    nav_class, nav_location, unreal.Rotator(0.0, 0.0, 0.0)
                )
                if volume is None:
                    raise RuntimeError("Failed to create navigation volume: " + nav_label)
                volume.set_actor_label(nav_label)
            volume.set_actor_location(nav_location, False, False)
            _, extent = volume.get_actor_bounds(False)
            target_extent = (
                zone["size"][0] * 50.0 + 1000.0,
                zone["size"][1] * 50.0 + 1000.0,
                1500.0,
            )
            if min(extent.x, extent.y, extent.z) <= 0.01:
                nav_result[nav_label] = "unverified_zero_brush"
                unreal.log_warning("NARIS: nav volume brush has zero extent: " + nav_label)
                continue
            scale = volume.get_actor_scale3d()
            volume.set_actor_scale3d(unreal.Vector(
                scale.x * target_extent[0] / extent.x,
                scale.y * target_extent[1] / extent.y,
                scale.z * target_extent[2] / extent.z,
            ))
            nav_result[nav_label] = "bounds_configured_requires_navigation_build"
    result["navigation_bounds"] = nav_result

    has_navmesh_volume = any(
        actor.get_class().get_name() == "NavMeshBoundsVolume"
        for actor in actors.get_all_level_actors()
    )
    result["navmesh_volume_found"] = has_navmesh_volume
    if not has_navmesh_volume:
        unreal.log_warning(
            "NARIS: Add a NavMeshBoundsVolume to each W04 encounter zone; "
            "AI will not navigate without a generated navmesh."
        )
    if not levels.save_current_level():
        raise RuntimeError("Could not save modified W04 blockout level")
    unreal.log("NARIS_W04_VILLAIN_AUTHORING="
               + json.dumps(result, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
