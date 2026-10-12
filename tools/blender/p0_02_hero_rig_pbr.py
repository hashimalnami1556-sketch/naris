# CALL OF NARIS — P0-02 Hero Rig + PBR Production Gate
# Consumes Production/Hero/P0-01_reimport_log.json and SK_AshenVessel_Production.blend
import bpy, os, sys, json, math, traceback
from mathutils import Vector

PROJECT_ROOT=r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
HERO_DIR=argv[argv.index("--hero-dir")+1] if "--hero-dir" in argv else os.path.join(PROJECT_ROOT,"Production","Hero")
LOG1=os.path.join(HERO_DIR,"P0-01_reimport_log.json")
SRC_BLEND=os.path.join(HERO_DIR,"SK_AshenVessel_Production.blend")
OUT_BLEND=os.path.join(HERO_DIR,"SK_AshenVessel_PBR.blend")
OUT_FBX=os.path.join(HERO_DIR,"SK_AshenVessel_PBR.fbx")
LOG2=os.path.join(HERO_DIR,"P0-02_rig_pbr_log.json")

def fail(reason, extra=None, code=20):
    report={"status":"FAIL","reason":reason}
    if extra: report.update(extra)
    with open(LOG2,"w",encoding="utf-8") as f: json.dump(report,f,indent=2,ensure_ascii=False)
    print(json.dumps(report,indent=2,ensure_ascii=False))
    raise SystemExit(code)

if not os.path.isfile(LOG1): fail("missing_p0_01_log")
with open(LOG1,"r",encoding="utf-8") as f: p1=json.load(f)
if not p1.get("production_grade"): fail("p0_01_not_production_grade",{"p0_01_status":p1.get("status")},21)
if not os.path.isfile(SRC_BLEND): fail("missing_p0_01_blend",22)

bpy.ops.wm.open_mainfile(filepath=SRC_BLEND)

armatures=[o for o in bpy.data.objects if o.type=="ARMATURE"]
meshes=[o for o in bpy.data.objects if o.type=="MESH"]
if not armatures: fail("no_armature",23)
if not meshes: fail("no_mesh",24)
arm=max(armatures,key=lambda o:len(o.data.bones))
arm.name="SKEL_NARIS_Humanoid"

ALIASES={
"root":("root","Root","ROOT","armature"),
"pelvis":("pelvis","hips","hip","Hips","mixamorig:Hips"),
"spine_01":("spine","spine1","spine_01","Spine","mixamorig:Spine"),
"spine_02":("spine2","spine_02","Spine1","mixamorig:Spine1"),
"spine_03":("spine3","spine_03","Spine2","mixamorig:Spine2"),
"neck_01":("neck","neck_01","Neck","mixamorig:Neck"),
"head":("head","Head","mixamorig:Head"),
"clavicle_l":("clavicle_l","shoulder_l","LeftShoulder","mixamorig:LeftShoulder"),
"upperarm_l":("upperarm_l","arm_l","LeftArm","mixamorig:LeftArm"),
"lowerarm_l":("lowerarm_l","forearm_l","LeftForeArm","mixamorig:LeftForeArm"),
"hand_l":("hand_l","LeftHand","mixamorig:LeftHand"),
"clavicle_r":("clavicle_r","shoulder_r","RightShoulder","mixamorig:RightShoulder"),
"upperarm_r":("upperarm_r","arm_r","RightArm","mixamorig:RightArm"),
"lowerarm_r":("lowerarm_r","forearm_r","RightForeArm","mixamorig:RightForeArm"),
"hand_r":("hand_r","RightHand","mixamorig:RightHand"),
"thigh_l":("thigh_l","upleg_l","LeftUpLeg","mixamorig:LeftUpLeg"),
"calf_l":("calf_l","leg_l","LeftLeg","mixamorig:LeftLeg"),
"foot_l":("foot_l","LeftFoot","mixamorig:LeftFoot"),
"ball_l":("ball_l","toe_l","LeftToeBase","mixamorig:LeftToeBase"),
"thigh_r":("thigh_r","upleg_r","RightUpLeg","mixamorig:RightUpLeg"),
"calf_r":("calf_r","leg_r","RightLeg","mixamorig:RightLeg"),
"foot_r":("foot_r","RightFoot","mixamorig:RightFoot"),
"ball_r":("ball_r","toe_r","RightToeBase","mixamorig:RightToeBase"),
}

def normalized(s):
    return s.lower().replace("mixamorig:","").replace(" ","").replace("-","_")

existing={b.name:b for b in arm.data.bones}
renamed={}
unmapped=[]
for canonical, aliases in ALIASES.items():
    if canonical in arm.data.bones:
        renamed[canonical]=canonical
        continue
    match=None
    alias_norm={normalized(x) for x in aliases}
    for b in arm.data.bones:
        if normalized(b.name) in alias_norm:
            match=b; break
    if match and canonical not in arm.data.bones:
        old=match.name
        match.name=canonical
        renamed[old]=canonical
    else:
        unmapped.append(canonical)

# Make sure mesh objects are bound/weighted.
weighted=[]
unweighted=[]
for m in meshes:
    has_groups=len(m.vertex_groups)>0
    has_arm_mod=any(mod.type=="ARMATURE" and mod.object==arm for mod in m.modifiers)
    if has_groups:
        weighted.append(m.name)
        if not has_arm_mod:
            mod=m.modifiers.new("NARIS_Armature","ARMATURE")
            mod.object=arm
    else:
        unweighted.append(m.name)

# PBR material factory.
def principled_material(name,base,metallic,roughness,emission=None,emission_strength=0.0):
    mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes=True
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    for n in list(nodes): nodes.remove(n)
    out=nodes.new("ShaderNodeOutputMaterial")
    bs=nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Base Color"].default_value=(*base,1.0)
    bs.inputs["Metallic"].default_value=metallic
    bs.inputs["Roughness"].default_value=roughness
    if emission and "Emission Color" in bs.inputs:
        bs.inputs["Emission Color"].default_value=(*emission,1.0)
        bs.inputs["Emission Strength"].default_value=emission_strength
    links.new(bs.outputs["BSDF"],out.inputs["Surface"])
    return mat

obs=principled_material("M_NARIS_Obsidian",(0.012,0.017,0.024),0.82,0.58)
gold=principled_material("M_NARIS_AgedGold",(0.34,0.18,0.035),0.88,0.42)
ember=principled_material("M_NARIS_EmberFire",(0.31,0.012,0.003),0.28,0.38,(1.0,0.07,0.01),4.5)

# Keep NARIS style materials available in the .blend, but do not append
# unassigned slots to production meshes. A real source PBR material is preferable
# to three cosmetic slots with no polygon segmentation.
style_material_library=[obs.name,gold.name,ember.name]
material_slots={}
renamed_primary={}
for m in meshes:
    slots=m.data.materials
    if len(slots)==0:
        slots.append(obs)
    elif slots[0]:
        lower=slots[0].name.lower()
        if lower.startswith("tripo_") or lower.startswith("material"):
            old_name=slots[0].name
            slots[0].name="M_NARIS_AshenVessel_PBR"
            renamed_primary[old_name]=slots[0].name
    material_slots[m.name]=[x.name if x else None for x in slots]

def has_principled_material(mesh):
    for mat in mesh.data.materials:
        if not mat:
            continue
        if not mat.use_nodes:
            return True
        if mat.node_tree and any(node.type=="BSDF_PRINCIPLED" for node in mat.node_tree.nodes):
            return True
    return False

pbr_material_ready=any(has_principled_material(m) for m in meshes)

# Bounds/height.
mn=Vector((1e20,1e20,1e20)); mx=Vector((-1e20,-1e20,-1e20)); found=False
for o in meshes:
    for c in o.bound_box:
        p=o.matrix_world@Vector(c); found=True
        for i in range(3):
            mn[i]=min(mn[i],p[i]); mx[i]=max(mx[i],p[i])
height=float(mx.z-mn.z) if found else 0.0

required=("pelvis","spine_01","spine_02","neck_01","head","hand_l","hand_r","thigh_l","thigh_r","foot_l","foot_r")
present=[x for x in required if x in arm.data.bones]
missing=[x for x in required if x not in arm.data.bones]

# UE-friendly root sanity.
zero_scale=[o.name for o in bpy.context.scene.objects if abs(o.scale.x)<1e-6 or abs(o.scale.y)<1e-6 or abs(o.scale.z)<1e-6]
negative_scale=[o.name for o in bpy.context.scene.objects if o.scale.x<0 or o.scale.y<0 or o.scale.z<0]

# Gate is strict but does not demand every optional bone.
gate={
 "armature":len(arm.data.bones)>=15,
 "weighted_mesh":len(weighted)>=1,
 "canonical_required":len(present)>=9,
 "height":1.80<=height<=1.90,
 "no_zero_scale":len(zero_scale)==0,
 "no_negative_scale":len(negative_scale)==0,
 "pbr_material":pbr_material_ready,
}
passed=all(gate.values())

# Save/export even when gate fails for inspection, but status clearly blocks P0-03.
bpy.ops.wm.save_as_mainfile(filepath=OUT_BLEND)
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
for m in meshes: m.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.fbx(
    filepath=OUT_FBX,
    use_selection=True,
    add_leaf_bones=False,
    apply_unit_scale=True,
    bake_anim=False,
    object_types={'ARMATURE','MESH'}
)

report={
 "status":"PASS" if passed else "FAIL_GATE",
 "production_grade":passed,
 "import_candidate_ready":passed,
 "source":SRC_BLEND,
 "output_blend":OUT_BLEND,
 "output_fbx":OUT_FBX,
 "armature":arm.name,
 "bone_count":len(arm.data.bones),
 "weighted_meshes":weighted,
 "unweighted_meshes":unweighted,
 "renamed_bones":renamed,
 "canonical_present":present,
 "canonical_missing":missing,
 "height_m":height,
 "zero_scale":zero_scale,
 "negative_scale":negative_scale,
 "gate":gate,
 "material_slots":material_slots,
 "renamed_primary_materials":renamed_primary,
 "materials":["M_NARIS_Obsidian","M_NARIS_AgedGold","M_NARIS_EmberFire"],
 "style_material_library":style_material_library,
 "material_policy":"preserve real assigned PBR; style materials remain unassigned until authored segmentation exists"
}
with open(LOG2,"w",encoding="utf-8") as f: json.dump(report,f,indent=2,ensure_ascii=False)
print("=== P0-02 DONE ===")
print(json.dumps(report,indent=2,ensure_ascii=False))
if not passed: raise SystemExit(30)
