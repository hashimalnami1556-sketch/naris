# CALL OF NARIS — P0-BOSS-02 Ash Warden Rig / Animation / PBR Gate
# Blender 5.2+. Consumes P0-BOSS-01 candidate and exports a production candidate.
import bpy, os, sys, json, math, traceback
from pathlib import Path
from mathutils import Vector

PROJECT_ROOT=Path(r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57")
argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
BOSS_DIR=Path(argv[argv.index("--boss-dir")+1]) if "--boss-dir" in argv else PROJECT_ROOT/"Production"/"Boss"/"AshWarden"
LOG1=BOSS_DIR/"P0-BOSS_AshWarden_log.json"
SRC_BLEND=BOSS_DIR/"SK_AshWarden_Candidate.blend"
OUT_BLEND=BOSS_DIR/"SK_AshWarden_Production.blend"
OUT_FBX=BOSS_DIR/"SK_AshWarden_Production.fbx"
REPORT=BOSS_DIR/"P0-BOSS-02_rig_anim_pbr.json"

REQUIRED=("pelvis","spine_01","spine_02","neck_01","head","hand_l","hand_r","thigh_l","thigh_r","foot_l","foot_r")
ALIASES={
 "root":("root","Root","ROOT","armature"),
 "pelvis":("pelvis","hips","hip","Hips","mixamorig:Hips"),
 "spine_01":("spine","spine1","spine_01","Spine","mixamorig:Spine"),
 "spine_02":("spine2","spine_02","Spine1","mixamorig:Spine1"),
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

def fail(reason,extra=None,code=30):
    out={"status":"FAIL","production_grade":False,"reason":reason}
    if extra: out.update(extra)
    BOSS_DIR.mkdir(parents=True,exist_ok=True)
    REPORT.write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf-8")
    print(json.dumps(out,indent=2,ensure_ascii=False))
    raise SystemExit(code)

def norm(s):
    return s.lower().replace("mixamorig:","").replace(" ","").replace("-","_")

if not LOG1.is_file(): fail("missing_p0_boss_01_log")
g1=json.loads(LOG1.read_text(encoding="utf-8"))
if g1.get("status")!="PASS_CANDIDATE": fail("p0_boss_01_not_passed",{"gate":g1})
if not SRC_BLEND.is_file(): fail("missing_candidate_blend",{"path":str(SRC_BLEND)})

bpy.ops.wm.open_mainfile(filepath=str(SRC_BLEND))
arms=[o for o in bpy.data.objects if o.type=="ARMATURE"]
meshes=[o for o in bpy.data.objects if o.type=="MESH"]
if not arms: fail("no_armature")
if not meshes: fail("no_mesh")
arm=max(arms,key=lambda o:len(o.data.bones))
arm.name="SKEL_AshWarden"

# Canonicalize compatible humanoid names without destructively rebuilding the rig.
renamed={}
for canonical,aliases in ALIASES.items():
    if arm.data.bones.get(canonical): continue
    alias_norm={norm(a) for a in aliases}
    match=next((b for b in arm.data.bones if norm(b.name) in alias_norm),None)
    if match and not arm.data.bones.get(canonical):
        old=match.name; match.name=canonical; renamed[old]=canonical

present=[b for b in REQUIRED if arm.data.bones.get(b)]
missing=[b for b in REQUIRED if not arm.data.bones.get(b)]

weighted=[]
unweighted=[]
for m in meshes:
    # Halberd and decorative rigid parts may remain separate/static.
    if m.name.lower().startswith("sm_ashwarden_halberd"):
        continue
    if len(m.vertex_groups)>0:
        weighted.append(m.name)
        if not any(mod.type=="ARMATURE" and mod.object==arm for mod in m.modifiers):
            mod=m.modifiers.new("NARIS_Armature","ARMATURE");mod.object=arm
    else:
        unweighted.append(m.name)

# PBR materials: explicit NARIS boss language.
def make_mat(name,base,metal,rough,emit=None,strength=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True
    nodes=m.node_tree.nodes; links=m.node_tree.links
    for n in list(nodes): nodes.remove(n)
    out=nodes.new("ShaderNodeOutputMaterial")
    bs=nodes.new("ShaderNodeBsdfPrincipled")
    bs.inputs["Base Color"].default_value=(*base,1.0)
    bs.inputs["Metallic"].default_value=metal
    bs.inputs["Roughness"].default_value=rough
    if emit and "Emission Color" in bs.inputs:
        bs.inputs["Emission Color"].default_value=(*emit,1.0)
        bs.inputs["Emission Strength"].default_value=strength
    links.new(bs.outputs["BSDF"],out.inputs["Surface"])
    return m

pbr={
 "M_AshWarden_BlackenedSteel":make_mat("M_AshWarden_BlackenedSteel",(.012,.017,.022),.92,.42),
 "M_AshWarden_AgedBronze":make_mat("M_AshWarden_AgedBronze",(.24,.105,.025),.86,.47),
 "M_AshWarden_Burgundy":make_mat("M_AshWarden_Burgundy",(.11,.007,.014),.08,.74),
 "M_AshWarden_Ember":make_mat("M_AshWarden_Ember",(.26,.006,.002),.22,.32,(1.0,.045,.004),4.2),
}
for m in meshes:
    existing={x.name for x in m.data.materials if x}
    for name,mat in pbr.items():
        if name not in existing:m.data.materials.append(mat)

# Animation helpers.
if not arm.animation_data: arm.animation_data_create()
def pose_reset():
    for pb in arm.pose.bones:
        pb.rotation_mode='XYZ'
        pb.rotation_euler=(0,0,0)
        pb.location=(0,0,0)
        pb.scale=(1,1,1)

def key(pb,frame,rot=None,loc=None):
    if not pb:return
    pb.rotation_mode='XYZ'
    if rot is not None: pb.rotation_euler=rot
    if loc is not None: pb.location=loc
    pb.keyframe_insert("rotation_euler",frame=frame)
    pb.keyframe_insert("location",frame=frame)

def action(name,end,author):
    act=bpy.data.actions.get(name) or bpy.data.actions.new(name)
    # Clear existing curves if rerun.
    for fc in list(act.fcurves): act.fcurves.remove(fc)
    arm.animation_data.action=act
    pose_reset()
    author()
    act.frame_range=(1,end)
    return act

def pb(n): return arm.pose.bones.get(n)

def anim_idle():
    for f,z,lean in ((1,0,0),(30,.025,math.radians(1.5)),(60,0,0)):
        key(pb("pelvis"),f,loc=(0,0,z))
        key(pb("spine_02"),f,rot=(lean,0,0))
        key(pb("upperarm_l"),f,rot=(0,math.radians(-4),math.radians(-8)))
        key(pb("upperarm_r"),f,rot=(0,math.radians(4),math.radians(8)))

def anim_walk():
    for f,phase in ((1,1),(9,-1),(17,1),(25,-1),(33,1)):
        a=math.radians(26)*phase
        key(pb("thigh_l"),f,rot=(a,0,0));key(pb("thigh_r"),f,rot=(-a,0,0))
        key(pb("upperarm_l"),f,rot=(-a*.55,0,0));key(pb("upperarm_r"),f,rot=(a*.55,0,0))
        key(pb("pelvis"),f,loc=(0,0,.018 if phase<0 else 0))

def anim_attack():
    # Heavy halberd/body strike pose even when halberd remains a separate weapon asset.
    key(pb("spine_02"),1,rot=(0,0,0));key(pb("upperarm_r"),1,rot=(0,0,0));key(pb("lowerarm_r"),1,rot=(0,0,0))
    key(pb("spine_02"),12,rot=(math.radians(-10),math.radians(8),math.radians(-18)))
    key(pb("upperarm_r"),12,rot=(math.radians(-50),math.radians(-20),math.radians(35)))
    key(pb("lowerarm_r"),12,rot=(math.radians(-38),0,0))
    key(pb("spine_02"),24,rot=(math.radians(18),math.radians(-10),math.radians(28)))
    key(pb("upperarm_r"),24,rot=(math.radians(75),math.radians(10),math.radians(-30)))
    key(pb("lowerarm_r"),24,rot=(math.radians(28),0,0))
    key(pb("spine_02"),42,rot=(0,0,0));key(pb("upperarm_r"),42,rot=(0,0,0));key(pb("lowerarm_r"),42,rot=(0,0,0))

def anim_phase2():
    for f,s in ((1,0),(16,1),(32,-1),(48,0)):
        key(pb("pelvis"),f,loc=(0,0,.04 if s else 0))
        key(pb("spine_01"),f,rot=(math.radians(-5*s),0,0))
        key(pb("upperarm_l"),f,rot=(math.radians(-38*s),math.radians(12*s),math.radians(-22*s)))
        key(pb("upperarm_r"),f,rot=(math.radians(-38*s),math.radians(-12*s),math.radians(22*s)))
        key(pb("head"),f,rot=(math.radians(6*s),0,0))

def anim_hit():
    key(pb("spine_02"),1,rot=(0,0,0));key(pb("spine_02"),8,rot=(math.radians(-18),0,math.radians(8)));key(pb("spine_02"),20,rot=(0,0,0))
    key(pb("head"),8,rot=(math.radians(12),0,0))

def anim_death():
    key(pb("pelvis"),1,loc=(0,0,0));key(pb("spine_01"),1,rot=(0,0,0))
    key(pb("spine_01"),26,rot=(math.radians(22),0,math.radians(8)))
    key(pb("pelvis"),52,loc=(0,0,-.45));key(pb("spine_01"),52,rot=(math.radians(68),0,math.radians(12)))
    key(pb("head"),52,rot=(math.radians(30),0,0))
    key(pb("pelvis"),72,loc=(0,0,-.62));key(pb("spine_01"),72,rot=(math.radians(84),0,math.radians(15)))

actions=[
 action("A_AshWarden_Idle",60,anim_idle),
 action("A_AshWarden_Walk",33,anim_walk),
 action("A_AshWarden_Attack",42,anim_attack),
 action("A_AshWarden_Phase2",48,anim_phase2),
 action("A_AshWarden_HitReact",20,anim_hit),
 action("A_AshWarden_Death",72,anim_death),
]
for a in actions:
    a.use_fake_user=True

# Target height uses body bounds excluding weapon/runes that could distort scale.
def body_bounds():
    mn=Vector((1e20,1e20,1e20));mx=Vector((-1e20,-1e20,-1e20));found=False
    for o in meshes:
        if "halberd" in o.name.lower():continue
        found=True
        for c in o.bound_box:
            p=o.matrix_world@Vector(c)
            for i in range(3):mn[i]=min(mn[i],p[i]);mx[i]=max(mx[i],p[i])
    return (mn,mx) if found else (None,None)
mn,mx=body_bounds();height=float(mx.z-mn.z) if mn else 0.0

gate={
 "armature_bones_at_least_15":len(arm.data.bones)>=15,
 "canonical_required_at_least_9":len(present)>=9,
 "weighted_body_mesh":len(weighted)>=1,
 "six_actions":len(actions)==6,
 "four_pbr_materials":all(bpy.data.materials.get(n) for n in pbr),
 "body_height_reasonable":2.10<=height<=2.70,
}
passed=all(gate.values())

bpy.ops.wm.save_as_mainfile(filepath=str(OUT_BLEND))
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True)
for m in meshes:m.select_set(True)
bpy.context.view_layer.objects.active=arm
bpy.ops.export_scene.fbx(
 filepath=str(OUT_FBX),use_selection=True,add_leaf_bones=False,
 apply_unit_scale=True,bake_anim=True,bake_anim_use_all_actions=True,
 bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.0,
 object_types={'ARMATURE','MESH'}
)

report={
 "status":"PASS" if passed else "FAIL_GATE",
 "production_candidate":passed,
 "source_candidate_type":g1.get("candidate_type"),
 "source_used_procedural_fallback":bool(g1.get("used_procedural_fallback")),
 "armature":arm.name,
 "bone_count":len(arm.data.bones),
 "canonical_present":present,
 "canonical_missing":missing,
 "weighted_meshes":weighted,
 "unweighted_meshes":unweighted,
 "body_height_m":height,
 "actions":[{"name":a.name,"frame_range":[float(a.frame_range[0]),float(a.frame_range[1])]} for a in actions],
 "materials":list(pbr.keys()),
 "output_blend":str(OUT_BLEND),
 "output_fbx":str(OUT_FBX),
 "gate":gate,
 "final_art":False,
 "next_gate":"P0-BOSS-03 Unreal skeletal/animation/physics/LOD + D3D12 boss arena QA"
}
REPORT.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding="utf-8")
print("=== P0-BOSS-02 DONE ===")
print(json.dumps(report,indent=2,ensure_ascii=False))
if not passed: raise SystemExit(31)
