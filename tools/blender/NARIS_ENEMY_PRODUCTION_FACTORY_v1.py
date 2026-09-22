"""NARIS Enemy Production Factory v1
Generates deterministic Blender blockout/production scaffolds for web-game enemies.
Runtime target: Babylon.js / GLB. Cinematic target: FBX.
This is a production scaffold, not final sculpt/retopo/UV/PBR/animation.
"""
import bpy
from mathutils import Vector

ENEMIES = {
    "ASHEN_SHADE": {
        "asset_id": "NARIS-W04-ENM-ASHEN-SHADE-0001", "name": "Ashen Shade",
        "health": 220, "damage": 24, "speed": 3.8, "range": 2.8,
        "element": "AetherViolet", "flying": True, "scale": (1.15, 2.2, 1.15),
    },
    "THORN_CREATURE": {
        "asset_id": "NARIS-W07-ENM-THORN-CREATURE-0001", "name": "Thorn Creature",
        "health": 300, "damage": 32, "speed": 4.6, "range": 2.2,
        "element": "Emerald", "flying": False, "scale": (1.25, 1.5, 1.25),
    },
    "STONE_GUARDIAN": {
        "asset_id": "NARIS-W08-ENM-STONE-GUARDIAN-0001", "name": "Stone Guardian",
        "health": 650, "damage": 55, "speed": 1.7, "range": 3.2,
        "element": "Obsidian", "flying": False, "scale": (1.65, 2.6, 1.45),
    },
    "GATE_GUARDIAN": {
        "asset_id": "NARIS-GG-001", "name": "Gate Guardian",
        "health": 1800, "damage": 55, "speed": 2.6, "range": 3.2,
        "element": "Void", "flying": False, "scale": (2.1, 3.8, 1.8),
    },
}


def mat(name, color, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    if emission:
        m.use_nodes = True
        bs = m.node_tree.nodes.get("Principled BSDF")
        if bs:
            bs.inputs["Base Color"].default_value = (*color, 1)
            bs.inputs["Emission Color"].default_value = (*emission, 1)
            bs.inputs["Emission Strength"].default_value = 4.0
    return m


def cube(name, loc, scale, material):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object; o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    return o


def uv(name, loc, scale, material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, location=loc)
    o = bpy.context.object; o.name = name; o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    o.data.materials.append(material)
    return o


def socket(name, loc, parent=None):
    o = bpy.data.objects.new(name, None); o.empty_display_type = 'SPHERE'; o.empty_display_size = 0.12; o.location = loc
    if parent: o.parent = parent
    return o


def build_enemy(key, cfg):
    col = bpy.data.collections.new(f"NARIS_{key}"); bpy.context.scene.collection.children.link(col)
    steel = mat(f"{key}_Steel", (0.10, 0.12, 0.14))
    dark = mat(f"{key}_Dark", (0.025, 0.02, 0.03))
    glow = mat(f"{key}_Glow", (0.18, 0.55, 0.9), (0.08, 0.7, 1.0))
    root = bpy.data.objects.new(f"{key}_ROOT", None); col.objects.link(root)
    root["naris_asset_id"] = cfg["asset_id"]; root["enemy_id"] = key.lower(); root["health"] = cfg["health"]
    root["damage"] = cfg["damage"]; root["speed"] = cfg["speed"]; root["attack_range"] = cfg["range"]
    root["flying"] = cfg["flying"]; root["element"] = cfg["element"]; root["runtime"] = "babylonjs"; root["export"] = "glb"

    sx, sy, sz = cfg["scale"]
    body = uv(f"{key}_BODY", (0, sy * 0.52, 0), (sx, sy, sz), steel); body.parent = root
    chest = cube(f"{key}_CHEST", (0, sy * 0.78, -0.18 * sz), (sx * 0.72, sy * 0.38, sz * 0.5), dark); chest.parent = root
    head = uv(f"{key}_HEAD", (0, sy * 1.48, -0.02), (sx * 0.55, sy * 0.34, sz * 0.55), dark); head.parent = root
    for x in (-sx * 0.22, sx * 0.22):
        eye = uv(f"{key}_EYE", (x, sy * 1.52, -sz * 0.5), (sx * 0.10, sy * 0.09, sz * 0.06), glow); eye.parent = root

    # Limb / attack silhouettes
    arm_l = cube(f"{key}_ARM_L", (-sx * 0.95, sy * 0.82, 0), (sx * 0.22, sy * 0.62, sz * 0.22), steel); arm_l.parent = root
    arm_r = cube(f"{key}_ARM_R", (sx * 0.95, sy * 0.82, 0), (sx * 0.22, sy * 0.62, sz * 0.22), steel); arm_r.parent = root
    weapon = cube(f"{key}_WEAPON", (sx * 1.10, sy * 0.28, -sz * 0.2), (sx * 0.12, sy * 0.9, sz * 0.12), glow); weapon.parent = root

    socket("SOCKET_VFX_CORE", (0, sy * 0.9, -sz * 0.5), root)
    socket("SOCKET_ATTACK", (0, sy * 0.65, -cfg["range"]), root)
    socket("SOCKET_HIT", (0, sy * 1.0, 0), root)
    socket("SOCKET_PROJECTILE", (0, sy * 1.25, -sz * 0.6), root)
    socket("SOCKET_AUDIO", (0, 0.5, 0), root)

    bpy.context.view_layer.objects.active = root; root.select_set(True)
    return root


def main():
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for key, cfg in ENEMIES.items(): build_enemy(key, cfg)
    scene = bpy.context.scene
    scene["naris_factory"] = "NARIS_ENEMY_PRODUCTION_FACTORY_v1"
    scene["asset_count"] = len(ENEMIES)
    scene["runtime_target"] = "Babylon.js"
    scene["web_format"] = "GLB/glTF 2.0"
    scene["cinematic_format"] = "FBX"
    print(f"NARIS enemy factory built: {len(ENEMIES)} enemies")


if __name__ == "__main__":
    main()
