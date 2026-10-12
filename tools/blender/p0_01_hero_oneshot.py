# CALL OF NARIS — P0-01 Hero One-Shot Production Pass
# Blender 5.2+
import bpy, sys, os, glob, json, traceback
from mathutils import Vector

PROJECT_ROOT = r"C:\Users\Admin\OneDrive\NARIS_MASTER_BUNDLE\Game\NARIS_UE57"
argv = sys.argv[sys.argv.index("--")+1:] if "--" in sys.argv else []
OUT = argv[argv.index("--out")+1] if "--out" in argv else os.path.join(PROJECT_ROOT,"Production","Hero")
os.makedirs(OUT, exist_ok=True)

ROOTS = [
    os.path.join(PROJECT_ROOT,"Pipeline","Exchange","FBX"),
    os.path.join(PROJECT_ROOT,"Pipeline","Exchange","GLB"),
    os.path.join(PROJECT_ROOT,"Assets","Characters"),
    os.path.join(PROJECT_ROOT,"SourceAssets"),
    r"C:\Users\Admin\NARIS\Pipeline\BlenderAAA\Exports",
]
MODEL_EXTS=("*.fbx","*.glb","*.gltf","*.blend")
IMAGE_EXTS=("*.png","*.jpg","*.jpeg","*.tga","*.exr")
HERO_WORDS=("ashen","vessel","naris","hero","character","warrior","knight","nomad")
BAD_WORDS=("city","environment","rock","tree","gate","bridge","shrine","chest","building","ruin")
BONE_HINTS=("root","pelvis","hips","spine","neck","head","clavicle","upperarm","lowerarm","hand","thigh","calf","foot")
SWORD_WORDS=("sword","blade","katana","greatsword")

def uniq(items):
    seen=set(); out=[]
    for item in items:
        key=os.path.normcase(os.path.abspath(item))
        if key not in seen:
            seen.add(key); out.append(os.path.abspath(item))
    return out

models=[]; images=[]
for root in ROOTS:
    if not os.path.isdir(root): continue
    for ext in MODEL_EXTS: models += glob.glob(os.path.join(root,"**",ext),recursive=True)
    for ext in IMAGE_EXTS: images += glob.glob(os.path.join(root,"**",ext),recursive=True)
models=uniq(models); images=uniq(images)

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def import_any(path):
    ext=os.path.splitext(path)[1].lower()
    if ext==".fbx":
        bpy.ops.import_scene.fbx(filepath=path,automatic_bone_orientation=False)
    elif ext in (".glb",".gltf"):
        bpy.ops.import_scene.gltf(filepath=path)
    elif ext==".blend":
        with bpy.data.libraries.load(path,link=False) as (src,dst):
            dst.objects=[n for n in src.objects]
        col=bpy.context.scene.collection
        for obj in dst.objects:
            if obj:
                try: col.objects.link(obj)
                except RuntimeError: pass
    else:
        raise RuntimeError("Unsupported format: "+ext)

def world_bounds():
    mn=Vector((1e20,1e20,1e20)); mx=Vector((-1e20,-1e20,-1e20)); found=False
    for obj in bpy.data.objects:
        if obj.type!="MESH": continue
        found=True
        for corner in obj.bound_box:
            p=obj.matrix_world @ Vector(corner)
            for i in range(3):
                mn[i]=min(mn[i],p[i]); mx[i]=max(mx[i],p[i])
    return (mn,mx) if found else (None,None)

def plausible_height_m(mn,mx):
    if mn is None: return 0.0
    z=float(mx.z-mn.z)
    choices=(z,z/100.0,z*100.0)
    plausible=[v for v in choices if .5<=v<=4.0]
    return min(plausible,key=lambda v:abs(v-1.85)) if plausible else z

def score(path):
    reset_scene()
    try:
        import_any(path)
    except Exception as exc:
        return {"path":path,"score":-999.0,"error":str(exc)}
    tris=verts=bones=armatures=weighted=0
    materials=set(); bone_names=[]; has_sword=False
    for obj in bpy.data.objects:
        if obj.type=="MESH":
            verts+=len(obj.data.vertices)
            tris+=sum(max(0,len(p.vertices)-2) for p in obj.data.polygons)
            if len(obj.vertex_groups)>=8: weighted+=1
            for mat in obj.data.materials:
                if mat: materials.add(mat.name.lower())
            if any(w in obj.name.lower() for w in SWORD_WORDS): has_sword=True
        elif obj.type=="ARMATURE":
            armatures+=1
            bones+=len(obj.data.bones)
            bone_names.extend(b.name.lower() for b in obj.data.bones)

    mn,mx=world_bounds()
    height=plausible_height_m(mn,mx)
    pl=path.lower()
    hero_hits=sum(1 for w in HERO_WORDS if w in pl)
    bad_hits=sum(1 for w in BAD_WORDS if w in pl)
    humanoid_hits=sum(1 for w in BONE_HINTS if any(w in b for b in bone_names))
    mat_hits=sum(1 for w in ("obsidian","gold","fire","ember","metal","cloth","armor")
                 if any(w in m for m in materials))

    s=0.0
    s+=min(tris,160000)/160000*18.0
    s+=min(bones,160)/160*24.0
    s+=min(humanoid_hits,10)/10*24.0
    s+=min(hero_hits,5)*4.0
    s+=min(mat_hits,5)*2.0
    s+=8.0 if armatures>0 else -20.0
    s+=8.0 if weighted>0 else -8.0
    s+=5.0 if has_sword else 0.0
    s+=8.0 if 1.55<=height<=2.15 else (-4.0 if height>0 else -8.0)
    s-=bad_hits*8.0

    return {
        "path":path,"score":round(s,2),"tris":tris,"verts":verts,"bones":bones,
        "armatures":armatures,"weighted_meshes":weighted,
        "humanoid_bone_hits":humanoid_hits,"materials":sorted(materials),
        "has_sword":has_sword,"height_m":round(height,4),
        "hero_path_hits":hero_hits,"bad_path_hits":bad_hits,
        "objects":len(bpy.data.objects)
    }

def choose_fallback_texture():
    ranked=[]
    for path in images:
        p=path.lower(); s=0
        s+=8 if "ashen" in p else 0
        s+=6 if "vessel" in p else 0
        s+=5 if "hero" in p else 0
        s+=3 if "naris" in p else 0
        s+=4 if any(x in p for x in ("basecolor","albedo","diffuse")) else 0
        s-=6 if any(x in p for x in ("normal","_rm","rough","metal")) else 0
        if s>0: ranked.append((s,path))
    ranked.sort(reverse=True)
    return ranked[0][1] if ranked else None

def material_set():
    defs={
        "M_NARIS_Obsidian":((.018,.022,.028,1),.72,.76),
        "M_NARIS_AgedGold":((.31,.16,.035,1),.62,.86),
        "M_NARIS_EmberFire":((.55,.035,.006,1),.20,.42),
    }
    out={}
    for name,(color,rough,metal) in defs.items():
        mat=bpy.data.materials.get(name) or bpy.data.materials.new(name)
        mat.diffuse_color=color
        mat.roughness=rough
        mat.metallic=metal
        out[name]=mat
    return out

def prepare_material_identity():
    """Preserve real source material assignments; never fabricate unused slots."""
    style_library=material_set()
    result={"mesh_slots":{},"renamed_primary":{},"style_library":sorted(style_library.keys())}
    for obj in bpy.data.objects:
        if obj.type!="MESH":
            continue
        slots=obj.data.materials
        if len(slots)==0:
            # A mesh with no material gets one honest fallback, not three fake slots.
            slots.append(style_library["M_NARIS_Obsidian"])
        else:
            primary=slots[0]
            if primary:
                lower=primary.name.lower()
                if lower.startswith("tripo_") or lower.startswith("material"):
                    old_name=primary.name
                    primary.name="M_NARIS_AshenVessel_PBR"
                    result["renamed_primary"][old_name]=primary.name
        result["mesh_slots"][obj.name]=[m.name if m else None for m in slots]
    return result

def normalize_to_height(target=1.85):
    mn,mx=world_bounds()
    if mn is None: return {"ok":False,"reason":"no_mesh"}
    current=float(mx.z-mn.z)
    if current<=1e-8: return {"ok":False,"reason":"zero_height"}
    factor=target/current
    roots=[o for o in bpy.context.scene.objects if o.parent is None]
    for o in roots:
        o.scale=tuple(v*factor for v in o.scale)
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT")
    for o in roots: o.select_set(True)
    if roots:
        bpy.context.view_layer.objects.active=roots[0]
        try:
            bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        except Exception:
            pass
    bpy.context.view_layer.update()
    mn2,mx2=world_bounds()
    return {"ok":True,"factor":factor,
            "height_after_blender_units":float(mx2.z-mn2.z) if mn2 else 0.0}

def export_sword(path):
    swords=[o for o in bpy.data.objects if o.type=="MESH"
            and any(w in o.name.lower() for w in SWORD_WORDS)]
    if not swords: return None
    bpy.ops.object.select_all(action="DESELECT")
    for o in swords:
        o.name="SM_Sword_AshenVessel"
        o.select_set(True)
    bpy.context.view_layer.objects.active=swords[0]
    bpy.ops.export_scene.fbx(filepath=path,use_selection=True,
        add_leaf_bones=False,apply_unit_scale=True,bake_anim=False)
    return path

def emergency_relief(texture_path,out_path):
    reset_scene()
    img=bpy.data.images.load(texture_path)
    w,h=img.size
    xs=max(16,min(int(w//16),96))
    ys=max(16,min(int(h//16),128))
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=xs,y_subdivisions=ys,size=2.0)
    grid=bpy.context.object
    grid.name="SM_AshenVessel_2_5D_RELIEF_EMERGENCY"
    px=list(img.pixels)
    for v in grid.data.vertices:
        u=max(0,min(1,(v.co.x+1)/2))
        vv=max(0,min(1,(v.co.y+1)/2))
        ix=min(int(u*(w-1)),w-1)
        iy=min(int(vv*(h-1)),h-1)
        i=(iy*w+ix)*4
        lum=.2126*px[i]+.7152*px[i+1]+.0722*px[i+2]
        v.co.z=(lum-.5)*.12*px[i+3]
    solid=grid.modifiers.new("EmergencyThickness","SOLIDIFY")
    solid.thickness=.035
    bpy.context.view_layer.objects.active=grid
    bpy.ops.object.modifier_apply(modifier=solid.name)
    grid.data.materials.append(material_set()["M_NARIS_Obsidian"])
    bpy.ops.export_scene.fbx(filepath=out_path,use_selection=False,
        apply_unit_scale=True,bake_anim=False)

results=[]
for i,path in enumerate(models,1):
    try:
        item=score(path)
    except Exception:
        item={"path":path,"score":-999.0,"error":traceback.format_exc()}
    results.append(item)
    print(f"[{i}/{len(models)}] {item.get('score')} :: {os.path.basename(path)}")

results.sort(key=lambda x:x.get("score",-999),reverse=True)
winner=results[0] if results else None
THRESHOLD=55.0

prod_fbx=os.path.join(OUT,"SK_AshenVessel_Production.fbx")
prod_blend=os.path.join(OUT,"SK_AshenVessel_Production.blend")
sword_fbx=os.path.join(OUT,"SM_Sword_AshenVessel.fbx")
fallback_texture=choose_fallback_texture()
status="FAIL_NO_USABLE_SOURCE"
production_grade=False
normalization={}
material_identity={}
sword_output=None

if (winner and winner.get("score",-999)>=THRESHOLD
        and winner.get("armatures",0)>0
        and winner.get("humanoid_bone_hits",0)>=5):
    reset_scene()
    import_any(winner["path"])
    normalization=normalize_to_height(1.85)
    material_identity=prepare_material_identity()
    sword_output=export_sword(sword_fbx)
    bpy.ops.wm.save_as_mainfile(filepath=prod_blend)
    bpy.ops.export_scene.fbx(filepath=prod_fbx,use_selection=False,
        add_leaf_bones=False,apply_unit_scale=True,bake_anim=True)
    status="OK_PRODUCTION_FROM_"+os.path.basename(winner["path"])
    production_grade=True
elif fallback_texture:
    emergency_relief(fallback_texture,prod_fbx)
    bpy.ops.wm.save_as_mainfile(filepath=prod_blend)
    status="EMERGENCY_2_5D_RELIEF_FROM_"+os.path.basename(fallback_texture)

log={
    "status":status,
    "production_grade":production_grade,
    "decision_rule":"Production requires a rigged humanoid; billboard relief is emergency visual fallback only.",
    "threshold":THRESHOLD,
    "winner":winner,
    "top10":results[:10],
    "candidate_count":len(results),
    "fallback_texture":fallback_texture,
    "normalization":normalization,
    "material_identity":material_identity,
    "material_policy":"preserve assigned source PBR; do not fabricate unassigned style slots",
    "output_fbx":prod_fbx if os.path.exists(prod_fbx) else None,
    "output_blend":prod_blend if os.path.exists(prod_blend) else None,
    "sword_output":sword_output
}
with open(os.path.join(OUT,"P0-01_reimport_log.json"),"w",encoding="utf-8") as f:
    json.dump(log,f,indent=2,ensure_ascii=False)
print("=== P0-01 DONE ===")
print(json.dumps(log,indent=2,ensure_ascii=False))
if status.startswith("FAIL"):
    raise SystemExit(3)
