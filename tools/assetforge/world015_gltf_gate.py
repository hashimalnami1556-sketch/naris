"""WORLD-015 source-geometry gate for real glTF2/GLB terrain tiles.

This module is pure stdlib so it runs in GitHub Actions and the UE host's Python.
It validates GLB binary structure and signed Y-up altitude bounds; it does NOT
claim that the GLB has been imported correctly by Unreal. That check happens
inside the external Work015 editor-authoring package before any actor placement.
"""
import json
import math
from pathlib import Path
import struct


def inspect_terrain_glb(path):
    data = Path(path).read_bytes()
    if len(data) < 28 or data[:4] != b"glTF":
        raise ValueError("GLB magic or length invalid")
    version, byte_count = struct.unpack_from("<II", data, 4)
    if version != 2 or byte_count != len(data):
        raise ValueError("GLB version/byte count inconsistent")
    json_len, chunk_type = struct.unpack_from("<I4s", data, 12)
    if chunk_type != b"JSON" or not (0 < json_len <= len(data) - 20):
        raise ValueError("glTF JSON chunk invalid")
    gltf = json.loads(data[20:20 + json_len].decode("utf-8"))
    meshes = gltf.get("meshes", [])
    if len(meshes) != 1 or len(meshes[0].get("primitives", [])) != 1:
        raise ValueError("expected one terrain mesh")
    primitive = meshes[0]["primitives"][0]
    if primitive.get("mode", 4) != 4:
        raise ValueError("non-triangle topology")
    accessors = gltf["accessors"]
    pos = accessors[primitive["attributes"]["POSITION"]]
    indices = accessors[primitive["indices"]]
    if pos["type"] != "VEC3" or indices["type"] != "SCALAR":
        raise ValueError("invalid accessor types")
    low, high = pos["min"], pos["max"]
    if len(low) != 3 or len(high) != 3:
        raise ValueError("position accessor missing 3D bounds")
    if not all(math.isfinite(float(v)) for v in low + high):
        raise ValueError("nonfinite vertex bounds")
    if indices["count"] <= 0 or indices["count"] % 3:
        raise ValueError("invalid triangle count")
    return {"triangles": indices["count"] // 3,
            "width_m": high[0] - low[0],
            "depth_m": high[2] - low[2],
            "height_min_m": low[1],
            "height_max_m": high[1]}


def check_tile_against_source(path, tile, tolerance=0.002):
    actual = inspect_terrain_glb(path)
    if actual["triangles"] != tile["triangle_count"]:
        raise ValueError("triangle count changed")
    if abs(actual["width_m"] - 250) > tolerance:
        raise ValueError("X axis is not 250m")
    if abs(actual["depth_m"] - 250) > tolerance:
        raise ValueError("glTF ground-plane Z axis is not 250m")
    for k in ("height_min_m", "height_max_m"):
        if k not in tile or abs(actual[k] - tile[k]) > tolerance:
            raise ValueError("signed glTF up-axis height mismatch: " + k)
    return True
