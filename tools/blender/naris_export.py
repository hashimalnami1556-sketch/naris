"""NARIS Blender validation/export helper.

Run inside Blender:
  blender --background asset.blend --python tools/blender/naris_export.py -- --out <dir>

The script validates selected mesh/armature objects and exports deterministic FBX/glTF
exchange files plus a JSON manifest. It does not modify source geometry.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import bpy

ASSET_ID = re.compile(r"^NARIS-W\d{2}-(CHR|ENM|BOS|WPN|PRP|ENV|MAT|VFX|UI|MAP|CINE|AUD|QST)-[A-Z0-9_]+-\d{4}$")
ALLOWED_TYPES = {"MESH", "ARMATURE", "EMPTY"}
EPS = 1e-4


def parse_args() -> argparse.Namespace:
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :] if "--" in argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--asset-id", default="")
    p.add_argument("--no-fbx", action="store_true")
    p.add_argument("--no-gltf", action="store_true")
    return p.parse_args(argv)


def near(a: float, b: float) -> bool:
    return abs(a - b) <= EPS


def validate_object(obj: bpy.types.Object) -> list[str]:
    issues: list[str] = []
    if obj.type not in ALLOWED_TYPES:
        issues.append(f"{obj.name}: unsupported type {obj.type}")
        return issues

    if obj.type == "MESH":
        if not obj.data.polygons:
            issues.append(f"{obj.name}: mesh has no polygons")
        if len(obj.data.uv_layers) == 0:
            issues.append(f"{obj.name}: mesh has no UV map")

    if not all(near(v, 1.0) for v in obj.scale):
        issues.append(f"{obj.name}: unapplied/non-unit scale {tuple(round(v, 5) for v in obj.scale)}")

    if any(abs(v) > EPS for v in obj.rotation_euler):
        issues.append(f"{obj.name}: non-zero Euler rotation; apply transforms before final export")

    if obj.name.startswith("UCX_") and obj.type != "MESH":
        issues.append(f"{obj.name}: UCX collision helper must be a mesh")

    return issues


def collect_manifest(asset_id: str, objects: list[bpy.types.Object], issues: list[str]) -> dict:
    return {
        "schema": "naris.blender.exchange.v1",
        "asset_id": asset_id,
        "blend_file": bpy.data.filepath,
        "objects": [
            {
                "name": o.name,
                "type": o.type,
                "location": [round(v, 6) for v in o.location],
                "rotation_euler": [round(v, 6) for v in o.rotation_euler],
                "scale": [round(v, 6) for v in o.scale],
                "materials": [m.name for m in o.data.materials] if o.type == "MESH" else [],
                "uv_layers": [u.name for u in o.data.uv_layers] if o.type == "MESH" else [],
            }
            for o in objects
        ],
        "issues": issues,
        "status": "pass" if not issues else "fail",
    }


def main() -> int:
    args = parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    selected = [o for o in bpy.context.selected_objects if o.type in ALLOWED_TYPES]
    if not selected:
        selected = [o for o in bpy.context.scene.objects if o.type in ALLOWED_TYPES]

    asset_id = args.asset_id.strip() or (selected[0].name if selected else "")
    issues: list[str] = []
    if not ASSET_ID.match(asset_id):
        issues.append(
            "Asset ID must follow NARIS-W<world>-<domain>-<TYPE>-<sequence>; "
            f"received: {asset_id!r}"
        )

    for obj in selected:
        issues.extend(validate_object(obj))

    manifest = collect_manifest(asset_id, selected, issues)
    manifest_path = out / f"{asset_id or 'UNNAMED'}_blender_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    if issues:
        print(json.dumps(manifest, indent=2))
        return 2

    for o in bpy.context.selected_objects:
        o.select_set(False)
    for o in selected:
        o.select_set(True)
    if selected:
        bpy.context.view_layer.objects.active = selected[0]

    if not args.no_fbx:
        bpy.ops.export_scene.fbx(
            filepath=str(out / f"{asset_id}.fbx"),
            use_selection=True,
            apply_unit_scale=True,
            apply_scale_options="FBX_SCALE_UNITS",
            axis_forward="-Y",
            axis_up="Z",
            add_leaf_bones=False,
            bake_anim=True,
        )

    if not args.no_gltf:
        bpy.ops.export_scene.gltf(
            filepath=str(out / f"{asset_id}.glb"),
            export_format="GLB",
            use_selection=True,
            export_apply=True,
            export_yup=True,
        )

    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
