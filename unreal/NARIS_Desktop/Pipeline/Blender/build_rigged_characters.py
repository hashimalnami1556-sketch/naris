import bpy, math, os, json
from mathutils import Vector

ROOT=r"C:\Users\Admin\NARIS"
SRC=os.path.join(ROOT,"SourceAssets","Blender","Rigged")
OUT=os.path.join(ROOT,"Pipeline","Exchange","FBX","Rigged")
os.makedirs(SRC,exist_ok=True); os.makedirs(OUT,exist_ok=True)

def clear():
    bpy.ops.object.mode_set(mode='OBJECT') if bpy.context.object and bpy.context.object.mode!='OBJECT' else None
    bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
    for d in (bpy.data.meshes,bpy.data.armatures,bpy.data.actions):
        for x in list(d):
            if x.users==0: d.remove(x)

def make_armature(name,bones):
    data=bpy.data.armatures.new(name+"_Skeleton")
    obj=bpy.data.objects.new(name+"_Armature",data)
    bpy.context.collection.objects.link(obj)
    bpy.context.view_layer.objects.active=obj; obj.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    made={}
    for bname,head,tail,parent in bones:
        b=data.edit_bones.new(bname); b.head=head; b.tail=tail
        if parent: b.parent=made[parent]
        made[bname]=b
    bpy.ops.object.mode_set(mode='POSE')
    for pb in obj.pose.bones: pb.rotation_mode='XYZ'
    bpy.ops.object.mode_set(mode='OBJECT')
    return obj

def box_geo(center,size):
    cx,cy,cz=center; sx,sy,sz=[v*0.5 for v in size]
    v=[(cx+x*sx,cy+y*sy,cz+z*sz) for x,y,z in
       [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    f=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]
    return v,f

def make_weighted_mesh(name,arm,segments):
    verts=[]; faces=[]; ranges=[]
    for bone,center,size in segments:
        base=len(verts); v,f=box_geo(center,size); verts.extend(v); faces.extend(tuple(base+i for i in q) for q in f)
        ranges.append((bone,list(range(base,base+8))))
    mesh=bpy.data.meshes.new(name+"_Mesh"); mesh.from_pydata(verts,[],faces); mesh.update()
    obj=bpy.data.objects.new(name+"_Body",mesh); bpy.context.collection.objects.link(obj)
    for bone,idxs in ranges:
        vg=obj.vertex_groups.new(name=bone); vg.add(idxs,1.0,'REPLACE')
    mod=obj.modifiers.new("Armature","ARMATURE"); mod.object=arm
    obj.parent=arm
    return obj

def action(arm,name,keys,end):
    act=bpy.data.actions.new(name=name)
    arm.animation_data_create(); arm.animation_data.action=act
    for frame,bone,rot in keys:
        pb=arm.pose.bones.get(bone)
        if not pb: continue
        pb.rotation_euler=tuple(math.radians(x) for x in rot)
        pb.keyframe_insert(data_path="rotation_euler",frame=frame)
    act.frame_start=1; act.frame_end=end
    arm.animation_data.action=None
    for pb in arm.pose.bones: pb.rotation_euler=(0,0,0)
    return act

def finalize(name,arm):
    scene=bpy.context.scene; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=0.01
    blend=os.path.join(SRC,name+".blend")
    fbx=os.path.join(OUT,name+".fbx")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=fbx,object_types={'ARMATURE','MESH'},use_selection=True,
        apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',
        add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False)
    return {"blend":blend,"fbx":fbx,"bones":len(arm.data.bones),"actions":[a.name for a in bpy.data.actions]}

def build_ashen():
    clear(); n="SK_AshenVessel"
    B=[
    ("root",(0,0,0),(0,0,.2),None),("pelvis",(0,0,.78),(0,0,1.0),"root"),
    ("spine",(0,0,1.0),(0,0,1.28),"pelvis"),("chest",(0,0,1.28),(0,0,1.52),"spine"),
    ("neck",(0,0,1.52),(0,0,1.66),"chest"),("head",(0,0,1.66),(0,0,1.9),"neck"),
    ("upperarm_l",(-.18,0,1.47),(-.55,0,1.38),"chest"),("lowerarm_l",(-.55,0,1.38),(-.82,0,1.18),"upperarm_l"),("hand_l",(-.82,0,1.18),(-.94,0,1.12),"lowerarm_l"),
    ("upperarm_r",(.18,0,1.47),(.55,0,1.38),"chest"),("lowerarm_r",(.55,0,1.38),(.82,0,1.18),"upperarm_r"),("hand_r",(.82,0,1.18),(.94,0,1.12),"lowerarm_r"),
    ("thigh_l",(-.14,0,.82),(-.14,0,.44),"pelvis"),("shin_l",(-.14,0,.44),(-.14,0,.08),"thigh_l"),("foot_l",(-.14,0,.08),(-.14,-.22,.03),"shin_l"),
    ("thigh_r",(.14,0,.82),(.14,0,.44),"pelvis"),("shin_r",(.14,0,.44),(.14,0,.08),"thigh_r"),("foot_r",(.14,0,.08),(.14,-.22,.03),"shin_r")]
    arm=make_armature(n,B)
    seg=[("pelvis",(0,0,.88),(.38,.25,.25)),("spine",(0,0,1.16),(.36,.24,.36)),("chest",(0,0,1.4),(.52,.28,.34)),("head",(0,0,1.78),(.28,.28,.3))]
    for s,x in [("l",-1),("r",1)]:
        seg += [(f"upperarm_{s}",(.39*x,0,1.42),(.34,.18,.18)),(f"lowerarm_{s}",(.69*x,0,1.28),(.3,.15,.15)),(f"hand_{s}",(.88*x,0,1.15),(.16,.16,.16)),
                (f"thigh_{s}",(.14*x,0,.62),(.2,.22,.42)),(f"shin_{s}",(.14*x,0,.25),(.16,.18,.38)),(f"foot_{s}",(.14*x,-.11,.07),(.18,.34,.12))]
    make_weighted_mesh(n,arm,seg)
    action(arm,"AN_Ashen_Idle",[(1,"chest",(0,0,-2)),(15,"chest",(0,0,2)),(30,"chest",(0,0,-2))],30)
    action(arm,"AN_Ashen_Walk",[(1,"thigh_l",(28,0,0)),(1,"thigh_r",(-28,0,0)),(12,"thigh_l",(-28,0,0)),(12,"thigh_r",(28,0,0)),(24,"thigh_l",(28,0,0)),(24,"thigh_r",(-28,0,0))],24)
    action(arm,"AN_Ashen_Attack",[(1,"upperarm_r",(0,0,-35)),(8,"upperarm_r",(-35,20,55)),(8,"chest",(0,0,-22)),(16,"upperarm_r",(0,0,-35)),(16,"chest",(0,0,0))],16)
    return finalize(n,arm)

def build_wolf():
    clear(); n="SK_CelestialWolf"
    B=[("root",(0,0,.45),(0,.2,.45),None),("spine",(0,-.35,.48),(0,.35,.58),"root"),("neck",(0,.35,.58),(0,.58,.72),"spine"),("head",(0,.58,.72),(0,.82,.7),"neck"),("tail1",(0,-.35,.5),(0,-.65,.58),"spine"),("tail2",(0,-.65,.58),(0,-.92,.65),"tail1")]
    for side,x in [("l",-0.18),("r",0.18)]:
        for pos,y in [("front",.28),("back",-.28)]:
            B += [(f"{pos}_upper_{side}",(x,y,.48),(x,y,.24),"spine"),(f"{pos}_lower_{side}",(x,y,.24),(x,y,.06),f"{pos}_upper_{side}")]
    arm=make_armature(n,B)
    seg=[("spine",(0,0,.53),(.42,.82,.35)),("neck",(0,.47,.65),(.3,.35,.3)),("head",(0,.7,.72),(.34,.38,.3)),("tail1",(0,-.5,.56),(.18,.38,.18)),("tail2",(0,-.79,.62),(.14,.34,.14))]
    for side,x in [("l",-0.18),("r",0.18)]:
        for pos,y in [("front",.28),("back",-.28)]:
            seg += [(f"{pos}_upper_{side}",(x,y,.35),(.16,.16,.28)),(f"{pos}_lower_{side}",(x,y,.14),(.12,.14,.22))]
    make_weighted_mesh(n,arm,seg)
    action(arm,"AN_Wolf_Idle",[(1,"tail1",(0,0,-12)),(12,"tail1",(0,0,12)),(24,"tail1",(0,0,-12))],24)
    action(arm,"AN_Wolf_Run",[(1,"front_upper_l",(28,0,0)),(1,"back_upper_r",(28,0,0)),(1,"front_upper_r",(-28,0,0)),(1,"back_upper_l",(-28,0,0)),(10,"front_upper_l",(-28,0,0)),(10,"back_upper_r",(-28,0,0)),(10,"front_upper_r",(28,0,0)),(10,"back_upper_l",(28,0,0)),(20,"front_upper_l",(28,0,0))],20)
    action(arm,"AN_Wolf_Bite",[(1,"neck",(0,0,0)),(6,"neck",(24,0,0)),(6,"head",(-18,0,0)),(12,"neck",(0,0,0)),(12,"head",(0,0,0))],12)
    return finalize(n,arm)

def build_beast():
    clear(); n="SK_BoneBeast"
    B=[("root",(0,0,.55),(0,.15,.55),None),("pelvis",(0,-.22,.6),(0,0,.68),"root"),("spine",(0,0,.68),(0,.36,.84),"pelvis"),("chest",(0,.36,.84),(0,.58,1.0),"spine"),("neck",(0,.58,1.0),(0,.74,1.12),"chest"),("head",(0,.74,1.12),(0,1.0,1.12),"neck"),("jaw",(0,.78,1.08),(0,1.02,1.02),"head"),("tail",(0,-.22,.62),(0,-.62,.72),"pelvis")]
    for side,x in [("l",-0.26),("r",0.26)]:
        B += [(f"forearm_{side}",(x,.46,.82),(x,.45,.35),"chest"),(f"foreclaw_{side}",(x,.45,.35),(x,.55,.08),f"forearm_{side}"),
              (f"hindleg_{side}",(x,-.15,.58),(x,-.18,.24),"pelvis"),(f"hindclaw_{side}",(x,-.18,.24),(x,-.05,.06),f"hindleg_{side}")]
    arm=make_armature(n,B)
    seg=[("pelvis",(0,-.1,.64),(.5,.48,.38)),("spine",(0,.2,.78),(.58,.55,.42)),("chest",(0,.48,.94),(.72,.48,.48)),("head",(0,.87,1.11),(.48,.5,.38)),("jaw",(0,.91,1.03),(.42,.38,.18)),("tail",(0,-.42,.68),(.28,.55,.24))]
    for side,x in [("l",-0.26),("r",0.26)]:
        seg += [(f"forearm_{side}",(x,.46,.57),(.22,.22,.5)),(f"foreclaw_{side}",(x,.5,.2),(.22,.32,.28)),(f"hindleg_{side}",(x,-.17,.4),(.28,.3,.4)),(f"hindclaw_{side}",(x,-.1,.15),(.26,.38,.22))]
    make_weighted_mesh(n,arm,seg)
    action(arm,"AN_Beast_Idle",[(1,"head",(0,0,-4)),(15,"head",(0,0,4)),(30,"head",(0,0,-4))],30)
    action(arm,"AN_Beast_Run",[(1,"forearm_l",(24,0,0)),(1,"hindleg_r",(24,0,0)),(1,"forearm_r",(-24,0,0)),(1,"hindleg_l",(-24,0,0)),(10,"forearm_l",(-24,0,0)),(10,"hindleg_r",(-24,0,0)),(10,"forearm_r",(24,0,0)),(10,"hindleg_l",(24,0,0)),(20,"forearm_l",(24,0,0))],20)
    action(arm,"AN_Beast_Swipe",[(1,"forearm_r",(0,0,-10)),(7,"forearm_r",(-55,0,40)),(7,"chest",(0,0,-15)),(14,"forearm_r",(0,0,-10)),(14,"chest",(0,0,0))],14)
    return finalize(n,arm)

report={"AshenVessel":build_ashen(),"CelestialWolf":build_wolf(),"BoneBeast":build_beast()}
with open(os.path.join(ROOT,"Pipeline","Blender","RIG_EXPORT_REPORT.json"),"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
print("NARIS_RIG_EXPORT_SUCCESS",json.dumps(report))
