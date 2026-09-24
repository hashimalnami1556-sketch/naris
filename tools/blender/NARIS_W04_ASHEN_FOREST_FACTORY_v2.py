import argparse
import bpy
import json
import math
import sys
from pathlib import Path
from mathutils import Vector

# CALL OF NARIS - W04 Ashen Forest procedural environment factory
# Blender 4.x. Generates a clean modular blockout/dressing foundation.
# Canonical dimensions come from the checked-in environment factory contract.

COLLECTION = "NARIS_W04_FACTORY"
REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = (
    REPO_ROOT
    / "data"
    / "environments"
    / "W04_AshenForest_environment_factory_v2.json"
)
CONFIG = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))

SNAP_GRID = float(CONFIG["grid_m"])
FLOOR_MODULE = float(CONFIG["modular_units"]["floor"])
HEIGHT = float(CONFIG["modular_units"]["height"])
STREAMING_CELL_M = float(CONFIG["streaming"]["cell_size_m"])


def parse_args():
    argv = sys.argv
    argv = argv[argv.index("--") + 1:] if "--" in argv else []
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-blend")
    return parser.parse_args(argv)


def ensure_uv(obj):
    if obj.type != "MESH" or len(obj.data.uv_layers) > 0:
        return

    for selected in bpy.context.selected_objects:
        selected.select_set(False)

    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    obj.data.uv_layers.new(name="UVMap")
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66.0), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")


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

def mat(name, color, metallic=0.0, roughness=0.8):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1.0)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value = (*color, 1.0)
        bs.inputs["Metallic"].default_value = metallic
        bs.inputs["Roughness"].default_value = roughness
    return m

def cube(name, loc, scale, material=None, bevel=0.08):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        mod = o.modifiers.new("EdgeBevel", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    if material:
        o.data.materials.append(material)
    ensure_uv(o)
    move_to_collection(o, get_collection())
    return o

def cylinder(name, loc, radius, depth, material=None, vertices=16):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    if material:
        o.data.materials.append(material)
    ensure_uv(o)
    move_to_collection(o, get_collection())
    return o

def arch(name, loc, width=3.0, height=3.5, depth=0.45, material=None):
    side = (width / 2.0) - 0.45
    cube(name+"_L", (loc[0]-side, loc[1], loc[2]+height/2), (0.45, depth, height/2), material)
    cube(name+"_R", (loc[0]+side, loc[1], loc[2]+height/2), (0.45, depth, height/2), material)
    cube(name+"_TOP", (loc[0], loc[1], loc[2]+height-0.45), (width/2, depth, 0.45), material)

def floor_tile(name, x, y, material):
    return cube(
        name,
        (x, y, -0.10),
        (FLOOR_MODULE / 2, FLOOR_MODULE / 2, 0.10),
        material,
        0.03,
    )

def tree(name, loc, trunk_mat, leaf_mat, scale=1.0):
    cylinder(name+"_TRUNK", (loc[0],loc[1],loc[2]+2.0*scale), 0.32*scale, 4.0*scale, trunk_mat, 10)
    for i, z in enumerate((3.0,4.0,4.8)):
        bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.25*scale, location=(loc[0]+(i-1)*0.35*scale, loc[1], loc[2]+z*scale))
        o=bpy.context.object; o.name=f"{name}_CANOPY_{i:02d}"; o.scale=(1.2,0.9,0.75); bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        o.data.materials.append(leaf_mat); ensure_uv(o); move_to_collection(o,get_collection())

def rock(name, loc, scale, material):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1, radius=1.0, location=loc)
    o=bpy.context.object; o.name=name; o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material); ensure_uv(o); move_to_collection(o,get_collection()); return o

def make_lod_marker(source, lod_level):
    # Metadata-only empty used by import scripts to pair generated meshes with LOD policy.
    e = bpy.data.objects.new(f"{source.name}__LOD{lod_level}", None)
    get_collection().objects.link(e)
    e.empty_display_type = "CUBE"
    e.empty_display_size = 0.15
    e["source_asset"] = source.name
    e["lod_level"] = lod_level
    e["lod_policy"] = json.dumps(CONFIG["lod"], sort_keys=True)
    return e

def build():
    # Materials
    stone=mat("MAT_AshStone",(0.16,0.15,0.14),0,0.82)
    moss=mat("MAT_MossStone",(0.12,0.16,0.12),0,0.9)
    wood=mat("MAT_BurnedWood",(0.055,0.035,0.025),0,0.92)
    ash=mat("MAT_AshGround",(0.10,0.095,0.09),0,0.96)
    crystal=mat("MAT_AetherCrystal",(0.08,0.35,0.8),0.05,0.2)
    crystal.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value=(0.02,0.35,1.0,1.0)
    crystal.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value=7.0

    # 8x8 foundation
    for ix in range(-4,4):
        for iy in range(-4,4):
            floor_tile(f"W04_Floor_{ix+4:02d}_{iy+4:02d}",ix*FLOOR_MODULE,iy*FLOOR_MODULE, ash if (ix+iy)%3 else stone)

    # Modular ruin walls / arches
    for i in range(5):
        cube(f"W04_Wall_A_{i:02d}",(i*FLOOR_MODULE-8,8,1.75),(2,0.3,1.75),stone)
    for i in range(3):
        arch(f"W04_Arch_{i:02d}",(i*6-6,-6,0),3.5,4.5,0.5,moss)
    for i in range(4):
        cylinder(f"W04_Pillar_{i:02d}",(i*3-4,4,2.0),0.45,4.0,stone,12)

    # Broken bridge
    for i in range(6):
        cube(f"W04_Bridge_{i:02d}",(i*3-7.5,-12,2.2),(1.45,1.8,0.25),wood,0.04)

    # Dressing
    for i,loc in enumerate([(-12,4,0),(-4,12,0),(10,10,0),(13,-4,0),(-13,-10,0)]):
        tree(f"W04_BurnedTree_{i:02d}",loc,wood,ash,1.0+(i%2)*0.25)
    for i,loc in enumerate([(-10,7,0),(8,7,0),(12,-8,0),(-6,-12,0),(4,-9,0)]):
        rock(f"W04_Rock_{i:02d}",(loc[0],loc[1],0.5),(1.2,0.8,0.7),stone)

    # Waystone
    cube("W04_Waystone_Base",(0,0,0.6),(0.9,0.9,0.6),stone)
    cylinder("W04_Waystone_Crystal",(0,0,1.9),0.42,2.1,crystal,8)

    # Bone Beast Arena ring
    for i in range(16):
        a=(math.tau*i)/16
        r=7.0
        rock(f"W04_ArenaBone_{i:02d}",(math.cos(a)*r,math.sin(a)*r,0.8),(0.35,0.35,1.4),stone)

    # Metadata root
    root=bpy.data.objects.new("NARIS_W04_ENVIRONMENT_ROOT",None); get_collection().objects.link(root)
    root["asset_pack"] = CONFIG["asset_pack"]
    root["world"] = CONFIG["world"]
    root["grid_m"] = SNAP_GRID
    root["floor_module_m"] = FLOOR_MODULE
    root["height_m"] = HEIGHT
    root["streaming_cell_m"] = STREAMING_CELL_M
    root["engine_targets"] = "|".join(CONFIG["engine_targets"])
    root["collision_policy"] = json.dumps(CONFIG["collision"], sort_keys=True)
    root["lod_policy"] = json.dumps(CONFIG["lod"], sort_keys=True)

    for o in list(get_collection().objects):
        if o.type=='MESH' and not o.name.endswith("_CRYSTAL"):
            make_lod_marker(o,1)
    print("CALL OF NARIS W04 environment factory generated.")

if __name__ == "__main__":
    args = parse_args()
    build()
    if args.out_blend:
        out_blend = Path(args.out_blend).resolve()
        out_blend.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(out_blend))
        print(f"NARIS_W04_FACTORY_BLEND={out_blend}")
