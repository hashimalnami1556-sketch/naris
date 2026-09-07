import bpy
import math
from mathutils import Vector

"""NARIS — Gate Guardian Production Factory v1

Procedural hero/boss asset scaffold for Blender 4.x.
This replaces the primitive Demon King sample with a Naris-specific Gate Guardian
production block: modular body, armor, horns, weapon, emissive sockets, materials,
LOD placeholders, collision proxy and gameplay metadata.

Run from Blender's Scripting workspace. The generated scene is intentionally
engine-neutral and exports cleanly to GLB/FBX after art refinement.
"""

# -----------------------------------------------------------------------------
# Reset / collections
# -----------------------------------------------------------------------------
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for c in list(bpy.data.collections):
    if c.name.startswith('NARIS_'):
        bpy.data.collections.remove(c)

ROOT = bpy.data.collections.new('NARIS_GATE_GUARDIAN')
BODY = bpy.data.collections.new('NARIS_GG_BODY')
ARMOR = bpy.data.collections.new('NARIS_GG_ARMOR')
WEAPON = bpy.data.collections.new('NARIS_GG_WEAPON')
FX = bpy.data.collections.new('NARIS_GG_FX')
COLL = bpy.data.collections.new('NARIS_GG_COLLISION')
LOD = bpy.data.collections.new('NARIS_GG_LOD')
bpy.context.scene.collection.children.link(ROOT)
for c in (BODY, ARMOR, WEAPON, FX, COLL, LOD):
    ROOT.children.link(c)


def move_to(obj, collection):
    for c in list(obj.users_collection):
        c.objects.unlink(obj)
    collection.objects.link(obj)


def mat(name, base, metallic=0.0, rough=0.5, emission=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*base, 1.0)
    bsdf.inputs['Metallic'].default_value = metallic
    bsdf.inputs['Roughness'].default_value = rough
    if emission:
        bsdf.inputs['Emission Color'].default_value = (*emission, 1.0)
        bsdf.inputs['Emission Strength'].default_value = 5.0
    return m

MAT_BODY = mat('MAT_GG_ObsidianBody', (0.045, 0.055, 0.065), 0.15, 0.42)
MAT_STONE = mat('MAT_GG_AncientStone', (0.16, 0.17, 0.18), 0.35, 0.68)
MAT_METAL = mat('MAT_GG_BlackIron', (0.055, 0.06, 0.07), 0.85, 0.28)
MAT_GOLD = mat('MAT_GG_NarisGold', (0.34, 0.21, 0.07), 0.8, 0.3)
MAT_VOID = mat('MAT_GG_VioletVoid', (0.035, 0.01, 0.06), 0.15, 0.3, (0.34, 0.02, 0.65))
MAT_EMBER = mat('MAT_GG_Ember', (0.25, 0.025, 0.005), 0.1, 0.3, (1.0, 0.10, 0.01))


def smooth(obj):
    if hasattr(obj.data, 'polygons'):
        for p in obj.data.polygons:
            p.use_smooth = True


def uv_sphere(name, loc, scale, material, collection=BODY, seg=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=rings, location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    smooth(o)
    o.data.materials.append(material)
    move_to(o, collection)
    return o


def cube(name, loc, scale, material, bevel=0.08, collection=ARMOR):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        b = o.modifiers.new('Bevel', 'BEVEL')
        b.width = bevel
        b.segments = 3
    o.data.materials.append(material)
    move_to(o, collection)
    return o


def cylinder(name, loc, radius, depth, material, collection=BODY, vertices=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=loc)
    o = bpy.context.object
    o.name = name
    smooth(o)
    o.data.materials.append(material)
    move_to(o, collection)
    return o


def cone(name, loc, r1, r2, depth, material, rotation=(0, 0, 0), collection=ARMOR):
    bpy.ops.mesh.primitive_cone_add(vertices=24, radius1=r1, radius2=r2, depth=depth, location=loc, rotation=rotation)
    o = bpy.context.object
    o.name = name
    smooth(o)
    o.data.materials.append(material)
    move_to(o, collection)
    return o

# -----------------------------------------------------------------------------
# Body — imposing but game-readable silhouette
# -----------------------------------------------------------------------------
# proportions: ~3.2m boss
uv_sphere('GG_Chest', (0, 0, 1.75), (0.92, 0.58, 1.05), MAT_BODY)
uv_sphere('GG_Abdomen', (0, -0.01, 1.05), (0.62, 0.48, 0.62), MAT_BODY)
uv_sphere('GG_Head', (0, 0, 2.85), (0.48, 0.43, 0.55), MAT_STONE)

for side, x in (('L', -0.82), ('R', 0.82)):
    cylinder(f'GG_UpperArm_{side}', (x, 0, 1.75), 0.25, 0.95, MAT_BODY)
    cylinder(f'GG_Forearm_{side}', (x * 1.06, 0, 1.08), 0.23, 0.75, MAT_BODY)
    uv_sphere(f'GG_Fist_{side}', (x * 1.07, -0.02, 0.63), (0.28, 0.28, 0.3), MAT_STONE)

for side, x in (('L', -0.38), ('R', 0.38)):
    cylinder(f'GG_Thigh_{side}', (x, 0, 0.62), 0.31, 0.9, MAT_BODY)
    cylinder(f'GG_Shin_{side}', (x, 0, -0.15), 0.25, 0.65, MAT_STONE)
    cube(f'GG_Boot_{side}', (x, -0.13, -0.52), (0.32, 0.5, 0.18), MAT_METAL, 0.1, BODY)

# -----------------------------------------------------------------------------
# Armor — modular plates
# -----------------------------------------------------------------------------
for side, x in (('L', -0.9), ('R', 0.9)):
    cube(f'GG_Shoulder_{side}', (x, 0, 2.02), (0.34, 0.52, 0.22), MAT_METAL, 0.12)
    cube(f'GG_ArmPlate_{side}', (x * 1.02, -0.02, 1.43), (0.29, 0.18, 0.38), MAT_STONE, 0.07)
    cube(f'GG_ThighPlate_{side}', (x * 0.44, -0.08, 0.62), (0.3, 0.34, 0.22), MAT_METAL, 0.07)

for i, z in enumerate((1.85, 1.55, 1.25)):
    cube(f'GG_ChestPlate_{i}', (0, -0.56, z), (0.52 - i * 0.05, 0.10, 0.13), MAT_STONE, 0.05)

# crown / horns
for side, x, rz in (('L', -0.31, math.radians(-18)), ('R', 0.31, math.radians(18))):
    h = cone(f'GG_Horn_{side}', (x, 0, 3.28), 0.17, 0.015, 0.78, MAT_VOID, (0, rz, 0))
    h.rotation_euler[1] = rz

# -----------------------------------------------------------------------------
# Naris weapon: Gatebreaker greatblade
# -----------------------------------------------------------------------------
blade = cube('GG_Gatebreaker_Blade', (0.92, -0.05, 0.2), (0.10, 0.16, 1.05), MAT_GOLD, 0.035, WEAPON)
blade.rotation_euler[1] = math.radians(-12)
handle = cylinder('GG_Gatebreaker_Handle', (1.13, -0.05, -0.85), 0.07, 0.55, MAT_METAL, WEAPON)
handle.rotation_euler[1] = math.radians(90)

# -----------------------------------------------------------------------------
# Emissive eyes/core + sockets
# -----------------------------------------------------------------------------
def emissive_sphere(name, loc, scale, material):
    return uv_sphere(name, loc, scale, material, FX, 20, 10)

emissive_sphere('GG_Eye_L', (-0.18, -0.39, 2.9), (0.07, 0.025, 0.035), MAT_VOID)
emissive_sphere('GG_Eye_R', (0.18, -0.39, 2.9), (0.07, 0.025, 0.035), MAT_VOID)
emissive_sphere('GG_Core', (0, -0.66, 1.72), (0.15, 0.045, 0.18), MAT_VOID)

for name, loc in {
    'Socket_Weapon_R': (1.05, 0, 1.0),
    'Socket_VFX_Core': (0, -0.72, 1.72),
    'Socket_FX_Head': (0, 0, 3.5),
}.items():
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=loc)
    o = bpy.context.object
    o.name = name
    move_to(o, FX)

# -----------------------------------------------------------------------------
# Collision proxy + LOD placeholders
# -----------------------------------------------------------------------------
proxy = cylinder('GG_COLLISION_CAPSULE', (0, 0, 1.35), 0.72, 2.9, MAT_BODY, COLL, 16)
proxy.display_type = 'WIRE'
proxy.hide_render = True

for level, scale in ((1, 0.82), (2, 0.58)):
    # non-rendering proxy markers; final decimation should be authored after sculpt
    bpy.ops.object.empty_add(type='CUBE', location=(0, 0, 1.5))
    o = bpy.context.object
    o.name = f'GG_LOD{level}_TARGET'
    o.scale = (scale, scale, scale)
    move_to(o, LOD)

# -----------------------------------------------------------------------------
# Gameplay metadata
# -----------------------------------------------------------------------------
root = bpy.data.objects.new('GG_GAMEPLAY_ROOT', None)
ROOT.objects.link(root)
root['asset_id'] = 'NARIS-GG-001'
root['asset_type'] = 'boss_character'
root['display_name'] = 'Gate Guardian'
root['realm'] = 'ash_gate'
root['health'] = 1800
root['damage'] = 55
root['speed'] = 2.6
root['attack_range'] = 3.2
root['phase_thresholds'] = [0.70, 0.40]
root['flee'] = False
root['element'] = 'void'
root['vfx_palette'] = 'aether_violet_ancient_gold'
root['export_runtime'] = 'GLB'
root['export_cinematic'] = 'FBX'

# Scene metadata
scene = bpy.context.scene
scene['NARIS_ASSET_ID'] = 'NARIS-GG-001'
scene['NARIS_ASSET_VERSION'] = '1.0.0'
scene['NARIS_EXPORT_TARGET'] = 'Babylon.js / GLB'
scene['NARIS_PRODUCTION_STATUS'] = 'BLOCKOUT_PRODUCTION_READY_FOR_SCULPT'

# Organize root display
for obj in ROOT.objects:
    obj.select_set(False)

bpy.context.view_layer.objects.active = root
root.select_set(True)

print('NARIS Gate Guardian factory complete.')
print('Next art pass: sculpt/detail -> retopo -> UV -> PBR -> rig -> animations -> GLB.')
