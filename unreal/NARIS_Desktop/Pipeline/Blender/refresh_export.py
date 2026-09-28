import bpy, os, math
ROOT=r"C:\Users\Admin\NARIS"
BLEND=os.path.join(ROOT,"SourceAssets","Blender","NARIS_MasterScene.blend")
FBX=os.path.join(ROOT,"Pipeline","Exchange","FBX","NARIS_Blockout.fbx")

# Make shading explicit
for obj in bpy.context.scene.objects:
    if obj.type == 'MESH':
        for p in obj.data.polygons:
            p.use_smooth = obj.name.startswith(("CHR_","ENM_"))

bpy.ops.wm.save_as_mainfile(filepath=BLEND)
for o in bpy.context.scene.objects:
    o.select_set(o.type in {'MESH','ARMATURE'})
bpy.ops.export_scene.fbx(
    filepath=FBX,
    use_selection=True,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',
    axis_forward='-Y',
    axis_up='Z',
    add_leaf_bones=False,
    bake_anim=True,
    mesh_smooth_type='FACE'
)
print("NARIS_FBX_REFRESHED", FBX)
