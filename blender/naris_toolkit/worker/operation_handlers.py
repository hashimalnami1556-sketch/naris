"""CALL OF NARIS — explicit Blender Worker operation handlers.

Only named operations are exposed. This module never evaluates or executes
Python supplied through worker parameters.
"""

from __future__ import annotations

import os
from typing import Any

import bpy


def _event_result(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


def _asset_objects(asset_id: str | None) -> list[bpy.types.Object]:
    if not asset_id:
        obj = bpy.context.active_object
        return [obj] if obj else []
    matches = [o for o in bpy.data.objects if o.get("naris_asset_id") == asset_id]
    if not matches:
        obj = bpy.data.objects.get(asset_id)
        if obj:
            matches = [obj]
    return matches


def _require_asset(asset_id: str | None) -> list[bpy.types.Object]:
    objects = _asset_objects(asset_id)
    if not objects:
        raise RuntimeError(f"NARIS_ASSET_NOT_FOUND: {asset_id or '<active object>'}")
    return objects


def validate_asset(asset_id: str | None, parameters: dict[str, Any]) -> dict[str, Any]:
    objects = _require_asset(asset_id)
    required = ["naris_asset_id", "naris_category", "naris_export", "naris_version", "naris_engine_target"]
    findings: list[dict[str, Any]] = []
    mesh_objects = 0
    polygons = 0
    for obj in objects:
        missing = [key for key in required if not obj.get(key)]
        if obj.type == "MESH":
            mesh_objects += 1
            polygons += len(obj.data.polygons)
        findings.append({"object": obj.name, "missing_metadata": missing, "type": obj.type})
    errors = [f"{x['object']}: missing {', '.join(x['missing_metadata'])}" for x in findings if x["missing_metadata"]]
    return _event_result(assetId=asset_id, object_count=len(objects), mesh_objects=mesh_objects,
                         polygon_count=polygons, findings=findings, valid=not errors, errors=errors)


def build_asset(asset_id: str | None, parameters: dict[str, Any]) -> dict[str, Any]:
    objects = _require_asset(asset_id)
    category = str(parameters.get("category", "Environment"))
    export = str(parameters.get("export", "GLB,FBX"))
    engine = str(parameters.get("engine_target", "Unity 6"))
    version = str(parameters.get("version", "1.0"))
    for obj in objects:
        obj["naris_asset_id"] = asset_id or obj.get("naris_asset_id") or obj.name
        obj["naris_category"] = category
        obj["naris_export"] = export
        obj["naris_version"] = version
        obj["naris_engine_target"] = engine
        obj["naris_lod0"] = 1.0
        obj["naris_lod1"] = float(parameters.get("lod1", 0.60))
        obj["naris_lod2"] = float(parameters.get("lod2", 0.30))
        obj["naris_collision"] = f"{obj.name}_COL"
    return _event_result(assetId=asset_id, object_count=len(objects), metadata_updated=True)


def generate_lod(asset_id: str | None, parameters: dict[str, Any]) -> dict[str, Any]:
    objects = [o for o in _require_asset(asset_id) if o.type == "MESH"]
    ratios = parameters.get("ratios", [1.0, 0.5, 0.25, 0.1])
    created: list[str] = []
    for obj in objects:
        for index, ratio in enumerate(ratios[1:], start=1):
            name = f"{obj.name}_LOD{index}"
            if bpy.data.objects.get(name):
                continue
            dup = obj.copy()
            dup.data = obj.data.copy()
            dup.name = name
            bpy.context.collection.objects.link(dup)
            mod = dup.modifiers.new(f"NARIS_LOD{index}", "DECIMATE")
            mod.ratio = max(0.001, min(1.0, float(ratio)))
            bpy.context.view_layer.objects.active = dup
            dup.select_set(True)
            try:
                bpy.ops.object.modifier_apply(modifier=mod.name)
            finally:
                dup.select_set(False)
            dup["naris_asset_id"] = asset_id
            dup["naris_lod_level"] = index
            created.append(name)
    return _event_result(assetId=asset_id, ratios=ratios, created=created, count=len(created))


def generate_collision(asset_id: str | None, parameters: dict[str, Any]) -> dict[str, Any]:
    objects = [o for o in _require_asset(asset_id) if o.type == "MESH"]
    mode = str(parameters.get("mode", "CONVEX")).upper()
    created: list[str] = []
    for obj in objects:
        name = f"{obj.name}_COL"
        old = bpy.data.objects.get(name)
        if old:
            bpy.data.objects.remove(old, do_unlink=True)
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)
        try:
            bpy.ops.object.duplicate()
            col = bpy.context.object
            col.name = name
            col.data = obj.data.copy()
            col["naris_collision"] = True
            col["naris_collision_mode"] = mode
            for poly in col.data.polygons:
                poly.use_smooth = False
            if mode in {"BOX", "CAPSULE"}:
                bpy.ops.object.modifier_add(type="DECIMATE")
                bpy.context.object.modifiers[-1].ratio = 0.1
            created.append(name)
        finally:
            obj.select_set(False)
    return _event_result(assetId=asset_id, mode=mode, created=created, count=len(created))


def process_textures(asset_id: str | None, parameters: dict[str, Any]) -> dict[str, Any]:
    objects = _require_asset(asset_id)
    resolution = int(parameters.get("resolution", 4096))
    materials = []
    for obj in objects:
        for slot in obj.material_slots:
            if slot.material and slot.material.name not in materials:
                materials.append(slot.material.name)
    return _event_result(assetId=asset_id, resolution=resolution, materials=materials,
                         processed=False, note="Texture processing contract validated; image transforms require explicit source paths.")


def render_preview(asset_id: str | None, parameters: dict[str, Any]) -> dict[str, Any]:
    _require_asset(asset_id)
    filepath = str(parameters.get("filepath", os.path.join("generated", "previews", f"{asset_id or 'preview'}.png")))
    if not os.path.isabs(filepath):
        filepath = os.path.abspath(filepath)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    scene = bpy.context.scene
    scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)
    return _event_result(assetId=asset_id, filepath=filepath, rendered=True)


def export_asset(asset_id: str | None, parameters: dict[str, Any]) -> dict[str, Any]:
    objects = _require_asset(asset_id)
    fmt = str(parameters.get("format", "glb")).lower()
    filepath = parameters.get("filepath")
    if not filepath:
        filepath = os.path.abspath(os.path.join("generated", "exports", f"{asset_id or 'asset'}.{fmt}"))
    filepath = os.path.abspath(str(filepath))
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    try:
        if fmt in {"glb", "gltf"}:
            bpy.ops.wm.gltf_export(filepath=filepath, export_format=fmt)
        elif fmt == "fbx":
            bpy.ops.export_scene.fbx(filepath=filepath, use_selection=True)
        elif fmt == "obj":
            bpy.ops.wm.obj_export(filepath=filepath, export_selected_objects=True)
        else:
            raise RuntimeError(f"NARIS_EXPORT_FORMAT_UNSUPPORTED: {fmt}")
    finally:
        for obj in objects:
            obj.select_set(False)
    if not os.path.exists(filepath):
        raise RuntimeError(f"NARIS_EXPORT_ARTIFACT_MISSING: {filepath}")
    return _event_result(assetId=asset_id, format=fmt, filepath=filepath, exported=True,
                         size_bytes=os.path.getsize(filepath))


HANDLERS = {
    "VALIDATE_ASSET": validate_asset,
    "BUILD_ASSET": build_asset,
    "GENERATE_LOD": generate_lod,
    "GENERATE_COLLISION": generate_collision,
    "PROCESS_TEXTURES": process_textures,
    "RENDER_PREVIEW": render_preview,
    "EXPORT_ASSET": export_asset,
}
