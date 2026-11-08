"""WORLD-015: real GLB2 binary and signed vertical-bounds validator.

Pure Python stdlib. Requires genuine vertex + index BIN bytes. Does not imply
a successful Unreal import; an in-editor GLB Y-up -> UE Z-up check is separate.
"""
import json
import math
from pathlib import Path
import struct


def inspect_terrain_glb(path):
    data = Path(path).read_bytes()
    if len(data) < 28 or data[:4] != b"glTF":
        raise ValueError("GLB magic/truncated")
    version, n = struct.unpack_from("<II", data, 4)
    if version != 2 or n != len(data):
        raise ValueError("GLB version/length mismatch")
    json_len, json_type = struct.unpack_from("<I4s", data, 12)
    if json_type != b"JSON" or not (0 < json_len <= len(data) - 28):
        raise ValueError("GLB JSON chunk invalid")
    at = 20 + json_len
    binary_len, binary_type = struct.unpack_from("<I4s", data, at)
    if binary_type != b"BIN\x00" or at + 8 + binary_len != len(data):
        raise ValueError("GLB vertex/index BIN chunk missing")
    parsed = json.loads(data[20:at].decode("utf-8"))
    buffers = parsed.get("buffers", [])
    if len(buffers) != 1 or not (0 < buffers[0]["byteLength"] <= binary_len):
        raise ValueError("GLB buffer not backed by physical bytes")
    meshes = parsed.get("meshes", [])
    if len(meshes) != 1 or len(meshes[0].get("primitives", [])) != 1:
        raise ValueError("Expected exactly one terrain mesh/primitive")
    primitive = meshes[0]["primitives"][0]
    if primitive.get("mode", 4) != 4:
        raise ValueError("Terrain topology must be triangles")
    accessors = parsed["accessors"]
    position = accessors[primitive["attributes"]["POSITION"]]
    indices = accessors[primitive["indices"]]
    if position["type"] != "VEC3" or position.get("componentType") != 5126:
        raise ValueError("Terrain requires Float32 POSITION")
    if indices["type"] != "SCALAR" or indices.get("componentType") not in (5121, 5123, 5125):
        raise ValueError("Invalid terrain index component type")
    if position["count"] <= 2 or indices["count"] <= 0 or indices["count"] % 3:
        raise ValueError("Degenerate or incomplete terrain data")
    views = parsed["bufferViews"]

    def accessor_pos(acc, element_bytes):
        view = views[acc["bufferView"]]
        offset = view.get("byteOffset", 0) + acc.get("byteOffset", 0)
        stride = view.get("byteStride", element_bytes)
        last = offset + (acc["count"] - 1) * stride + element_bytes
        if view.get("buffer", 0) != 0 or stride < element_bytes or offset < 0:
            raise ValueError("Invalid GLB buffer view")
        if last > view.get("byteOffset", 0) + view["byteLength"] or last > binary_len:
            raise ValueError("GLB accessor extends beyond actual BIN data")
        return at + 8 + offset, stride

    v_start, v_stride = accessor_pos(position, 12)
    vertices = [struct.unpack_from("<fff", data, v_start + i * v_stride)
                for i in range(position["count"])]
    if any(not math.isfinite(v) for point in vertices for v in point):
        raise ValueError("Nonfinite terrain coordinate")
    lo = [min(p[k] for p in vertices) for k in range(3)]
    hi = [max(p[k] for p in vertices) for k in range(3)]
    if len(position.get("min", [])) != 3 or len(position.get("max", [])) != 3:
        raise ValueError("Missing glTF position bounds")
    if any(abs(x - y) > 0.002 for x, y in zip(lo + hi, position["min"] + position["max"])):
        raise ValueError("Declared GLB accessor bounds do not match vertices")

    fmt, width = {5121: ("B", 1), 5123: ("H", 2), 5125: ("I", 4)}[indices["componentType"]]
    i_start, i_stride = accessor_pos(indices, width)
    ids = [struct.unpack_from("<" + fmt, data, i_start + k * i_stride)[0]
           for k in range(indices["count"])]
    if any(idx >= len(vertices) for idx in ids):
        raise ValueError("Triangle refers to a missing vertex")
    for face in (0, len(ids) // 6 * 3, len(ids) - 3):
        p0, p1, p2 = (vertices[ids[face + k]] for k in range(3))
        ax, az = p1[0] - p0[0], p1[2] - p0[2]
        bx, bz = p2[0] - p0[0], p2[2] - p0[2]
        if az * bx - ax * bz <= 0:
            raise ValueError("Downward-facing terrain triangle")
    return {"triangles": len(ids) // 3,
            "width_m": hi[0] - lo[0], "depth_m": hi[2] - lo[2],
            "height_min_m": lo[1], "height_max_m": hi[1]}


def check_tile_against_source(path, tile, tolerance=0.002):
    geom = inspect_terrain_glb(path)
    if geom["triangles"] != tile["triangle_count"]:
        raise ValueError("Triangle count mismatch")
    if abs(geom["width_m"] - 250) > tolerance or abs(geom["depth_m"] - 250) > tolerance:
        raise ValueError("GLB tile footprint mismatch")
    for field in ("height_min_m", "height_max_m"):
        if field not in tile or abs(geom[field] - float(tile[field])) > tolerance:
            raise ValueError("Signed Y-up terrain elevation mismatch: " + field)
    return True
