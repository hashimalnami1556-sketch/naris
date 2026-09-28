import bpy, os, json, math
ROOT=r"C:\Users\Admin\NARIS"; OB=os.path.join(ROOT,"SourceAssets","Blender","RiggedV3"); OU=os.path.join(ROOT,"Pipeline","Exchange","FBX","RiggedV4"); ON=os.path.join(ROOT,"Pipeline","Exchange","UnityV4"); RP=os.path.join(ROOT,"Pipeline","Blender","RIG_UPGRADE_V3_REPORT.json")
for p in (OB,OU,ON): os.makedirs(p,exist_ok=True)
def action(arm,n,k,e,loop=False):
 a=bpy.data.actions.get(n) or bpy.data.actions.new(name=n); a.use_fake_user=True; arm.animation_data_create(); arm.animation_data.action=a
 for f,b,r in k:
  pb=arm.pose.bones.get(b)
  if pb: pb.rotation_mode='XYZ'; pb.rotation_euler=tuple(math.radians(v) for v in r); pb.keyframe_insert(data_path="rotation_euler",frame=f)
 a.frame_start=1; a.frame_end=e; a["NARIS_Loop"]=loop; arm.animation_data.action=None
 for pb in arm.pose.bones: pb.rotation_euler=(0,0,0)
def bone(arm,n,h,t,p):
 if n in arm.data.bones:return
 bpy.context.view_layer.objects.active=arm; arm.select_set(True); bpy.ops.object.mode_set(mode='EDIT'); b=arm.data.edit_bones.new(n); b.head=h;b.tail=t;b.parent=arm.data.edit_bones.get(p);bpy.ops.object.mode_set(mode='OBJECT')
def upgrade(path):
 bpy.ops.wm.open_mainfile(filepath=path); arm=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE'); n=os.path.splitext(os.path.basename(path))[0]
 if n=="SK_AshenVessel":
  bone(arm,"socket_back_weapon",(0,.10,1.40),(0,.26,1.44),"chest"); bone(arm,"socket_head_vfx",(0,0,1.93),(0,0,2.07),"head")
  action(arm,"AN_Ashen_Run",[(1,"thigh_l",(42,0,0)),(1,"thigh_r",(-42,0,0)),(8,"thigh_l",(-42,0,0)),(8,"thigh_r",(42,0,0)),(16,"thigh_l",(42,0,0)),(16,"thigh_r",(-42,0,0))],16,True)
  action(arm,"AN_Ashen_Parry",[(1,"upperarm_l",(0,0,10)),(5,"upperarm_l",(-35,0,-55)),(5,"lowerarm_l",(0,0,-45)),(12,"upperarm_l",(-35,0,-55)),(18,"upperarm_l",(0,0,0)),(18,"lowerarm_l",(0,0,0))],18)
  action(arm,"AN_Ashen_Resonance",[(1,"chest",(0,0,0)),(10,"chest",(-12,0,0)),(10,"upperarm_l",(0,0,-28)),(10,"upperarm_r",(0,0,28)),(26,"chest",(-12,0,0)),(38,"chest",(0,0,0)),(38,"upperarm_l",(0,0,0)),(38,"upperarm_r",(0,0,0))],38)
 elif n=="SK_CelestialWolf":
  bone(arm,"socket_companion_link",(0,-.05,.72),(0,-.05,.84),"spine"); action(arm,"AN_Wolf_SoulVision",[(1,"head",(0,0,0)),(8,"head",(-12,0,0)),(8,"neck",(-8,0,0)),(24,"head",(-12,0,0)),(36,"head",(0,0,0)),(36,"neck",(0,0,0))],36)
 else:
  bone(arm,"socket_roar_vfx",(0,.78,1.28),(0,.78,1.44),"head"); action(arm,"AN_Beast_Enrage",[(1,"chest",(0,0,0)),(8,"chest",(-12,0,-8)),(8,"head",(-18,0,0)),(18,"chest",(-12,0,8)),(28,"chest",(-12,0,-8)),(40,"chest",(0,0,0)),(40,"head",(0,0,0))],40)
 blend=os.path.join(OB,n+".blend");bpy.ops.wm.save_as_mainfile(filepath=blend);bpy.ops.object.select_all(action='DESELECT')
 for o in bpy.context.scene.objects:
  if o.type in {'MESH','ARMATURE'}:o.select_set(True)
 ue=os.path.join(OU,n+".fbx"); bpy.ops.export_scene.fbx(filepath=ue,use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Y',axis_up='Z',add_leaf_bones=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.0)
 un=os.path.join(ON,n+".fbx"); bpy.ops.export_scene.fbx(filepath=un,use_selection=True,object_types={'ARMATURE','MESH'},axis_forward='-Z',axis_up='Y',add_leaf_bones=False,use_mesh_modifiers=True,mesh_smooth_type='FACE',bake_anim=True,bake_anim_use_all_actions=True,bake_anim_use_nla_strips=False,bake_anim_simplify_factor=0.0)
 return {"blend":blend,"ue_fbx":ue,"unity_fbx":un,"bones":len(arm.data.bones),"actions":sorted(a.name for a in bpy.data.actions)}
src=os.path.join(ROOT,"SourceAssets","Blender","RiggedV2");r={}
for n in ("SK_AshenVessel","SK_CelestialWolf","SK_BoneBeast"):r[n]=upgrade(os.path.join(src,n+".blend"))
with open(RP,"w",encoding="utf-8") as f:json.dump(r,f,indent=2)
print("NARIS_RIG_V3_UPGRADE_OK",json.dumps(r))
