"""LEVEL-001 V5 — projected, latticed Hijazi-inspired oriels on real OSM walls.
Review-only GLB. Not a verified historical facade; no source/UE map changes.
Uses Python standard library and existing verified GIS V3/V4 geometry helpers.
"""
from pathlib import Path
import json,math,hashlib,struct
import LEVEL001_footprint_glb as geo
from LEVEL001_facade_v4 import wall_axes

GLB_NAME="JED_AlBalad_ProjectedRawashin_V5.glb"
MAX_DEPTH=.89

def cuboid(mesh,orig,t,n,left,right,bottom,top,near,far):
    if not(left<right and bottom<top and -.001<=near<far<=MAX_DEPTH+1e-7):
        raise ValueError("invalid oriel geometry bounds")
    def vert(x,y,z):
        return (orig[0]+t[0]*x+n[0]*z,y,orig[2]+t[2]*x+n[2]*z)
    p=[vert(left,bottom,near),vert(right,bottom,near),
       vert(right,top,near),vert(left,top,near),
       vert(left,bottom,far),vert(right,bottom,far),
       vert(right,top,far),vert(left,top,far)]
    for a,b,c,d in ((0,3,2,1),(4,5,6,7),(0,4,7,3),
                    (1,2,6,5),(3,7,6,2),(0,1,5,4)):
        mesh.tri(p[a],p[b],p[c])
        mesh.tri(p[a],p[c],p[d])

def _export_glb(path,parts):
    temp=path.with_name("_V5_temporary_geometry.glb")
    if temp.exists() or path.exists():raise FileExistsError("V5 export output already exists")
    geo.write_glb(temp,parts)
    data=temp.read_bytes()
    count=struct.unpack_from("<I",data,12)[0]
    doc=json.loads(data[20:20+count])
    offset=20+count
    bcount,btype=struct.unpack_from("<I4s",data,offset)
    if btype!=b"BIN\x00" or offset+8+bcount!=len(data):
        raise ValueError("GLB binary chunk invalid")
    binary=data[offset+8:]
    mats=[
      ("V5_Rawashin_Warm_Cedar",[.27,.105,.048,1],.78),
      ("V5_Stone_Mouldings",[.70,.59,.44,1],.9),
      ("V5_Shadowed_Screen",[.055,.045,.036,1],.94)]
    for i,(name,color,rough) in enumerate(mats):
        doc["materials"][i]={"name":name,"doubleSided":True,
            "pbrMetallicRoughness":{"baseColorFactor":color,"roughnessFactor":rough,"metallicFactor":0.0}}
    doc["asset"]["generator"]="NARIS V5 architectural stylization of real OSM footprints"
    doc["asset"]["extras"]={"historical_accuracy_verified":False,"unreal_integrated":False}
    encoded=json.dumps(doc,sort_keys=True,separators=(",",":")).encode("utf-8")
    while len(encoded)%4:encoded+=b" "
    with path.open("xb") as out:
        out.write(struct.pack("<4sII",b"glTF",2,12+8+len(encoded)+8+len(binary)))
        out.write(struct.pack("<I4s",len(encoded),b"JSON"))
        out.write(encoded)
        out.write(struct.pack("<I4s",len(binary),b"BIN\x00"))
        out.write(binary)
    if struct.unpack_from("<I",path.read_bytes(),8)[0]!=path.stat().st_size:
        raise RuntimeError("GLB total length mismatch")
    temp.unlink()

def export_projected_rawashin(source,outdir,lat=21.4839,lon=39.1875,radius_m=500):
    source=Path(source);outdir=Path(outdir)
    obj=json.loads(source.read_text(encoding="utf-8"))
    if obj.get("license")!="ODbL 1.0":
        raise ValueError("The GIS source license was not verified")
    origin=obj["origin_wgs84"]
    ox=(lon-origin["lon"])*111320*math.cos(math.radians(origin["lat"]))*100
    oy=(lat-origin["lat"])*110540*100
    wood,stone,shadow=geo.Mesh(),geo.Mesh(),geo.Mesh()
    eligible=0;ids=[];roshans=0;bars=0;doors=0
    for rec in obj["buildings"]:
        ring=[tuple(map(float,p)) for p in rec.get("footprint_cm",[])]
        if len(ring)>1 and ring[0]==ring[-1]:ring.pop()
        if len(ring)<3 or abs(geo.area2(ring))<1e5:continue
        center=((max(p[0] for p in ring)+min(p[0] for p in ring))/2,
                (max(p[1] for p in ring)+min(p[1] for p in ring))/2)
        if math.hypot(center[0]-ox,center[1]-oy)>radius_m*100:continue
        if geo.area2(ring)<0:ring.reverse()
        try:geo.triangulate_polygon(ring)
        except ValueError:continue
        eligible+=1
        height=max(2.4,min(350.0,float(rec.get("height_m") or 9.6)))
        edges=[]
        for i,A in enumerate(ring):
            B=ring[(i+1)%len(ring)]
            size=math.hypot((B[0]-A[0])/100,(B[1]-A[1])/100)
            if size>=3.8:edges.append((size,A,B))
        if not edges or height<5:continue
        length,A,B=max(edges,key=lambda v:(min(v[0],24),-abs(v[0]-12)))
        t,n=wall_axes(A,B)
        origin3=((A[0]-ox)/100,0,-(A[1]-oy)/100)
        count=min(3,max(1,int((length-1.6)/2.7)))
        max_floors=min(4,max(1,int(height/3)))
        built=0
        for floor in range(max_floors):
            low=1.4+floor*3.02
            high=low+1.56
            if high>=height-.65:continue
            for j in range(count):
                center_x=length*(j+1)/(count+1)
                half=min(.48,length/(count+1)*.28)
                L=center_x-half;R=center_x+half
                if L<.6 or R>length-.6:continue
                # Enclosed three-dimensional oriel, 0.89m projection, shadow inside:
                cuboid(shadow,origin3,t,n,L+.08,R-.08,low+.08,high-.10,.72,.765)
                cuboid(shadow,origin3,t,n,L,L+.08,low+.08,high-.07,.27,.72)
                cuboid(shadow,origin3,t,n,R-.08,R,low+.08,high-.07,.27,.72)
                # Projected wooden side frames, base, roof, front corners:
                for ll,rr in ((L,L+.075),(R-.075,R)):
                    cuboid(wood,origin3,t,n,ll,rr,low,high,.23,.82)
                cuboid(wood,origin3,t,n,L,R,low-.075,low+.06,.18,.88)
                cuboid(wood,origin3,t,n,L-.065,R+.065,high-.09,high+.07,.16,.89)
                cuboid(stone,origin3,t,n,L-.08,R+.08,high+.07,high+.115,.10,.89)
                # Front lattice, closer to the street than dark backing:
                for k in range(1,6):
                    x=L+(R-L)*k/6
                    cuboid(wood,origin3,t,n,x-.016,x+.016,low+.085,high-.08,.77,.832)
                    bars+=1
                for k in range(1,5):
                    y=low+(high-low)*k/5
                    cuboid(wood,origin3,t,n,L+.06,R-.06,y-.016,y+.016,.766,.839)
                    bars+=1
                # Two side lattices, not flat decals:
                for dep in (.39,.52,.65):
                    for ll,rr in ((L+.004,L+.043),(R-.043,R-.004)):
                        cuboid(wood,origin3,t,n,ll,rr,low+.11,high-.12,dep,dep+.027)
                        bars+=1
                # Balcony sill + repeated finials distinct from V4:
                cuboid(stone,origin3,t,n,L-.11,R+.11,low-.145,low-.055,.15,.89)
                roshans+=1;built+=1
        if built:
            ids.append(rec.get("osm_id"))
            if length>4.1:
                # Portal with segmented header; decorative only, not physical doorway:
                cx=length/2
                for x in (cx-.82,cx+.74):
                    cuboid(stone,origin3,t,n,x,x+.08,.10,2.4,.09,.24)
                cuboid(stone,origin3,t,n,cx-.88,cx+.88,2.32,2.46,.07,.30)
                doors+=1
    if not ids or not roshans:raise ValueError("OSM sector has no eligible facade oriel locations")
    outdir.mkdir(parents=True,exist_ok=True)
    glb=outdir/GLB_NAME
    if glb.exists():raise FileExistsError(str(glb))
    _export_glb(glb,[("Projected_Rawashin_Cedar",wood),
                     ("Projected_Cornices_Limestone",stone),
                     ("Deep_Lattice_ShadowPanels",shadow)])
    report={"schema":"naris.level001.review05.projected_rawashin",
       "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
       "license":obj["license"],
       "eligible_building_count":eligible,"decorated_building_count":len(ids),
       "decorated_osm_ids":ids,"projected_rawashin_count":roshans,
       "lattice_rails_count":bars,"door_portal_count":doors,
       "max_outward_projection_m":MAX_DEPTH,
       "triangle_count":wood.triangles+stone.triangles+shadow.triangles,
       "glb_sha256":hashlib.sha256(glb.read_bytes()).hexdigest(),
       "glb_bytes":glb.stat().st_size,
       "model_anchor_world_cm":{"x":round(ox,3),"y":round(oy,3),"z":0},
       "source_footprints_unchanged":True,"photomatch_verified":False,
       "historical_facades_verified":False,"collision_tested":False,
       "navmesh_tested":False,"unreal_import_tested":False,
       "client_server_tested":False,"performance_measured":False,
       "production_approved":False,
       "note":"Heritage-inspired 3D detailing. Requires verified construction references, actual UE QA."}
    man=outdir/"JED_AlBalad_ProjectedRawashin_V5_manifest.json"
    if man.exists():raise FileExistsError(str(man))
    man.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    return report

if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("out")
    args=ap.parse_args()
    print(json.dumps(export_projected_rawashin(args.source,args.out),indent=2))
