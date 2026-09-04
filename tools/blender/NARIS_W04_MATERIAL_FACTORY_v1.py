import bpy
import math
import random

# CALL OF NARIS - W04 ASHEN FOREST
# Procedural PBR Material Factory - Blender 4.x
# Creates production-ready node materials without external texture dependencies.
# Run in Blender's Scripting workspace.

COLLECTION = "NARIS_W04_MATERIALS"
SEED = 4104


def rgba(hex_color):
    h = hex_color.lstrip('#')
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4)) + (1.0,)


def clear_collection(name):
    col = bpy.data.collections.get(name)
    if col:
        for obj in list(col.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.data.collections.remove(col)
    return bpy.data.collections.new(name)


def node_material(name, base, roughness, metallic=0.0, noise_scale=5.0,
                  detail_scale=35.0, bump_strength=0.35, emission=None,
                  emission_strength=0.0, wet=False, crystal=False):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    n = nt.nodes
    l = nt.links

    out = n.new('ShaderNodeOutputMaterial'); out.location = (900, 0)
    bsdf = n.new('ShaderNodeBsdfPrincipled'); bsdf.location = (620, 0)
    bsdf.inputs['Base Color'].default_value = base
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = metallic

    tex = n.new('ShaderNodeTexNoise'); tex.location = (-700, 120)
    tex.inputs['Scale'].default_value = noise_scale
    tex.inputs['Detail'].default_value = 7.0
    tex.inputs['Roughness'].default_value = 0.72
    tex.inputs['Distortion'].default_value = 0.22

    detail = n.new('ShaderNodeTexNoise'); detail.location = (-700, -180)
    detail.inputs['Scale'].default_value = detail_scale
    detail.inputs['Detail'].default_value = 4.0
    detail.inputs['Roughness'].default_value = 0.65

    ramp = n.new('ShaderNodeValToRGB'); ramp.location = (-350, 160)
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = tuple(max(0.0, c * 0.58) for c in base[:3]) + (1,)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = tuple(min(1.0, c * 1.42 + 0.015) for c in base[:3]) + (1,)

    bump = n.new('ShaderNodeBump'); bump.location = (320, -160)
    bump.inputs['Strength'].default_value = bump_strength
    bump.inputs['Distance'].default_value = 0.08

    mapping = n.new('ShaderNodeMapping'); mapping.location = (-930, 120)
    coord = n.new('ShaderNodeTexCoord'); coord.location = (-1150, 120)

    l.new(coord.outputs['Generated'], mapping.inputs['Vector'])
    l.new(mapping.outputs['Vector'], tex.inputs['Vector'])
    l.new(mapping.outputs['Vector'], detail.inputs['Vector'])
    l.new(tex.outputs['Fac'], ramp.inputs['Fac'])
    l.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    l.new(detail.outputs['Fac'], bump.inputs['Height'])
    l.new(bump.outputs['Normal'], bsdf.inputs['Normal'])

    if wet:
        bsdf.inputs['Roughness'].default_value = roughness
        bsdf.inputs['Coat Weight'].default_value = 0.28
        bsdf.inputs['Coat Roughness'].default_value = 0.12

    if crystal:
        bsdf.inputs['Transmission Weight'].default_value = 0.16
        bsdf.inputs['IOR'].default_value = 1.46
        bsdf.inputs['Roughness'].default_value = 0.16

    if emission:
        bsdf.inputs['Emission Color'].default_value = emission
        bsdf.inputs['Emission Strength'].default_value = emission_strength

    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def make_water():
    mat = bpy.data.materials.get('MAT_W04_WHISPER_LAKE_01') or bpy.data.materials.new('MAT_W04_WHISPER_LAKE_01')
    mat.use_nodes = True
    mat.surface_render_method = 'DITHERED'
    nt = mat.node_tree; nt.nodes.clear(); n = nt.nodes; l = nt.links
    out = n.new('ShaderNodeOutputMaterial'); out.location = (850, 0)
    bsdf = n.new('ShaderNodeBsdfPrincipled'); bsdf.location = (560, 0)
    bsdf.inputs['Base Color'].default_value = (0.025, 0.09, 0.13, 1)
    bsdf.inputs['Metallic'].default_value = 0.02
    bsdf.inputs['Roughness'].default_value = 0.08
    bsdf.inputs['Transmission Weight'].default_value = 0.55
    bsdf.inputs['IOR'].default_value = 1.333
    bsdf.inputs['Coat Weight'].default_value = 0.35
    bsdf.inputs['Coat Roughness'].default_value = 0.06
    noise_a = n.new('ShaderNodeTexNoise'); noise_a.location = (-620, 170)
    noise_a.inputs['Scale'].default_value = 2.2
    noise_a.inputs['Detail'].default_value = 5.0
    noise_b = n.new('ShaderNodeTexNoise'); noise_b.location = (-620, -100)
    noise_b.inputs['Scale'].default_value = 13.0
    noise_b.inputs['Detail'].default_value = 3.0
    bump = n.new('ShaderNodeBump'); bump.location = (250, -150)
    bump.inputs['Strength'].default_value = 0.18
    bump.inputs['Distance'].default_value = 0.06
    mix = n.new('ShaderNodeMixRGB'); mix.location = (-300, 60); mix.blend_type = 'MULTIPLY'
    coord = n.new('ShaderNodeTexCoord'); coord.location = (-850, 250)
    l.new(coord.outputs['Generated'], noise_a.inputs['Vector'])
    l.new(coord.outputs['Generated'], noise_b.inputs['Vector'])
    l.new(noise_a.outputs['Fac'], mix.inputs[1])
    l.new(noise_b.outputs['Fac'], mix.inputs[2])
    l.new(mix.outputs['Color'], bump.inputs['Height'])
    l.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def create_decal_material(name, color, emission=None):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree; nt.nodes.clear(); n = nt.nodes; l = nt.links
    out = n.new('ShaderNodeOutputMaterial'); out.location = (600, 0)
    bsdf = n.new('ShaderNodeBsdfPrincipled'); bsdf.location = (300, 0)
    bsdf.inputs['Base Color'].default_value = rgba(color)
    bsdf.inputs['Roughness'].default_value = 0.72
    bsdf.inputs['Alpha'].default_value = 0.82
    if emission:
        bsdf.inputs['Emission Color'].default_value = rgba(emission)
        bsdf.inputs['Emission Strength'].default_value = 2.0
    tex = n.new('ShaderNodeTexNoise'); tex.location = (-450, 0)
    tex.inputs['Scale'].default_value = 9.0
    ramp = n.new('ShaderNodeValToRGB'); ramp.location = (-180, 0)
    ramp.color_ramp.elements[0].position = 0.36
    ramp.color_ramp.elements[1].position = 0.62
    l.new(tex.outputs['Fac'], ramp.inputs['Fac'])
    l.new(ramp.outputs['Color'], bsdf.inputs['Alpha'])
    l.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def build():
    random.seed(SEED)
    col = clear_collection(COLLECTION)

    mats = [
        node_material('MAT_W04_ASH_SOIL_01', rgba('#17151B'), 0.93, noise_scale=6.0, detail_scale=70.0, bump_strength=0.28),
        node_material('MAT_W04_VOLCANIC_STONE_01', rgba('#302E36'), 0.84, noise_scale=3.4, detail_scale=42.0, bump_strength=0.52),
        node_material('MAT_W04_ANCIENT_STONE_01', rgba('#4A4650'), 0.72, noise_scale=2.7, detail_scale=28.0, bump_strength=0.46),
        node_material('MAT_W04_WET_STONE_01', rgba('#343942'), 0.34, noise_scale=4.0, detail_scale=34.0, bump_strength=0.38, wet=True),
        node_material('MAT_W04_BURNT_WOOD_01', rgba('#211914'), 0.82, noise_scale=5.0, detail_scale=24.0, bump_strength=0.42),
        node_material('MAT_W04_OXIDIZED_IRON_01', rgba('#3A4144'), 0.58, metallic=0.88, noise_scale=5.0, detail_scale=55.0, bump_strength=0.24),
        node_material('MAT_W04_AETHER_CRYSTAL_01', rgba('#0D617A'), 0.18, metallic=0.05, noise_scale=2.2, detail_scale=18.0, bump_strength=0.18, emission=rgba('#5FE8FF'), emission_strength=5.0, crystal=True),
        node_material('MAT_W04_AETHER_CORRUPTED_STONE_01', rgba('#1F1730'), 0.62, metallic=0.04, noise_scale=3.0, detail_scale=38.0, bump_strength=0.56, emission=rgba('#6C2CFF'), emission_strength=2.2),
        node_material('MAT_W04_MOSS_LICHEN_01', rgba('#394C3A'), 0.96, noise_scale=8.0, detail_scale=48.0, bump_strength=0.34),
        make_water(),
    ]

    decal_defs = {
        'DEC_W04_ASH_STREAK': '#2A2730',
        'DEC_W04_WATER_STAIN': '#1D2B32',
        'DEC_W04_ANCIENT_CRACK': '#15131A',
        'DEC_W04_RUNE_FADE': '#604B70',
        'DEC_W04_BURN_SCORCH': '#120C09',
        'DEC_W04_CLAW_SCRATCH': '#6A5B62',
        'DEC_W04_AETHER_CORRUPTION': '#5A27A8',
    }
    for name, color in decal_defs.items():
        create_decal_material(name, color, '#5FE8FF' if 'AETHER' in name else None)

    # A tiny material swatch rack for visual QA inside Blender.
    for i, mat in enumerate(mats):
        bpy.ops.mesh.primitive_cube_add(size=1.0, location=(i * 1.35, 0, 0))
        obj = bpy.context.object
        obj.name = f'SWATCH_{mat.name}'
        obj.data.materials.append(mat)
        obj.scale = (0.55, 0.55, 0.08)
        for c in list(obj.users_collection): c.objects.unlink(obj)
        col.objects.link(obj)

    bpy.context.scene['NARIS_MATERIAL_FACTORY'] = 'W04_v1'
    bpy.context.scene['NARIS_MATERIAL_SEED'] = SEED
    bpy.context.scene['NARIS_MATERIAL_COUNT'] = len(bpy.data.materials)
    print(f'[NARIS] Material factory complete. Production materials: {len(mats)} + 7 decals.')


if __name__ == '__main__':
    build()
