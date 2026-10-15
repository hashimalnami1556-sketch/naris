"""NARIS: validate and convert a skinned/animated GLB into Unreal-friendly FBX.

Run with Blender:
    blender -b -P tools/blender/export_naris_fiery_demon.py -- \
        --input D:/NARIS/Assets/NARIS_Fiery_Demon_COMBAT_PROXY_Rigged.glb \
        --output D:/NARIS/Build/FieryDemon.fbx \
        --report D:/NARIS/Build/fiery_demon_blender.json

An optional environment is exported with --static and no armature required.
This program validates Blender input and writes a provenance report. An FBX
passing validation here is not proof of successful Unreal import/playback.
"""
import argparse
import json
from pathlib import Path
import sys

import bpy


def parse_args():
    script_args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", dest="source", required=True)
    parser.add_argument("--output", dest="destination", required=True)
    parser.add_argument("--report", default="")
    parser.add_argument("--static", action="store_true")
    parser.add_argument("--min-actions", type=int, default=1)
    return parser.parse_args(script_args)


def convert(args):
    source = Path(args.source).expanduser().resolve()
    destination = Path(args.destination).expanduser().resolve()
    if not source.is_file() or source.suffix.lower() not in {".glb", ".gltf"}:
        raise FileNotFoundError(f"Missing source glTF/GLB: {source}")
    if args.min_actions < 0:
        raise ValueError("--min-actions must be nonnegative")
    if destination == source:
        raise ValueError("Destination must differ from source")

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(source))

    armatures = [obj for obj in bpy.data.objects if obj.type == "ARMATURE"]
    meshes = [obj for obj in bpy.data.objects if obj.type == "MESH"]
    actions = list(bpy.data.actions)

    if not meshes:
        raise RuntimeError("No MESH geometry imported; FBX refused")
    if not args.static:
        if len(armatures) != 1:
            raise RuntimeError(f"Expected 1 ARMATURE, found {len(armatures)}")
        rig = armatures[0]
        if len(rig.data.bones) < 15:
            raise RuntimeError(f"Rig has only {len(rig.data.bones)} bones (min 15)")
        for obj in meshes:
            if not obj.vertex_groups or not any(
                mod.type == "ARMATURE" for mod in obj.modifiers
            ):
                raise RuntimeError(f"Skinned MESH missing vertex groups/rig: {obj.name}")
        if len(actions) < args.min_actions:
            raise RuntimeError(
                f"Expected >={args.min_actions} animation actions, found {len(actions)}"
            )

    bpy.ops.object.select_all(action="DESELECT")
    selected = meshes if args.static else meshes + armatures
    for obj in selected:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = armatures[0] if armatures and not args.static else meshes[0]
    destination.parent.mkdir(parents=True, exist_ok=True)

    bpy.ops.export_scene.fbx(
        filepath=str(destination),
        use_selection=True,
        object_types={"ARMATURE", "MESH"},
        add_leaf_bones=False,
        apply_unit_scale=True,
        axis_forward="-Z",
        axis_up="Y",
        bake_anim=not args.static,
        bake_anim_use_all_actions=True,
        path_mode="COPY",
    )
    if not destination.is_file() or destination.stat().st_size < 4096:
        raise RuntimeError(f"FBX was not produced or is unexpectedly small: {destination}")

    report = {
        "status": "fbx_exported_unreal_import_unverified",
        "source": str(source),
        "destination": str(destination),
        "static": bool(args.static),
        "mesh_count": len(meshes),
        "skinned_bones": len(armatures[0].data.bones) if armatures else 0,
        "action_count": len(actions) if not args.static else 0,
        "action_names": sorted(action.name for action in actions) if not args.static else [],
        "fbx_bytes": destination.stat().st_size,
        "unreal_imported": False,
        "pie_tested": False,
    }
    if args.report:
        out = Path(args.report).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("[NARIS_FIERY_DEMON] " + json.dumps(report, ensure_ascii=False))
    return report


if __name__ == "__main__":
    convert(parse_args())
