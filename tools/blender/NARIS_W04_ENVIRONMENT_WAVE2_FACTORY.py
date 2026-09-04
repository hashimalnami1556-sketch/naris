import bpy
import math
from mathutils import Vector

# CALL OF NARIS - W04 Ashen Forest - Wave 2 procedural environment factory
# Blender 4.x. Run inside Blender's Scripting workspace.

GRID = 2.0
COLLECTION = "NARIS_W04_WAVE2"


def get_collection():
    col = bpy.data.collections.get(COLLECTION)
    if not col:
        col = bpy.data.collections.new(COLLECTION)
        bpy.context.scene.collection.children.link(col)
    return col


def move_to_collection(obj, col):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    col.objects.link(obj)


def material(name, base, roughness=0.8, metallic=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*base, 1.0)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*base, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return m


ASH_STONE = material("NARIS_ASH_STONE", (0.075, 0.07, 0.065), 0.92)
BURNT_WOOD = material("NARIS_BURNT_WOOD", (0.035, 0.022, 0.018), 0.98)
AETHER = material("NARIS_AETHER_CRYSTAL", (0.04, 0.22, 0.34), 0.28, 0.15)
EMBER = material("NARIS_EMBER", (0.35, 0.055, 0.008), 0.4)
MOSS = material("NARIS_EMBER_MOSS", (0.055, 0.12, 0.055), 1.0)


def cube(name, loc, scale, mat=ASH_STONE, bevel=0.08):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new("Soft_Ruin_Edges", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    o.data.materials.append(mat)
    move_to_collection(o, get_collection())
    return o


def cylinder(name, loc, radius, depth, mat=ASH_STONE, vertices=12):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    o.data.materials.append(mat)
    move_to_collection(o, get_collection())
    return o


def arch(name, loc, width=3.0, height=4.5, depth=0.45):
    # Gothic arch from side pillars + top voussoir blocks.
    cube(name + "_L", (loc[0] - width/2, loc[1], loc[2] + height/2), (0.35, depth, height/2), ASH_STONE)
    cube(name + "_R", (loc[0] + width/2, loc[1], loc[2] + height/2), (0.35, depth, height/2), ASH_STONE)
    steps = 7
    for i in range(steps):
        t = i / (steps - 1)
        x = (t * 2.0 - 1.0) * width/2
        z = height + math.sqrt(max(0.0, 1.0 - (x/(width/2))**2)) * 0.9
        cube(name + f"_voussoir_{i:02d}", (loc[0]+x, loc[1], loc[2]+z), (width/(steps*1.8), depth, 0.3), ASH_STONE)


def burnt_tree(name, loc, height=6.0):
    trunk = cylinder(name + "_trunk", (loc[0], loc[1], loc[2]+height/2), 0.28, height, BURNT_WOOD, 9)
    trunk.rotation_euler[1] = 0.12
    for i, angle in enumerate((-0.9, -0.35, 0.25, 0.72)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=7, radius=0.11, depth=height*0.42, location=(loc[0], loc[1], loc[2]+height*0.7))
        branch = bpy.context.object
        branch.name = f"{name}_branch_{i}"
        branch.rotation_euler = (0.0, angle, angle*0.35)
        branch.data.materials.append(BURNT_WOOD)
        move_to_collection(branch, get_collection())
    return trunk


def rubble_cluster(name, loc, count=7):
    for i in range(count):
        a = i * 2.399
        r = 0.25 + (i % 3) * 0.16
        cube(f"{name}_{i:02d}", (loc[0]+math.cos(a)*r, loc[1]+math.sin(a)*r, loc[2]+0.15*(i%2)), (0.25+0.05*(i%3), 0.18, 0.16+0.04*(i%2)), ASH_STONE, 0.05)


def waystone(name, loc):
    cylinder(name + "_base", (loc[0], loc[1], loc[2]+0.25), 0.75, 0.5, ASH_STONE, 8)
    bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.42, radius2=0.16, depth=1.8, location=(loc[0], loc[1], loc[2]+1.35))
    o = bpy.context.object
    o.name = name + "_crystal"
    o.data.materials.append(AETHER)
    move_to_collection(o, get_collection())


def build_w04_wave2():
    # Primary ruins
    for i, x in enumerate((-6, -3.5, 3.5, 6)):
        cube(f"RuinWall_{i:02d}", (x, 0, 1.5), (1.0, 0.45, 1.5))
    arch("GothicArch_01", (0, 0, 0))

    # Burnt grove dressing
    for i in range(18):
        a = i * 2.399
        r = 5.0 + (i % 4) * 1.2
        burnt_tree(f"BurntTree_{i:02d}", (math.cos(a)*r, math.sin(a)*r, 0), 4.5 + (i%3)*1.2)

    # Rocks/rubble
    for i in range(14):
        a = i * 1.91
        r = 3.0 + (i % 5) * 1.4
        rubble_cluster(f"Rubble_{i:02d}", (math.cos(a)*r, math.sin(a)*r, 0), 4 + i%5)

    waystone("Waystone_W04_01", (2.5, -2.0, 0))
    waystone("Waystone_W04_02", (-4.0, 4.0, 0))

    # Portal silhouette
    arch("HolyPortal_01", (8, 2, 0), 3.6, 5.2, 0.55)
    cylinder("PortalCore", (8, 2, 2.7), 1.25, 0.22, AETHER, 32)

    # Metadata custom properties for engine import.
    scene = bpy.context.scene
    scene["naris_world"] = "W04_Ashen_Forest"
    scene["naris_wave"] = "10-W2"
    scene["naris_grid_m"] = GRID
    scene["naris_collision"] = "generate_from_asset_class"
    scene["naris_lod_policy"] = "hero_0_1_2_distant_impostor"
    print("NARIS W04 Wave 2 factory complete")


if __name__ == "__main__":
    build_w04_wave2()
