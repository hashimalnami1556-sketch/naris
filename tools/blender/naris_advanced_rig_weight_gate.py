# NARIS Advanced Organic Rig — production weight/deformation gate
# Run inside Blender 4.x. It audits the ACTIVE production mesh/armature without fabricating PASS.
import bpy, json, math
from pathlib import Path

TARGETS={"Ash Wanderer":92,"Bone Hound":82,"Demon Warrior":106,"Aether Serpent":78,"Dragon":146}
MAX_INFLUENCES=4
POSE_DEG=30.0

def mesh_armature_pairs():
    out=[]
    for obj in bpy.data.objects:
        if obj.type!="MESH": continue
        arm=None
        for m in obj.modifiers:
            if m.type=="ARMATURE" and m.object: arm=m.object; break
        if arm: out.append((obj,arm))
    return out

def classify(name):
    s=name.lower().replace("_"," ")
    for k in TARGETS:
        if all(t in s for t in k.lower().split()): return k
    return None

def weight_audit(mesh):
    unweighted=[]; over=[]; normalized_errors=[]; vertex_rows=[]
    for v in mesh.data.vertices:
        ws=[g.weight for g in v.groups if g.weight>1e-6]
        total=sum(ws)
        if not ws: unweighted.append(v.index)
        if len(ws)>MAX_INFLUENCES: over.append((v.index,len(ws)))
        if ws and abs(total-1.0)>0.02: normalized_errors.append((v.index,total))
        vertex_rows.append({"vertex":v.index,"influences":len(ws),"sum":round(total,6)})
    return {"vertices":len(mesh.data.vertices),"unweighted_count":len(unweighted),
            "over_4_influences_count":len(over),"non_normalized_count":len(normalized_errors),
            "unweighted_sample":unweighted[:50],"over_4_sample":over[:50],
            "non_normalized_sample":normalized_errors[:50]}

def side_bleed(mesh):
    # Conservative naming-based L/R bleed detector. Does not infer anatomy.
    groups={g.index:g.name.lower() for g in mesh.vertex_groups}
    suspects=[]
    for v in mesh.data.vertices:
        names=[groups.get(g.group,"") for g in v.groups if g.weight>0.05]
        has_l=any(n.endswith((".l","_l"," left")) or "left" in n for n in names)
        has_r=any(n.endswith((".r","_r"," right")) or "right" in n for n in names)
        if has_l and has_r: suspects.append(v.index)
    return {"lr_bleed_suspect_count":len(suspects),"sample":suspects[:50]}

def pose_stress(arm):
    # Applies ±30° sequentially to deform bones, records test coverage, restores pose.
    tested=[]
    bpy.context.view_layer.objects.active=arm
    arm.select_set(True)
    for pb in arm.pose.bones:
        if not pb.bone.use_deform: continue
        old=pb.rotation_mode; pb.rotation_mode='XYZ'
        base=pb.rotation_euler.copy()
        for sign in (1,-1):
            pb.rotation_euler.x=base.x+math.radians(POSE_DEG*sign)
            bpy.context.view_layer.update()
        pb.rotation_euler=base; pb.rotation_mode=old
        tested.append(pb.name)
    bpy.context.view_layer.update()
    return tested

report={"schema":"naris.advanced-rig-weight-gate.v1","max_influences":MAX_INFLUENCES,
        "stress_pose_degrees":POSE_DEG,"characters":[],"overall":"PENDING"}
for mesh,arm in mesh_armature_pairs():
    kind=classify(mesh.name+" "+arm.name)
    target=TARGETS.get(kind)
    weights=weight_audit(mesh); bleed=side_bleed(mesh); tested=pose_stress(arm)
    bone_count=len([b for b in arm.data.bones if b.use_deform])
    structural=bool(target and bone_count>=target)
    numeric=(weights["unweighted_count"]==0 and weights["over_4_influences_count"]==0 and
             weights["non_normalized_count"]==0 and bleed["lr_bleed_suspect_count"]==0)
    # Visual deformation is intentionally not auto-passed.
    report["characters"].append({"class":kind or "UNCLASSIFIED","mesh":mesh.name,"armature":arm.name,
      "deform_bones":bone_count,"target_bones":target,"structural_target_met":structural,
      "weights":weights,"bleed":bleed,"stress_bones_tested":len(tested),
      "numeric_weight_gate":"PASS" if numeric else "FAIL",
      "visual_deformation_gate":"PENDING_ARTIST_REVIEW",
      "production_candidate":False})
out=Path(bpy.path.abspath("//"))/"Saved"/"TestReports"/"naris_advanced_rig_weight_gate.json"
out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,indent=2),encoding="utf-8")
print("NARIS_ADVANCED_RIG_WEIGHT_GATE",out)
