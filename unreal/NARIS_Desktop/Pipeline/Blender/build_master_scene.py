import bpy, os, math
from mathutils import Vector

ROOT=r"C:\Users\Admin\NARIS"
BLEND=os.path.join(ROOT,"SourceAssets","Blender","NARIS_MasterScene.blend")
FBX=os.path.join(ROOT,"Pipeline","Exchange","FBX","NARIS_Blockout.fbx")

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ground
bpy.ops.mesh.primitive_plane_add(size=40, location=(0,0,0))
ground=bpy.context.object
ground.name="ENV_AshenGround"

# hero blockout
bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=0.45, depth=1.8, location=(0,0,0.9))
hero=bpy.context.object
hero.name="CHR_AshenVessel_Blockout"

# wolf blockout
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=8, scale=(1.2,0.45,0.55), location=(2.2,0,0.55))
wolf=bpy.context.object
wolf.name="CHR_CelestialWolf_Blockout"

# enemy blockout
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(5,0,1.25), scale=(1.3,1.3,2.5))
enemy=bpy.context.object
enemy.name="ENM_BoneBeast_Blockout"

# gate
for x in (-3.5,3.5):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x,7,2.5), scale=(0.8,0.8,5))
    bpy.context.object.name="ENV_GatePillar"
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0,7,5), scale=(4.3,0.8,0.8))
bpy.context.object.name="ENV_GateLintel"

# camera + sun
bpy.ops.object.camera_add(location=(12,-18,10), rotation=(math.radians(67),0,math.radians(33)))
cam=bpy.context.object
bpy.context.scene.camera=cam
bpy.ops.object.light_add(type='SUN', location=(0,0,8))
sun=bpy.context.object
sun.rotation_euler=(math.radians(25),math.radians(-20),math.radians(30))

bpy.context.scene.unit_settings.system='METRIC'
bpy.context.scene.unit_settings.scale_length=0.01

os.makedirs(os.path.dirname(BLEND),exist_ok=True)
os.makedirs(os.path.dirname(FBX),exist_ok=True)
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
    bake_anim=True
)
print("NARIS_BLEND_OK", BLEND)
print("NARIS_FBX_OK", FBX)
