"""LEVEL-001 — genuine OSM footprint extrusion, no external packages.
Review-only geometry GLB. Does not modify source .umap or tracked files.
GLB uses metres/Y-up; manifest gives placement in UE GIS centimetres.
"""
from pathlib import Path
import hashlib
import json
import math
import struct

def area2(poly):
    return sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(poly,poly[1:]+poly[:1]))

def triangulate_polygon(poly):
    """Ear clip a simple, non-self-intersecting 2D polygon."""
    if len(poly)<3: return []
    ids=list(range(len(poly)))
    if area2(poly)<0: ids.reverse()
    ans=[]
    def cross(a,b,c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def inside(p,a,b,c):
        return cross(a,b,p)>=-1e-9 and cross(b,c,p)>=-1e-9 and cross(c,a,p)>=-1e-9
    watchdog=0
    while len(ids)>3:
        found=False
        for k in range(len(ids)):
            ia,ib,ic=ids[k-1],ids[k],ids[(k+1)%len(ids)]
            a,b,c=poly[ia],poly[ib],poly[ic]
            if cross(a,b,c)<=1e-8: continue
            if any(inside(poly[j],a,b,c) for j in ids if j not in (ia,ib,ic)): continue
            ans.append((ia,ib,ic))
            del ids[k]
            found=True
            break
        watchdog+=1
        if not found or watchdog>len(poly)*2:
            raise ValueError("invalid polygon for ear clipping")
    ans.append(tuple(ids))
    return ans

class Mesh:
    def __init__(self):
        self.positions=[]
        self.normals=[]
        self.indices=[]
    def tri(self,a,b,c):
        u=[b[i]-a[i] for i in range(3)]
        v=[c[i]-a[i] for i in range(3)]
        n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
        mag=math.sqrt(sum(x*x for x in n))
        if mag<1e-8:return
        n=tuple(x/mag for x in n)
        s=len(self.positions)
        self.positions.extend((a,b,c))
        self.normals.extend((n,n,n))
        self.indices.extend((s,s+1,s+2))
    @property
    def triangles(self):
        return len(self.indices)//3

def write_glb(path,parts):
    """Write GLB 2.0 with three PBR material slots and separate meshes."""
    materials=[
        ("HistoricLimestone_Procedural",[0.59,0.51,0.41,1]),
        ("Roofs_Procedural",[0.47,0.38,0.31,1]),
        ("RoadSurface_Procedural",[0.20,0.22,0.25,1]),
    ]
    doc={"asset":{"version":"2.0","generator":"NARIS LEVEL001 real OSM footprint exporter v3"},
         "scene":0,"scenes":[{"nodes":[]}],
         "nodes":[],"meshes":[],"accessors":[],"bufferViews":[],
         "buffers":[],"materials":[]}
    for name,color in materials:
        doc["materials"].append({"name":name,"pbrMetallicRoughness":{
            "baseColorFactor":color,"metallicFactor":0.0,"roughnessFactor":0.92},
            "doubleSided":True})
    binary=bytearray()
    def accessor(values,fmt,ctype,dimensions,target,lohi=False):
        flat=[x for row in values for x in row] if dimensions!=1 else list(values)
        while len(binary)%4: binary.append(0)
        off=len(binary)
        binary.extend(struct.pack("<"+str(len(flat))+fmt,*flat))
        vi=len(doc["bufferViews"])
        doc["bufferViews"].append({"buffer":0,"byteOffset":off,
                                   "byteLength":len(flat)*struct.calcsize(fmt),"target":target})
        acc={"bufferView":vi,"componentType":ctype,"count":len(values),
             "type":"SCALAR" if dimensions==1 else "VEC3"}
        if lohi and values:
            acc["min"]=[min(v[i] for v in values) for i in range(3)]
            acc["max"]=[max(v[i] for v in values) for i in range(3)]
        ix=len(doc["accessors"]);doc["accessors"].append(acc);return ix
    for mi,(name,mesh) in enumerate(parts):
        if not mesh.indices:continue
        p=accessor(mesh.positions,"f",5126,3,34962,True)
        n=accessor(mesh.normals,"f",5126,3,34962)
        ix=accessor(mesh.indices,"I",5125,1,34963)
        meshix=len(doc["meshes"])
        doc["meshes"].append({"name":name,"primitives":[{
            "attributes":{"POSITION":p,"NORMAL":n},
            "indices":ix,"material":mi,"mode":4}]})
        nodeix=len(doc["nodes"])
        doc["nodes"].append({"name":name,"mesh":meshix})
        doc["scenes"][0]["nodes"].append(nodeix)
    while len(binary)%4:binary.append(0)
    doc["buffers"]=[{"byteLength":len(binary)}]
    js=json.dumps(doc,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    while len(js)%4:js+=b" "
    total=12+8+len(js)+8+len(binary)
    with open(path,"xb") as out:
        out.write(struct.pack("<4sII",b"glTF",2,total))
        out.write(struct.pack("<I4s",len(js),b"JSON"));out.write(js)
        out.write(struct.pack("<I4s",len(binary),b"BIN\x00"));out.write(binary)
    return path.stat().st_size

def export_sector(cache,outdir,lat=21.4839,lon=39.1875,radius_m=500):
    cache=Path(cache);outdir=Path(outdir)
    d=json.loads(cache.read_text(encoding="utf-8"))
    origin=d["origin_wgs84"]
    x=(lon-origin["lon"])*111320*math.cos(math.radians(origin["lat"]))*100
    y=(lat-origin["lat"])*110540*100
    radius_cm=radius_m*100
    walls,roof,roads=Mesh(),Mesh(),Mesh()
    ids=[];road_ids=set();omitted=0
    def to3(p,h):
        return ((p[0]-x)/100.0,float(h),-(p[1]-y)/100.0)
    for b in d["buildings"]:
        ring=[tuple(float(v) for v in point) for point in b.get("footprint_cm",[])]
        if len(ring)>1 and ring[0]==ring[-1]:ring.pop()
        if len(ring)<3:continue
        cx=(min(pt[0] for pt in ring)+max(pt[0] for pt in ring))/2
        cy=(min(pt[1] for pt in ring)+max(pt[1] for pt in ring))/2
        if math.hypot(cx-x,cy-y)>radius_cm:continue
        if abs(area2(ring))<1e5: omitted+=1;continue
        if area2(ring)<0:ring.reverse()
        try:
            triangles=triangulate_polygon(ring)
        except ValueError:
            omitted+=1;continue
        h=float(b.get("height_m") or 9.6)
        h=max(2.4,min(350.0,h))
        for i in range(len(ring)):
            v0,v1=ring[i],ring[(i+1)%len(ring)]
            a=to3(v0,0);bb=to3(v1,0);c=to3(v1,h);e=to3(v0,h)
            walls.tri(a,bb,c)
            walls.tri(a,c,e)
        for i,j,k in triangles:roof.tri(to3(ring[i],h),to3(ring[j],h),to3(ring[k],h))
        ids.append(b.get("osm_id"))
    widths={"motorway":18,"trunk":16,"primary":14,"secondary":11,
            "tertiary":9,"residential":6,"unclassified":6,
            "pedestrian":4,"living_street":4,"service":4}
    for rd in d["roads"]:
        pts=rd.get("points_cm",[])
        w=widths.get(rd.get("class"),5)
        for aa,bb in zip(pts,pts[1:]):
            ax,ay=aa;bx,by=bb
            length=math.hypot(bx-ax,by-ay)
            if length<50:continue
            if math.hypot((ax+bx)*0.5-x,(ay+by)*0.5-y)>radius_cm:continue
            nx=-(by-ay)/length*(w*50)
            ny=(bx-ax)/length*(w*50)
            quad=[(ax+nx,ay+ny),(ax-nx,ay-ny),
                  (bx-nx,by-ny),(bx+nx,by+ny)]
            q=[to3(p,0.06) for p in quad]
            roads.tri(q[0],q[1],q[2]);roads.tri(q[0],q[2],q[3])
            road_ids.add(rd.get("osm_id"))
    if not ids:raise ValueError("no buildings selected; refusing empty model")
    outdir.mkdir(parents=True,exist_ok=True)
    glb=outdir/"JED_AlBalad_OSM_TrueFootprints_V3.glb"
    if glb.exists():raise FileExistsError(str(glb))
    size=write_glb(glb,[("OSM_Building_Walls",walls),
                        ("OSM_Building_Roofs",roof),
                        ("OSM_Roads",roads)])
    manifest={
        "schema":"naris.jeddah.real_footprints.v3.review",
        "source":d.get("source","OpenStreetMap contributors"),
        "source_license":d.get("license","ODbL 1.0"),
        "sector_center_wgs84":{"lat":lat,"lon":lon},
        "model_anchor_world_cm":{"x":round(x,3),"y":round(y,3),"z":0},
        "coordinate_system":"glTF2 metres, Y-up, -north local Z",
        "radius_m":radius_m,
        "buildings_selected":len(ids),
        "roads_selected":len(road_ids),
        "osm_building_ids":ids,
        "osm_road_ids":sorted(list(road_ids),key=str),
        "omitted_invalid_buildings":omitted,
        "triangles":{"walls":walls.triangles,"roofs":roof.triangles,
                     "roads":roads.triangles,"total":walls.triangles+roof.triangles+roads.triangles},
        "glb_size_bytes":size,
        "glb_sha256":hashlib.sha256(glb.read_bytes()).hexdigest(),
        "facades_photo_scanned":False,
        "unreal_import_tested":False,
        "performance_measured":False,
        "production_approved":False,
        "note":"True OSM footprint geometry, proxy heights; not photoreal, needs art/UE QA. Never overwrite GIS V2."
    }
    m=outdir/"JED_AlBalad_OSM_TrueFootprints_V3_manifest.json"
    if m.exists():raise FileExistsError(str(m))
    m.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding="utf-8")
    return manifest

if __name__=="__main__":
    cache=Path(r"C:\Users\Admin\NARIS\Saved\GIS\Jeddah\jeddah_gis_v2.json")
    out=cache.parent/"LEVEL001_AlBalad_Footprints_Review03"
    result=export_sector(cache,out)
    print(json.dumps({k:v for k,v in result.items() if k not in ("osm_building_ids","osm_road_ids")},
                     ensure_ascii=False,indent=2))
