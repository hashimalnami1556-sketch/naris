import bpy, os
OUT = r"C:\Users\Admin\NARIS\Pipeline\Exchange\FBX"
os.makedirs(OUT, exist_ok=True)
scene=bpy.context.scene
scene.unit_settings.system='METRIC'
scene.unit_settings.scale_length=0.01
for obj in bpy.context.scene.objects:
    obj.select_set(obj.type in {'MESH','ARMATURE'})
bpy.ops.export_scene.fbx(
    filepath=os.path.join(OUT,'NARIS_EXPORT.fbx'),
    use_selection=True,
    apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',
    axis_forward='-Y',
    axis_up='Z',
    add_leaf_bones=False,
    bake_anim=True,
    bake_anim_use_all_actions=True
)
print('NARIS FBX export complete')