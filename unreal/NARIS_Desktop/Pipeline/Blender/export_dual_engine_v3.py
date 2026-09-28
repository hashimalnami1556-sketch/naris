import bpy, os, json
ROOT = r"C:\Users\Admin\NARIS"
UE_OUT = os.path.join(ROOT, "Pipeline", "Exchange", "FBX", "RiggedV3")
UNITY_OUT = os.path.join(ROOT, "Pipeline", "Exchange", "Unity")
GLTF_OUT = os.path.join(ROOT, "Pipeline", "Exchange", "GLTF", "RiggedV2")
REPORT = os.path.join(ROOT, "Pipeline", "Blender", "DUAL_ENGINE_EXPORT_V3.json")
for p in (UE_OUT, UNITY_OUT, GLTF_OUT): os.makedirs(p, exist_ok=True)
def prepare_scene():
    s=bpy.context.scene
    s.unit_settings.system='METRIC'; s.unit_settings.scale_length=0.01; s.render.fps=30
    for o in s.objects:
        o.select_set(o.type in {'MESH','ARMATURE'})
        if o.type=='MESH':
            for poly in o.data.polygons: poly.use_smooth=True
def export_fbx(filepath, unity=False):
    bpy.ops.export_scene.fbx(filepath=filepath,use_selection=True,object_types={'ARMATURE','MESH'},
        apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',
        axis_forward='-Z' if unity else '-Y',axis_up='Y' if unity else 'Z',
        add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,
        bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.0,
        mesh_smooth_type='FACE',use_armature_deform_only=False)
def export_gltf(filepath):
    bpy.ops.export_scene.gltf(filepath=filepath,export_format='GLB',use_selection=True,
        export_animations=True,export_skins=True,export_yup=True)
def inspect_asset():
    arms=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    return {"armatures":len(arms),"meshes":len(meshes),"bones":sum(len(a.data.bones) for a in arms),
            "actions":sorted(a.name for a in bpy.data.actions),"vertices":sum(len(m.data.vertices) for m in meshes)}
name=os.path.splitext(os.path.basename(bpy.data.filepath))[0]
prepare_scene()
ue_fbx=os.path.join(UE_OUT,name+".fbx"); unity_fbx=os.path.join(UNITY_OUT,name+".fbx"); glb=os.path.join(GLTF_OUT,name+".glb")
export_fbx(ue_fbx,False); export_fbx(unity_fbx,True); export_gltf(glb)
data=inspect_asset(); data.update({"source":bpy.data.filepath,"ue_fbx":ue_fbx,"unity_fbx":unity_fbx,"glb":glb})
all_report={}
if os.path.exists(REPORT):
    try:
        with open(REPORT,'r',encoding='utf-8') as f: all_report=json.load(f)
    except Exception: all_report={}
all_report[name]=data
with open(REPORT,'w',encoding='utf-8') as f: json.dump(all_report,f,indent=2)
print("NARIS_DUAL_EXPORT_V3_SUCCESS",json.dumps(data))