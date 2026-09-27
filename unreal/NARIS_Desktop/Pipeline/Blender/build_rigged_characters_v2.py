import bpy, math, os, json
ROOT=r"C:\Users\Admin\NARIS"
SRC=os.path.join(ROOT,"SourceAssets","Blender","RiggedV2")
OUT=os.path.join(ROOT,"Pipeline","Exchange","FBX","RiggedV2")
REPORT=os.path.join(ROOT,"Pipeline","Blender","RIG_EXPORT_REPORT_V2.json")
os.makedirs(SRC,exist_ok=True); os.makedirs(OUT,exist_ok=True)

PALETTE={
 "Obsidian":(0.011,0.014,0.022,1),
 "BurnedSteel":(0.035,0.043,0.055,1),
 "AncientGold":(0.56,0.40,0.16,1),
 "MistCyan":(0.055,0.62,0.72,1),
 "AetherViolet":(0.19,0.08,0.56,1),
 "NarisFire":(0.78,0.12,0.025,1),
 "Bone":(0.58,0.52,0.42,1)}
def mat(name, color, metallic=.0, rough=.5):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
 m.diffuse_color=color; m.metallic=metallic; m.roughness=rough
 return m

def clear():
 if bpy.context.object and bpy.context.object.mode!='OBJECT': bpy.ops.object.mode_set(mode='OBJECT')
 bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
 for a in list(bpy.data.actions): bpy.data.actions.remove(a)
 for datablocks in (bpy.data.meshes,bpy.data.armatures,bpy.data.materials):
  for d in list(datablocks):
   if d.users==0: datablocks.remove(d)

def armature(name,bones):
 data=bpy.data.armatures.new(name+"_Skeleton"); obj=bpy.data.objects.new(name+"_Armature",data)
 bpy.context.collection.objects.link(obj); bpy.context.view_layer.objects.active=obj; obj.select_set(True)
 bpy.ops.object.mode_set(mode='EDIT'); made={}
 for bname,head,tail,parent in bones:
  b=data.edit_bones.new(bname); b.head=head; b.tail=tail
  if parent: b.parent=made[parent]
  made[bname]=b
 bpy.ops.object.mode_set(mode='POSE')
 for pb in obj.pose.bones: pb.rotation_mode='XYZ'
 bpy.ops.object.mode_set(mode='OBJECT'); return obj
def cube_geo(center,size):
 cx,cy,cz=center; sx,sy,sz=[v*.5 for v in size]
 verts=[(cx+x*sx,cy+y*sy,cz+z*sz) for x,y,z in
 [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
 faces=[(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(4,0,3,7)]
 return verts,faces

def weighted_mesh(name,arm,segments,materials):
 verts=[]; faces=[]; ranges=[]
 for bone,center,size,mat_index in segments:
  base=len(verts); v,f=cube_geo(center,size); verts+=v; faces += [tuple(base+i for i in q) for q in f]
  ranges.append((bone,list(range(base,base+8)),mat_index))
 mesh=bpy.data.meshes.new(name+"_Mesh"); mesh.from_pydata(verts,[],faces); mesh.update()
 obj=bpy.data.objects.new(name+"_Body",mesh); bpy.context.collection.objects.link(obj)
 for m in materials: obj.data.materials.append(m)
 for bone,idxs,mi in ranges:
  vg=obj.vertex_groups.new(name=bone); vg.add(idxs,1.0,'REPLACE')
  for p in mesh.polygons:
   if any(v in idxs for v in p.vertices): p.material_index=min(mi,len(materials)-1)
 mod=obj.modifiers.new("Armature","ARMATURE"); mod.object=arm; obj.parent=arm
 for p in mesh.polygons: p.use_smooth=True
 return obj

def make_action(arm,name,keys,end,loop=False):
 act=bpy.data.actions.new(name=name); act.use_fake_user=True
 arm.animation_data_create(); arm.animation_data.action=act
 for frame,bone,rot in keys:
  pb=arm.pose.bones.get(bone)
  if not pb: continue
  pb.rotation_euler=tuple(math.radians(x) for x in rot); pb.keyframe_insert(data_path="rotation_euler",frame=frame)
 act.frame_start=1; act.frame_end=end; act["NARIS_Loop"]=bool(loop)
 arm.animation_data.action=None
 for pb in arm.pose.bones: pb.rotation_euler=(0,0,0)
 return act

def add_marker_bone(B,name,head,parent,tail_offset=(0,.08,0)):
 tail=(head[0]+tail_offset[0],head[1]+tail_offset[1],head[2]+tail_offset[2])
 B.append((name,head,tail,parent))
def finalize(name,arm):
 scene=bpy.context.scene; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=.01
 scene.render.fps=30
 for obj in bpy.context.scene.objects:
  if obj.type in {'MESH','ARMATURE'}:
   obj["NARIS_AssetID"]=name; obj["NARIS_UE_Ready"]=True
 blend=os.path.join(SRC,name+".blend"); fbx=os.path.join(OUT,name+".fbx")
 bpy.ops.wm.save_as_mainfile(filepath=blend)
 bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type in {'MESH','ARMATURE'}: o.select_set(True)
 bpy.ops.export_scene.fbx(filepath=fbx,use_selection=True,object_types={'ARMATURE','MESH'},
  apply_unit_scale=True,apply_scale_options='FBX_SCALE_ALL',axis_forward='-Y',axis_up='Z',
  add_leaf_bones=False,bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,
  mesh_smooth_type='FACE',use_armature_deform_only=False)
 return {"blend":blend,"fbx":fbx,"bones":len(arm.data.bones),"actions":sorted(a.name for a in bpy.data.actions)}

def build_ashen():
 clear(); n="SK_AshenVessel"
 B=[("root",(0,0,0),(0,0,.2),None),("pelvis",(0,0,.78),(0,0,1.0),"root"),
 ("spine",(0,0,1.0),(0,0,1.28),"pelvis"),("chest",(0,0,1.28),(0,0,1.52),"spine"),
 ("neck",(0,0,1.52),(0,0,1.66),"chest"),("head",(0,0,1.66),(0,0,1.9),"neck"),
 ("upperarm_l",(-.18,0,1.47),(-.55,0,1.38),"chest"),("lowerarm_l",(-.55,0,1.38),(-.82,0,1.18),"upperarm_l"),("hand_l",(-.82,0,1.18),(-.94,0,1.12),"lowerarm_l"),
 ("upperarm_r",(.18,0,1.47),(.55,0,1.38),"chest"),("lowerarm_r",(.55,0,1.38),(.82,0,1.18),"upperarm_r"),("hand_r",(.82,0,1.18),(.94,0,1.12),"lowerarm_r"),
 ("thigh_l",(-.14,0,.82),(-.14,0,.44),"pelvis"),("shin_l",(-.14,0,.44),(-.14,0,.08),"thigh_l"),("foot_l",(-.14,0,.08),(-.14,-.22,.03),"shin_l"),
 ("thigh_r",(.14,0,.82),(.14,0,.44),"pelvis"),("shin_r",(.14,0,.44),(.14,0,.08),"thigh_r"),("foot_r",(.14,0,.08),(.14,-.22,.03),"shin_r")]
 add_marker_bone(B,"socket_weapon_r",(.96,0,1.10),"hand_r",(0,.22,0))
 add_marker_bone(B,"socket_shield_l",(-.96,0,1.10),"hand_l",(0,.18,0))
 add_marker_bone(B,"ik_hand_r",(1.0,0,1.08),"root",(0,0,.12)); add_marker_bone(B,"ik_hand_l",(-1.0,0,1.08),"root",(0,0,.12))
 add_marker_bone(B,"ik_foot_r",(.14,-.22,.03),"root",(0,-.12,0)); add_marker_bone(B,"ik_foot_l",(-.14,-.22,.03),"root",(0,-.12,0))
 arm=armature(n,B)
 mats=[mat("M_Naris_Obsidian",PALETTE["Obsidian"],.35,.32),mat("M_Naris_Gold",PALETTE["AncientGold"],.75,.22),mat("M_Naris_Fire",PALETTE["NarisFire"],.05,.28)]
 seg=[("pelvis",(0,0,.88),(.38,.25,.25),0),("spine",(0,0,1.16),(.36,.24,.36),0),("chest",(0,0,1.4),(.52,.28,.34),1),("head",(0,0,1.78),(.28,.28,.3),0)]
 for s,x in [("l",-1),("r",1)]:
  seg += [(f"upperarm_{s}",(.39*x,0,1.42),(.34,.18,.18),0),(f"lowerarm_{s}",(.69*x,0,1.28),(.3,.15,.15),0),(f"hand_{s}",(.88*x,0,1.15),(.16,.16,.16),1),
          (f"thigh_{s}",(.14*x,0,.62),(.2,.22,.42),0),(f"shin_{s}",(.14*x,0,.25),(.16,.18,.38),0),(f"foot_{s}",(.14*x,-.11,.07),(.18,.34,.12),0)]
 weighted_mesh(n,arm,seg,mats)
 make_action(arm,"AN_Ashen_Idle",[(1,"chest",(0,0,-2)),(15,"chest",(0,0,2)),(30,"chest",(0,0,-2))],30,True)
 make_action(arm,"AN_Ashen_Walk",[(1,"thigh_l",(28,0,0)),(1,"thigh_r",(-28,0,0)),(12,"thigh_l",(-28,0,0)),(12,"thigh_r",(28,0,0)),(24,"thigh_l",(28,0,0)),(24,"thigh_r",(-28,0,0))],24,True)
 make_action(arm,"AN_Ashen_Attack_Light",[(1,"upperarm_r",(0,0,-35)),(8,"upperarm_r",(-35,20,55)),(8,"chest",(0,0,-22)),(16,"upperarm_r",(0,0,-35)),(16,"chest",(0,0,0))],16)
 make_action(arm,"AN_Ashen_Attack_Heavy",[(1,"upperarm_r",(10,0,-70)),(10,"upperarm_r",(-65,15,70)),(10,"chest",(0,0,-32)),(22,"upperarm_r",(0,0,-20)),(22,"chest",(0,0,0))],22)
 make_action(arm,"AN_Ashen_Dodge",[(1,"chest",(18,0,0)),(8,"chest",(-30,0,0)),(16,"chest",(10,0,0)),(22,"chest",(0,0,0))],22)
 make_action(arm,"AN_Ashen_HitReact",[(1,"chest",(0,0,0)),(4,"chest",(-18,0,16)),(10,"chest",(0,0,0))],10)
 return finalize(n,arm)
def build_wolf():
 clear(); n="SK_CelestialWolf"
 B=[("root",(0,0,.45),(0,.2,.45),None),("spine",(0,-.35,.48),(0,.35,.58),"root"),("neck",(0,.35,.58),(0,.58,.72),"spine"),("head",(0,.58,.72),(0,.82,.7),"neck"),("tail1",(0,-.35,.5),(0,-.65,.58),"spine"),("tail2",(0,-.65,.58),(0,-.92,.65),"tail1")]
 for side,x in [("l",-0.18),("r",0.18)]:
  for pos,y in [("front",.28),("back",-.28)]:
   B += [(f"{pos}_upper_{side}",(x,y,.48),(x,y,.24),"spine"),(f"{pos}_lower_{side}",(x,y,.24),(x,y,.06),f"{pos}_upper_{side}")]
 add_marker_bone(B,"socket_aether_core",(0,.12,.68),"spine",(0,0,.12)); add_marker_bone(B,"socket_muzzle",(0,.88,.72),"head",(0,.18,0))
 arm=armature(n,B); mats=[mat("M_Wolf_Spirit",PALETTE["MistCyan"],.05,.18),mat("M_Wolf_Aether",PALETTE["AetherViolet"],.1,.2)]
 seg=[("spine",(0,0,.53),(.42,.82,.35),0),("neck",(0,.47,.65),(.3,.35,.3),0),("head",(0,.7,.72),(.34,.38,.3),1),("tail1",(0,-.5,.56),(.18,.38,.18),0),("tail2",(0,-.79,.62),(.14,.34,.14),0)]
 for side,x in [("l",-0.18),("r",0.18)]:
  for pos,y in [("front",.28),("back",-.28)]:
   seg += [(f"{pos}_upper_{side}",(x,y,.35),(.16,.16,.28),0),(f"{pos}_lower_{side}",(x,y,.14),(.12,.14,.22),0)]
 weighted_mesh(n,arm,seg,mats)
 make_action(arm,"AN_Wolf_Idle",[(1,"tail1",(0,0,-12)),(12,"tail1",(0,0,12)),(24,"tail1",(0,0,-12))],24,True)
 make_action(arm,"AN_Wolf_Run",[(1,"front_upper_l",(28,0,0)),(1,"back_upper_r",(28,0,0)),(10,"front_upper_l",(-28,0,0)),(10,"back_upper_r",(-28,0,0)),(20,"front_upper_l",(28,0,0))],20,True)
 make_action(arm,"AN_Wolf_Bite",[(1,"neck",(0,0,0)),(6,"neck",(24,0,0)),(6,"head",(-18,0,0)),(12,"neck",(0,0,0)),(12,"head",(0,0,0))],12)
 make_action(arm,"AN_Wolf_Roar",[(1,"head",(0,0,0)),(8,"head",(-22,0,0)),(18,"head",(-22,0,0)),(28,"head",(0,0,0))],28)
 make_action(arm,"AN_Wolf_Dash",[(1,"spine",(0,0,0)),(6,"spine",(14,0,0)),(12,"spine",(-8,0,0)),(18,"spine",(0,0,0))],18)
 return finalize(n,arm)

def build_beast():
 clear(); n="SK_BoneBeast"
 B=[("root",(0,0,.55),(0,.15,.55),None),("pelvis",(0,-.22,.6),(0,0,.68),"root"),("spine",(0,0,.68),(0,.36,.84),"pelvis"),("chest",(0,.36,.84),(0,.58,1.0),"spine"),("neck",(0,.58,1.0),(0,.74,1.12),"chest"),("head",(0,.74,1.12),(0,1.0,1.12),"neck"),("jaw",(0,.78,1.08),(0,1.02,1.02),"head"),("tail",(0,-.22,.62),(0,-.62,.72),"pelvis")]
 for side,x in [("l",-0.26),("r",0.26)]:
  B += [(f"forearm_{side}",(x,.46,.82),(x,.45,.35),"chest"),(f"foreclaw_{side}",(x,.45,.35),(x,.55,.08),f"forearm_{side}"),(f"hindleg_{side}",(x,-.15,.58),(x,-.18,.24),"pelvis"),(f"hindclaw_{side}",(x,-.18,.24),(x,-.05,.06),f"hindleg_{side}")]
 add_marker_bone(B,"hit_head",(0,.9,1.15),"head",(0,.12,0)); add_marker_bone(B,"hit_core",(0,.35,.82),"chest",(0,0,.12))
 add_marker_bone(B,"hit_tail",(0,-.72,.72),"tail",(0,-.12,0)); add_marker_bone(B,"socket_mouth_vfx",(0,1.05,1.08),"head",(0,.15,0))
 arm=armature(n,B); mats=[mat("M_Beast_Bone",PALETTE["Bone"],.05,.48),mat("M_Beast_Obsidian",PALETTE["Obsidian"],.28,.35),mat("M_Beast_Fire",PALETTE["NarisFire"],.05,.22)]
 seg=[("pelvis",(0,-.1,.64),(.5,.48,.38),1),("spine",(0,.2,.78),(.58,.55,.42),1),("chest",(0,.48,.94),(.72,.48,.48),0),("head",(0,.87,1.11),(.48,.5,.38),0),("jaw",(0,.91,1.03),(.42,.38,.18),2),("tail",(0,-.42,.68),(.28,.55,.24),0)]
 for side,x in [("l",-0.26),("r",0.26)]:
  seg += [(f"forearm_{side}",(x,.46,.57),(.22,.22,.5),0),(f"foreclaw_{side}",(x,.5,.2),(.22,.32,.28),2),(f"hindleg_{side}",(x,-.17,.4),(.28,.3,.4),0),(f"hindclaw_{side}",(x,-.1,.15),(.26,.38,.22),2)]
 weighted_mesh(n,arm,seg,mats)
 make_action(arm,"AN_Beast_Idle",[(1,"head",(0,0,-4)),(15,"head",(0,0,4)),(30,"head",(0,0,-4))],30,True)
 make_action(arm,"AN_Beast_Run",[(1,"forearm_l",(24,0,0)),(1,"hindleg_r",(24,0,0)),(10,"forearm_l",(-24,0,0)),(10,"hindleg_r",(-24,0,0)),(20,"forearm_l",(24,0,0))],20,True)
 make_action(arm,"AN_Beast_Swipe",[(1,"forearm_r",(0,0,-10)),(7,"forearm_r",(-55,0,40)),(7,"chest",(0,0,-15)),(14,"forearm_r",(0,0,-10)),(14,"chest",(0,0,0))],14)
 make_action(arm,"AN_Beast_Roar",[(1,"head",(0,0,0)),(8,"head",(-25,0,0)),(8,"jaw",(28,0,0)),(24,"head",(-25,0,0)),(24,"jaw",(28,0,0)),(34,"head",(0,0,0)),(34,"jaw",(0,0,0))],34)
 make_action(arm,"AN_Beast_TailSweep",[(1,"tail",(0,0,-35)),(8,"tail",(0,0,65)),(16,"tail",(0,0,-20)),(22,"tail",(0,0,0))],22)
 make_action(arm,"AN_Beast_Stunned",[(1,"head",(0,0,0)),(6,"head",(32,0,0)),(24,"head",(32,0,0)),(36,"head",(0,0,0))],36)
 return finalize(n,arm)

report={"version":2,"AshenVessel":build_ashen(),"CelestialWolf":build_wolf(),"BoneBeast":build_beast()}
with open(REPORT,"w",encoding="utf-8") as f: json.dump(report,f,indent=2)
print("NARIS_RIG_V2_SUCCESS",json.dumps(report))
