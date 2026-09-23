"""Author the W04 Ashen Forest production blockout from canonical layout data.

This creates /Game/NARIS/W04/Maps/W04_AshenForest_Blockout.
It is intentionally NOT the Shipping map. Zone geometry is labeled BLOCKOUT_*
so the strict Shipping map gate can never accept it accidentally.
"""
from __future__ import annotations

import json
from pathlib import Path
import unreal

MAP_PATH="/Game/NARIS/W04/Maps/W04_AshenForest_Blockout"
LAYOUT_RELATIVE=Path("NARIS_MASTER")/"09_WORLD"/"Ashen_Forest"/"LEVEL_LAYOUT.json"
CM_PER_METER=100.0


def repo_root() -> Path:
    return Path(unreal.Paths.project_dir()).resolve().parents[1]


def require_unreal_class(name: str):
    cls=getattr(unreal,name,None)
    if cls is None:
        raise RuntimeError(
            f"Required NARIS Unreal class is unavailable: {name}. "
            "Build the NARIS_W04 C++ module first."
        )
    return cls


def actor_by_label(subsystem,label: str):
    for actor in subsystem.get_all_level_actors():
        if actor.get_actor_label()==label:
            return actor
    return None


def ensure_actor(subsystem,actor_class,label,location,rotation=None):
    existing=actor_by_label(subsystem,label)
    if existing is not None:
        existing.set_actor_location(location,False,False)
        if rotation is not None:
            existing.set_actor_rotation(rotation,False)
        return existing,"updated"

    actor=subsystem.spawn_actor_from_class(
        actor_class,
        location,
        rotation or unreal.Rotator(0.0,0.0,0.0),
        transient=False,
    )
    if actor is None:
        raise RuntimeError(f"Could not spawn blockout actor: {label}")
    actor.set_actor_label(label)
    return actor,"created"


def ensure_level(levels):
    if unreal.EditorAssetLibrary.does_asset_exist(MAP_PATH):
        if not levels.load_level(MAP_PATH):
            raise RuntimeError(f"Could not load blockout level: {MAP_PATH}")
        return "loaded"
    if not levels.new_level(MAP_PATH,False):
        raise RuntimeError(f"Could not create blockout level: {MAP_PATH}")
    return "created"


def vector_from_center(center):
    return unreal.Vector(
        float(center[0])*CM_PER_METER,
        float(center[1])*CM_PER_METER,
        float(center[2])*CM_PER_METER,
    )


def main():
    layout_path=repo_root()/LAYOUT_RELATIVE
    layout=json.loads(layout_path.read_text(encoding="utf-8"))
    levels=unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    actors=unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    status=ensure_level(levels)

    cube=unreal.load_asset("/Engine/BasicShapes/Cube.Cube")
    if cube is None:
        raise RuntimeError("Engine cube asset unavailable")

    result={
        "schema":"naris.w04.production-blockout-authoring.v1",
        "map":MAP_PATH,
        "map_status":status,
        "production_ready":False,
        "shipping_allowed":False,
        "zones":{},
        "gameplay":{},
        "lighting":{},
    }

    # Six canonical zones from LEVEL_LAYOUT.json.
    for zone in layout.get("zones",[]):
        zone_id=zone["id"]
        center=vector_from_center(zone["center"])
        size=zone["size"]
        floor,label_status=ensure_actor(
            actors,
            unreal.StaticMeshActor,
            f"BLOCKOUT_ZONE_{zone_id}",
            unreal.Vector(center.x,center.y,center.z-25.0),
        )
        floor.get_editor_property("static_mesh_component").set_static_mesh(cube)
        # Engine cube is 1 meter; layout sizes are meters.
        floor.set_actor_scale3d(
            unreal.Vector(float(size[0]),float(size[1]),0.5)
        )
        marker,marker_status=ensure_actor(
            actors,
            unreal.TargetPoint,
            f"BLOCKOUT_MARKER_{zone_id}",
            unreal.Vector(center.x,center.y,center.z+100.0),
        )
        result["zones"][zone_id]={
            "floor":label_status,
            "marker":marker_status,
            "center_m":zone["center"],
            "size_m":zone["size"],
            "role":zone["role"],
        }

    zone_centers={
        z["id"]:vector_from_center(z["center"])
        for z in layout.get("zones",[])
    }

    placements=[
        ("PlayerStart",unreal.PlayerStart,"Z01_FOREST_ENTRANCE",(-100.0,0.0,120.0)),
        ("NARIS_Waystone_0001",require_unreal_class("NarisWaystone"),"Z01_FOREST_ENTRANCE",(0.0,0.0,80.0)),
        ("NARIS_MemoryCrystal_0001",require_unreal_class("NarisMemoryCrystal"),"Z02_BROKEN_SHRINE",(0.0,0.0,80.0)),
        ("NARIS_CelestialWolf_0001",require_unreal_class("CelestialWolf"),"Z04_WHISPER_LAKE",(0.0,0.0,100.0)),
        ("NARIS_AshGate_0001",require_unreal_class("NarisAshGate"),"Z05_ASH_GATE",(0.0,0.0,120.0)),
        ("NARIS_BoneBeastBoss_0001",require_unreal_class("BoneBeastBoss"),"Z06_BONE_BEAST_ARENA",(0.0,0.0,120.0)),
        ("NARIS_BossArenaController",require_unreal_class("NarisBossArenaController"),"Z06_BONE_BEAST_ARENA",(300.0,0.0,100.0)),
    ]

    for label,cls,zone_id,offset in placements:
        center=zone_centers[zone_id]
        loc=unreal.Vector(center.x+offset[0],center.y+offset[1],center.z+offset[2])
        actor,actor_status=ensure_actor(actors,cls,label,loc)
        result["gameplay"][label]={"status":actor_status,"zone":zone_id}

    boss=actor_by_label(actors,"NARIS_BoneBeastBoss_0001")
    arena=actor_by_label(actors,"NARIS_BossArenaController")
    if boss is not None and arena is not None:
        arena.set_editor_property("boss",boss)

    light_specs=[
        ("BLOCKOUT_DirectionalLight",unreal.DirectionalLight,unreal.Vector(0.0,0.0,50000.0),unreal.Rotator(-18.0,-32.0,0.0)),
        ("BLOCKOUT_SkyLight",unreal.SkyLight,unreal.Vector(0.0,0.0,30000.0),None),
        ("BLOCKOUT_ExponentialHeightFog",unreal.ExponentialHeightFog,unreal.Vector(0.0,0.0,0.0),None),
    ]
    for label,cls,loc,rot in light_specs:
        _,light_status=ensure_actor(actors,cls,label,loc,rot)
        result["lighting"][label]=light_status

    if not levels.save_current_level():
        raise RuntimeError("Could not save W04_AshenForest_Blockout")

    unreal.EditorAssetLibrary.save_directory(
        "/Game/NARIS/W04/Maps",
        only_if_is_dirty=False,
        recursive=True,
    )
    unreal.log(
        "NARIS_W04_PRODUCTION_BLOCKOUT="
        + json.dumps(result,ensure_ascii=False,sort_keys=True)
    )


if __name__=="__main__":
    main()
