import bpy

scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = 'METERS'

collections = ['AW_ARCHITECTURE','AW_TERRAIN','AW_PROPS','AW_MATERIALS','AW_VFX','AW_DECALS','AW_COLLISION','AW_EXPORT']
for name in collections:
    if name not in bpy.data.collections:
        c = bpy.data.collections.new(name)
        scene.collection.children.link(c)

scene.tool_settings.use_snap = True
scene.tool_settings.snap_elements = {'INCREMENT'}

if 'AW_Player_Scale_1.83m' not in bpy.data.objects:
    bpy.ops.mesh.primitive_cube_add(location=(0,0,0.915))
    obj = bpy.context.object
    obj.name = 'AW_Player_Scale_1.83m'
    obj.dimensions = (0.6,0.4,1.83)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

if 'AW_Grid_2M_Reference' not in bpy.data.objects:
    bpy.ops.mesh.primitive_plane_add(size=2, location=(3,0,0))
    bpy.context.object.name = 'AW_Grid_2M_Reference'

print('NARIS Ashen Wastes production scene initialized.')
