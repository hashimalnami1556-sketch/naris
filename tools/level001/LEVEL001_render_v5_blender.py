"""Blender only: true equal-camera V4 vs V5 comparison, not Unreal game evidence."""
import bpy,json,math
from pathlib import Path
from mathutils import Vector

gis=Path(r"C:\Users\Admin\NARIS\Saved\GIS\Jeddah")
v3=gis/"LEVEL001_AlBalad_Footprints_Review03/JED_AlBalad_OSM_TrueFootprints_V3.glb"
v4=gis/"LEVEL001_AlBalad_Footprints_Review04/JED_AlBalad_ArchitecturalDetails_V4.glb"
v5=gis/"LEVEL001_AlBalad_Footprints_Review05/JED_AlBalad_ProjectedRawashin_V5.glb"
out=gis/"LEVEL001_AlBalad_Footprints_Review05/Preview"
if not all(x.is_file() for x in (v3,v4,v5)):raise RuntimeError("MISSING_DEPENDENT_GLB")
if out.exists() and list(out.glob("*.png")):raise RuntimeError("EXISTING_V5_IMAGES_ABORT")
out.mkdir(parents=True,exist_ok=True)

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)
groups=[]
for path in (v3,v4,v5):
    existing=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    meshes=[o for o in bpy.data.objects if o not in existing and o.type=="MESH"]
    if len(meshes)!=3:raise RuntimeError("GLB_IMPORT_ACTOR_COUNT_MISMATCH_"+str(path))
    groups.append(meshes)
base,facades,rawashin=groups
for m in bpy.data.materials:
    if m.use_nodes:
        bsdf=next((n for n in m.node_tree.nodes if n.type=="BSDF_PRINCIPLED"),None)
        if bsdf:m.diffuse_color=tuple(bsdf.inputs["Base Color"].default_value)
# Preview-only pavement, never exported.
bpy.ops.mesh.primitive_plane_add(size=1300,location=(0,0,-.12))
plane=bpy.context.object
plane.name="PREVIEW_ONLY_NoTerrainIncludedInGLB"
pm=bpy.data.materials.new("PREVIEW_ONLY_Stone_Paving")
pm.diffuse_color=(.43,.395,.345,1)
plane.data.materials.append(pm)
camdata=bpy.data.cameras.new("V5_EVIDENCE_LOCKED_CAMERA")
cam=bpy.data.objects.new("V5_EVIDENCE_LOCKED_CAMERA",camdata)
bpy.context.collection.objects.link(cam)
scene=bpy.context.scene;scene.camera=cam
scene.render.engine="BLENDER_WORKBENCH"
scene.render.resolution_x=1440
scene.render.resolution_y=810
scene.render.resolution_percentage=100
scene.render.image_settings.file_format="PNG"
scene.render.film_transparent=False
scene.display.shading.light="STUDIO"
scene.display.shading.color_type="MATERIAL"
scene.display.shading.show_cavity=True
scene.display.shading.show_shadows=True
scene.display.shading.cavity_type="BOTH"
scene.display.shading.curvature_ridge_factor=1.4
scene.display.shading.curvature_valley_factor=1.0
camera_targets={}
def point_camera(position,target,ortho=False,scale=260):
    cam.location=Vector(position)
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat("-Z","Y").to_euler()
    camdata.type="ORTHO" if ortho else "PERSP"
    camdata.lens=30
    if ortho:camdata.ortho_scale=scale
def shot(name,rawashin_visible):
    for item in rawashin:item.hide_render=not rawashin_visible
    dest=out/name
    if dest.exists():raise RuntimeError("NOT_OVERWRITING_"+name)
    scene.render.filepath=str(dest)
    bpy.ops.render.render(write_still=True)
    if not dest.is_file() or dest.stat().st_size<150000:
        raise RuntimeError("RENDER_INVALID_"+name)
    return str(dest)
# Camera uses exactly same OSM building and source coordinates as V4 previous QA.
d=json.loads((gis/"jeddah_gis_v2.json").read_text(encoding="utf-8"))
art=json.loads((v4.parent/"JED_AlBalad_ArchitecturalDetails_V4_manifest.json").read_text(encoding="utf-8"))
orig=d["origin_wgs84"]
ox=(39.1875-orig["lon"])*111320*math.cos(math.radians(orig["lat"]))*100
oy=(21.4839-orig["lat"])*110540*100
ids=set(art["decorated_osm_ids"])
poss=[]
for b in d["buildings"]:
    if b.get("osm_id") not in ids:continue
    ring=[tuple(map(float,p)) for p in b.get("footprint_cm",[])]
    if len(ring)>1 and ring[0]==ring[-1]:ring.pop()
    if len(ring)<4:continue
    x=sum(p[0] for p in ring)/len(ring)
    y=sum(p[1] for p in ring)/len(ring)
    dist=math.hypot((x-ox)/100,(y-oy)/100)
    if 15<dist<150:poss.append((dist,b,ring))
if not poss:raise RuntimeError("NO_SAMPLE_BUILDING")
_,b,ring=min(poss,key=lambda e:e[0])
if sum(ring[i][0]*ring[(i+1)%len(ring)][1]-ring[(i+1)%len(ring)][0]*ring[i][1] for i in range(len(ring)))<0:
    ring.reverse()
edges=[]
for i,A in enumerate(ring):
    B=ring[(i+1)%len(ring)]
    length=math.hypot((B[0]-A[0])/100,(B[1]-A[1])/100)
    if length>=3.8:edges.append((length,A,B))
if not edges:raise RuntimeError("BUILDING_HAS_NO_ACCESSIBLE_FRONT")
length,A,B=max(edges,key=lambda e:(min(e[0],24),-abs(e[0]-12)))
dx=(B[0]-A[0])/100/length
dy=(B[1]-A[1])/100/length
px=(((A[0]+B[0])/2)-ox)/100
py=(((A[1]+B[1])/2)-oy)/100
camera_pos=(px+dy*14-dx*2,py-dx*14-dy*2,8)
camera_target=(px,py,5)
point_camera(camera_pos,camera_target,False)
before=shot("01_v4_street_before.png",False)
after=shot("02_v5_street_after.png",True)
point_camera((130,-155,175),(0,0,0),True,330)
overview_before=shot("03_v4_city_before.png",False)
overview_after=shot("04_v5_city_after.png",True)
report={"schema":"naris.level001.v5.preview",
    "render_engine":"BLENDER_WORKBENCH",
    "unreal_game_screenshot":False,
    "camera_locked_within_each_before_after_pair":True,
    "street_osm_id":b.get("osm_id"),
    "street_camera_m":list(camera_pos),
    "baseline_meshes_v3":len(base),
    "v4_facade_meshes":len(facades),
    "v5_projected_meshes":len(rawashin),
    "images":{"street_v4":before,"street_v5":after,
              "city_v4":overview_before,"city_v5":overview_after},
    "production_approved":False}
(gis/"LEVEL001_AlBalad_Footprints_Review05/LEVEL001_V5_Blender_Render_Report.json").write_text(
    json.dumps(report,indent=2),encoding="utf-8")
print("LEVEL001_V5_RENDER_COMPLETE="+json.dumps(report))
