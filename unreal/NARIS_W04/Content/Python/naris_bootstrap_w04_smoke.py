"""Create the W04 Unreal runtime-smoke map and minimum authored assets.

This is an editor bootstrap, not the final Ashen Forest production level.
It creates /Game/NARIS/W04/Maps/W04_Prototype because DefaultEngine.ini already
targets that path. The layout is deterministic and intentionally simple so the
Windows build/playtest can validate progression before final level art exists.
"""
from __future__ import annotations

import json
import unreal

MAP_PATH = "/Game/NARIS/W04/Maps/W04_Prototype"
DATA_DIR = "/Game/NARIS/W04/Data"
BOSS_DATA_PATH = DATA_DIR + "/DA_BoneBeast_Smoke"


def require_unreal_class(name: str):
    cls = getattr(unreal, name, None)
    if cls is None:
        raise RuntimeError(
            f"Required NARIS Unreal class is unavailable: {name}. "
            "Build the NARIS_W04 C++ module before running this bootstrap."
        )
    return cls


def ensure_level(level_subsystem):
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        if not level_subsystem.load_level(MAP_PATH):
            raise RuntimeError(f"Could not load existing W04 map: {MAP_PATH}")
        return "loaded"

    if not level_subsystem.new_level(MAP_PATH, False):
        raise RuntimeError(f"Could not create W04 map: {MAP_PATH}")
    return "created"


def ensure_boss_data(asset_tools):
    if unreal.EditorAssetLibrary.does_asset_exist(BOSS_DATA_PATH):
        asset = unreal.load_asset(BOSS_DATA_PATH)
        if asset is None:
            raise RuntimeError(f"Could not load boss data asset: {BOSS_DATA_PATH}")
        return asset, "loaded"

    boss_data_class = require_unreal_class("BoneBeastDataAsset")
    factory = unreal.DataAssetFactory()
    factory.set_editor_property("data_asset_class", boss_data_class)
    asset = asset_tools.create_asset(
        asset_name="DA_BoneBeast_Smoke",
        package_path=DATA_DIR,
        asset_class=boss_data_class,
        factory=factory,
    )
    if asset is None:
        raise RuntimeError("Could not create DA_BoneBeast_Smoke")

    # Smoke-only values. These are not production tuning.
    asset.set_editor_property("boss_id", unreal.Name("BoneBeast"))
    asset.set_editor_property("max_health", 100.0)
    asset.set_editor_property(
        "quest_completion_id",
        unreal.Name("Quest.W04.CorruptedHeart"),
    )
    unreal.EditorAssetLibrary.save_directory(
        DATA_DIR,
        only_if_is_dirty=False,
        recursive=True,
    )
    return asset, "created"


def actor_by_label(editor_actor_subsystem, label: str):
    for actor in editor_actor_subsystem.get_all_level_actors():
        if actor.get_actor_label() == label:
            return actor
    return None


def ensure_actor(editor_actor_subsystem, actor_class, label, location, rotation=None):
    existing = actor_by_label(editor_actor_subsystem, label)
    if existing is not None:
        return existing, "loaded"

    actor = editor_actor_subsystem.spawn_actor_from_class(
        actor_class,
        location,
        rotation or unreal.Rotator(0.0, 0.0, 0.0),
        transient=False,
    )
    if actor is None:
        raise RuntimeError(f"Could not spawn actor: {label}")
    actor.set_actor_label(label)
    return actor, "created"


def ensure_smoke_floor(editor_actor_subsystem):
    floor, status = ensure_actor(
        editor_actor_subsystem,
        unreal.StaticMeshActor,
        "DEV_SmokeFloor",
        unreal.Vector(1400.0, 0.0, -50.0),
    )
    mesh = unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if mesh is None:
        raise RuntimeError("Could not load /Engine/BasicShapes/Cube.Cube")

    component = floor.get_editor_property("static_mesh_component")
    component.set_static_mesh(mesh)
    floor.set_actor_scale3d(unreal.Vector(36.0, 12.0, 1.0))
    return status


def main():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()

    level_status = ensure_level(level_subsystem)
    boss_data, boss_data_status = ensure_boss_data(asset_tools)

    results = {
        "map": {"path": MAP_PATH, "status": level_status},
        "boss_data": {"path": BOSS_DATA_PATH, "status": boss_data_status},
        "actors": {},
        "smoke_only": True,
    }

    results["actors"]["floor"] = ensure_smoke_floor(actor_subsystem)

    placements = [
        ("PlayerStart", unreal.PlayerStart, unreal.Vector(-400.0, 0.0, 100.0)),
        (
            "NARIS_Waystone_0001",
            require_unreal_class("NarisWaystone"),
            unreal.Vector(0.0, 0.0, 50.0),
        ),
        (
            "NARIS_MemoryCrystal_0001",
            require_unreal_class("NarisMemoryCrystal"),
            unreal.Vector(600.0, 0.0, 50.0),
        ),
        (
            "NARIS_AshGate_0001",
            require_unreal_class("NarisAshGate"),
            unreal.Vector(1200.0, 0.0, 100.0),
        ),
        (
            "NARIS_CelestialWolf_0001",
            require_unreal_class("CelestialWolf"),
            unreal.Vector(1800.0, 0.0, 100.0),
        ),
        (
            "NARIS_BoneBeastBoss_0001",
            require_unreal_class("BoneBeastBoss"),
            unreal.Vector(3000.0, 0.0, 100.0),
        ),
        (
            "NARIS_RuntimeSmokeDirector",
            require_unreal_class("NarisRuntimeSmokeDirector"),
            unreal.Vector(-800.0, 400.0, 100.0),
        ),
    ]

    for label, actor_class, location in placements:
        actor, status = ensure_actor(
            actor_subsystem,
            actor_class,
            label,
            location,
        )
        results["actors"][label] = status
        if label == "NARIS_BoneBeastBoss_0001":
            actor.set_editor_property("boss_data", boss_data)

    # Basic editor lighting for smoke verification only.
    _, results["actors"]["DirectionalLight"] = ensure_actor(
        actor_subsystem,
        unreal.DirectionalLight,
        "DEV_DirectionalLight",
        unreal.Vector(0.0, 0.0, 600.0),
        unreal.Rotator(-45.0, -35.0, 0.0),
    )
    _, results["actors"]["SkyLight"] = ensure_actor(
        actor_subsystem,
        unreal.SkyLight,
        "DEV_SkyLight",
        unreal.Vector(0.0, 0.0, 500.0),
    )

    if not level_subsystem.save_current_level():
        raise RuntimeError("Could not save W04_Prototype")

    unreal.EditorAssetLibrary.save_directory(
        "/Game/NARIS/W04",
        only_if_is_dirty=False,
        recursive=True,
    )

    unreal.log(
        "NARIS_W04_BOOTSTRAP_RESULT="
        + json.dumps(results, ensure_ascii=False, sort_keys=True)
    )


if __name__ == "__main__":
    main()
