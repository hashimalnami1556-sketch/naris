# CALL OF NARIS — P0-BOSS Ash Warden One-Shot
# Blender 5.2+. Produces a unique boss candidate; never reuses BoneBeast as final art.
import bpy, os, sys, glob, json, math, traceback
from mathutils import Vector

PROJECT_ROOT=r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
argv=sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
OUT=argv[argv.index("--out")+1] if "--out" in argv else os.path.join(PROJECT_ROOT,"Production","Boss","AshWarden")
os.makedirs(OUT,exist_ok=True)

ROOTS=[
 os.path.join(PROJECT_ROOT,"SourceAssets"),
 os.path.join(PROJECT_ROOT,"Pipeline","Exchange","FBX"),
 os.path.join(PROJECT_ROOT,"Pipeline","Exchange","GLB"),
 os.path.join(PROJECT_ROOT,"Assets","Characters"),
]
MODEL_EXTS=("*.fbx","*.glb","*.gltf","*.blend")
BOSS_WORDS=("warden","guardian","sentinel","knight","giant","boss","ash","gatekeeper","armor","warrior")
BAD_WORDS=("wolf","beast","dog","city","tree","rock","environment")
HUMANOID_BONES=("pelvis","hips","spine","head","hand","upperarm","lowerarm","thigh","calf","foot")

def uniq(xs):
    seen=set(); out=[]
    for x in xs:
        k=os.path.normcase(os.path.abspath(x))
        if k not in seen:
            seen.add(k); out.append(os.path.abspath(x))
    return out

candidates=[]
for root in ROOTS:
    if not os.path.isdir(root): continue
    for ext in MODEL_EXTS:
        candidates+=glob.glob(os.path.join(root,"**",ext),recursive=True)
candidates=uniq(candidates)

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def import_any(path):
    ext=os.path.splitext(path)[1].lower()
    if ext==".fbx": bpy.ops.import_scene.fbx(filepath=path,automatic_bone_orientation=False)
    elif ext in (".glb",".gltf"): bpy.ops.import_scene.gltf(filepath=path)
    elif ext==".blend":
        with bpy.data.libraries.load(path,link=False) as (src,dst):
            dst.objects=list(src.objects)
        for o in dst.objects:
            if o:
                try:bpy.context.scene.collection.objects.link(o)
                except:pass
    else: raise RuntimeError(ext)

def bounds():
    mn=Vector((1e20,1e20,1e20)); mx=Vector((-1e20,-1e20,-1e20)); found=False
    for o in bpy.data.objects:
        if o.type!="MESH": continue
        found=True
        for c in o.bound_box:
            p=o.matrix_world@Vector(c)
            for i in range(3):
                mn[i]=min(mn[i],p[i]); mx[i]=max(mx[i],p[i])
    return (mn,mx) if found else (None,None)

def score(path):
    reset()
    try: import_any(path)
    except Exception as e: return {"path":path,"score":-999,"error":str(e)}
    tris=bones=arms=weighted=0; bone_names=[]; mats=set()
    for o in bpy.data.objects:
        if o.type=="MESH":
            tris+=sum(max(0,len(p.vertices)-2) for p in o.data.polygons)
            if len(o.vertex_groups)>=8: weighted+=1
            for m in o.data.materials:
                if m:mats.add(m.name.lower())
        elif o.type=="ARMATURE":
            arms+=1; bones+=len(o.data.bones); bone_names += [b.name.lower() for b in o.data.bones]
    path_l=path.lower()
    boss_hits=sum(1 for w in BOSS_WORDS if w in path_l)
    bad_hits=sum(1 for w in BAD_WORDS if w in path_l)
    hum=sum(1 for w in HUMANOID_BONES if any(w in b for b in bone_names))
    mn,mx=bounds(); z=(mx.z-mn.z) if mn else 0
    plausible=max(z,z/100.0) if z else 0
    s=min(tris,220000)/220000*16 + min(bones,180)/180*20 + min(hum,9)/9*28
    s+=min(boss_hits,6)*6 + (8 if arms else -18) + (8 if weighted else -8) - bad_hits*10
    return {"path":path,"score":round(s,2),"tris":tris,"bones":bones,"humanoid_hits":hum,"boss_hits":boss_hits,"bad_hits":bad_hits,"materials":sorted(mats)}

def mat(name,color,metal,rough,emit=None):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color=(*color,1);m.metallic=metal;m.roughness=rough
    if emit:
        m.use_nodes=True
        bs=next((n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None)
        if bs and "Emission Color" in bs.inputs:
            bs.inputs["Emission Color"].default_value=(*emit,1)
            bs.inputs["Emission Strength"].default_value=3.2
    return m

def add_uv_sphere(name,loc,scale,material):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=3,radius=1,location=loc)
    o=bpy.context.object;o.name=name;o.scale=scale
    o.data.materials.append(material);return o

def add_cube(name,loc,scale,material,bevel=.08):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.object;o.name=name;o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    bev=o.modifiers.new("Bevel","BEVEL");bev.width=bevel;bev.segments=3
    bpy.context.view_layer.objects.active=o
    bpy.ops.object.modifier_apply(modifier=bev.name)
    o.data.materials.append(material);return o

def procedural_fallback():
    reset()
    obs=mat("M_AshWarden_BlackenedSteel",(0.018,.022,.027),.92,.42)
    bronze=mat("M_AshWarden_AgedBronze",(.22,.10,.025),.86,.48)
    ember=mat("M_AshWarden_Ember",(.28,.008,.002),.25,.34,(1.0,.05,.005))
    cloth=mat("M_AshWarden_Burgundy",(.12,.008,.014),.08,.72)

    # 2.45m monumental humanoid silhouette
    add_cube("TorsoArmor",(0,0,1.62),(.46,.28,.55),obs,.12)
    add_cube("PelvisArmor",(0,0,1.05),(.34,.25,.24),bronze,.08)
    add_uv_sphere("Helmet",(0,0,2.23),(.32,.29,.38),obs)
    # Crown/horns
    for sx in (-1,1):
        bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=.10,radius2=.025,depth=.52,location=(sx*.27,0,2.52))
        h=bpy.context.object;h.name=f"CrownHorn_{sx:+d}";h.rotation_euler[1]=math.radians(sx*16);h.data.materials.append(bronze)
    # shoulders / arms
    for sx in (-1,1):
        add_cube(f"Pauldron_{sx:+d}",(sx*.55,0,1.85),(.25,.34,.22),obs,.10)
        add_cube(f"UpperArm_{sx:+d}",(sx*.62,0,1.42),(.16,.17,.38),obs,.06)
        add_cube(f"Forearm_{sx:+d}",(sx*.64,0,1.03),(.18,.18,.30),bronze,.06)
        add_cube(f"Hand_{sx:+d}",(sx*.64,0,.77),(.14,.15,.16),obs,.05)
        add_cube(f"Thigh_{sx:+d}",(sx*.22,0,.66),(.19,.21,.38),obs,.06)
        add_cube(f"Shin_{sx:+d}",(sx*.22,0,.28),(.17,.19,.34),bronze,.06)
        add_cube(f"Boot_{sx:+d}",(sx*.22,-.05,.04),(.20,.29,.12),obs,.05)

    # burgundy tabard + ember chest core
    add_cube("BurgundyTabard",(0,-.30,1.20),(.25,.035,.62),cloth,.025)
    add_uv_sphere("EmberCore",(0,-.295,1.72),(.11,.055,.15),ember)

    # boss halberd on right side
    bpy.ops.mesh.primitive_cylinder_add(vertices=16,radius=.045,depth=2.35,location=(.95,0,1.05))
    shaft=bpy.context.object;shaft.name="SM_AshWarden_Halberd_Shaft";shaft.data.materials.append(bronze)
    add_cube("SM_AshWarden_Halberd_Blade",(.95,0,2.23),(.34,.07,.20),obs,.04)
    add_uv_sphere("Halberd_EmberRune",(.95,-.08,2.23),(.07,.035,.09),ember)

    # armature canonical boss humanoid
    bpy.ops.object.armature_add(enter_editmode=True,location=(0,0,0))
    arm=bpy.context.object;arm.name="SKEL_AshWarden"
    eb=arm.data.edit_bones
    root=eb[0];root.name="root";root.head=(0,0,0);root.tail=(0,0,.18)
    def bone(name,head,tail,parent=None):
        b=eb.new(name);b.head=head;b.tail=tail;b.parent=parent;return b
    pelvis=bone("pelvis",(0,0,.88),(0,0,1.14),root)
    sp1=bone("spine_01",(0,0,1.14),(0,0,1.46),pelvis)
    sp2=bone("spine_02",(0,0,1.46),(0,0,1.82),sp1)
    neck=bone("neck_01",(0,0,1.82),(0,0,2.04),sp2)
    head=bone("head",(0,0,2.04),(0,0,2.42),neck)
    for side,sx in (("l",-1),("r",1)):
        clav=bone(f"clavicle_{side}",(0,0,1.80),(sx*.34,0,1.82),sp2)
        ua=bone(f"upperarm_{side}",(sx*.34,0,1.82),(sx*.62,0,1.43),clav)
        la=bone(f"lowerarm_{side}",(sx*.62,0,1.43),(sx*.64,0,.98),ua)
        bone(f"hand_{side}",(sx*.64,0,.98),(sx*.64,0,.72),la)
        th=bone(f"thigh_{side}",(sx*.18,0,1.02),(sx*.22,0,.55),pelvis)
        ca=bone(f"calf_{side}",(sx*.22,0,.55),(sx*.22,0,.16),th)
        fo=bone(f"foot_{side}",(sx*.22,0,.16),(sx*.22,-.25,.05),ca)
        bone(f"ball_{side}",(sx*.22,-.25,.05),(sx*.22,-.40,.05),fo)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Bind visible body pieces (except halberd) with automatic weights.
    body=[o for o in bpy.data.objects if o.type=="MESH" and not o.name.startswith("SM_AshWarden_Halberd")]
    bpy.ops.object.select_all(action="DESELECT")
    for o in body:o.select_set(True)
    arm.select_set(True);bpy.context.view_layer.objects.active=arm
    try:bpy.ops.object.parent_set(type="ARMATURE_AUTO")
    except Exception as e: print("AUTO_WEIGHT_WARNING",e)
    return arm

results=[]
for i,p in enumerate(candidates,1):
    try:r=score(p)
    except Exception:r={"path":p,"score":-999,"error":traceback.format_exc()}
    results.append(r);print(f"[{i}/{len(candidates)}] {r.get('score')} {os.path.basename(p)}")
results.sort(key=lambda x:x.get("score",-999),reverse=True)
winner=results[0] if results else None

THRESH=60.0
used_fallback=False
if winner and winner.get("score",-999)>=THRESH and winner.get("humanoid_hits",0)>=5 and winner.get("bad_hits",0)==0:
    reset();import_any(winner["path"])
    status="SOURCE_CANDIDATE"
else:
    procedural_fallback();used_fallback=True;status="PROCEDURAL_UNIQUE_CANDIDATE"

# normalize entire asset to 2.45 Blender units.
mn,mx=bounds()
if mn:
    cur=mx.z-mn.z
    if cur>1e-6:
        factor=2.45/cur
        roots=[o for o in bpy.context.scene.objects if o.parent is None]
        for o in roots:o.scale=tuple(v*factor for v in o.scale)
        bpy.context.view_layer.update()

blend=os.path.join(OUT,"SK_AshWarden_Candidate.blend")
fbx=os.path.join(OUT,"SK_AshWarden_Candidate.fbx")
bpy.ops.wm.save_as_mainfile(filepath=blend)
bpy.ops.export_scene.fbx(filepath=fbx,use_selection=False,add_leaf_bones=False,apply_unit_scale=True,bake_anim=False)

armatures=[o for o in bpy.data.objects if o.type=="ARMATURE"]
meshes=[o for o in bpy.data.objects if o.type=="MESH"]
report={
 "status":"PASS_CANDIDATE",
 "production_grade":False,
 "candidate_type":status,
 "used_procedural_fallback":used_fallback,
 "winner":winner,
 "top10":results[:10],
 "output_blend":blend,
 "output_fbx":fbx,
 "armatures":[{"name":a.name,"bones":len(a.data.bones)} for a in armatures],
 "mesh_count":len(meshes),
 "final_gate":"Unreal import + boss skeleton/animation + PBR + D3D12 visual/combat QA required before replacing proxy."
}
with open(os.path.join(OUT,"P0-BOSS_AshWarden_log.json"),"w",encoding="utf-8") as f:
    json.dump(report,f,indent=2,ensure_ascii=False)
print(json.dumps(report,indent=2,ensure_ascii=False))
