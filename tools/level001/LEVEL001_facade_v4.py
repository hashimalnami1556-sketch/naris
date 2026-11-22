"""LEVEL-001: review-only aligned Hijazi-inspired GLB for real OSM footprints.
Never modifies existing source GIS V2/Review03, imports, or Unreal configuration.
Procedural artistic facades are NOT historical surveys or photomatches.
"""
import json,math,struct,hashlib
from pathlib import Path
import LEVEL001_footprint_glb as geo
NAME='JED_AlBalad_ArchitecturalDetails_V4.glb'
MAX_PROJECTION=.30

def wall_axes(a,b):
    dx=(b[0]-a[0])/100;dy=(b[1]-a[1])/100
    leng=math.hypot(dx,dy)
    if leng<1e-8:raise ValueError('degenerate wall')
    return (dx/leng,0,-dy/leng),(dy/leng,0,dx/leng)

def box(mesh,origin,t,n,l,r,b,top,back,front):
    if not(l<r and b<top and 0<=back<front<=MAX_PROJECTION):raise ValueError('unsafe facade box')
    def v(s,y,d):return (origin[0]+t[0]*s+n[0]*d,y,origin[2]+t[2]*s+n[2]*d)
    vs=[v(l,b,back),v(r,b,back),v(r,top,back),v(l,top,back),
        v(l,b,front),v(r,b,front),v(r,top,front),v(l,top,front)]
    fs=((0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),
        (3,7,6,2),(0,1,5,4))
    # geo.Mesh.tri computes geometric normals from winding.
    for ia,ib,ic,id in fs:
        mesh.tri(vs[ia],vs[ib],vs[ic])
        mesh.tri(vs[ia],vs[ic],vs[id])

def write_materials_glb(path,meshes):
    tmp=path.with_name('LEVEL001_V4_Intermediate_DeleteAfterValidation.glb')
    if path.exists() or tmp.exists():raise FileExistsError(str(path))
    geo.write_glb(tmp,meshes)
    raw=tmp.read_bytes()
    if raw[:4]!=b'glTF':raise ValueError('invalid intermediate glb')
    jslen=struct.unpack_from('<I',raw,12)[0]
    doc=json.loads(raw[20:20+jslen])
    pos=20+jslen
    binlen,typ=struct.unpack_from('<I4s',raw,pos)
    if typ!=b'BIN\x00' or pos+8+binlen!=len(raw):raise ValueError('corrupt binary chunk')
    binchunk=raw[pos+8:]
    defs=[
        ('Hijazi_Weathered_Teak',[.28,.155,.085,1],.75,[0,0,0]),
        ('Hijazi_Pale_Limestone_Trim',[.74,.625,.49,1],.88,[0,0,0]),
        ('Hijazi_Warm_Window_Glass',[.17,.13,.10,1],.42,[.22,.10,.03])]
    for i,(name,col,rough,emit) in enumerate(defs):
        doc['materials'][i]={'name':name,'doubleSided':True,
            'pbrMetallicRoughness':{'baseColorFactor':col,'roughnessFactor':rough,'metallicFactor':0},
            'emissiveFactor':emit}
    doc['asset']['generator']='NARIS Review04 procedural heritage-inspired overlay — not photomatched'
    doc['asset']['extras']={'historical_accuracy_verified':False,'collision_validated':False}
    js=json.dumps(doc,sort_keys=True,separators=(',',':')).encode('utf-8')
    while len(js)%4:js+=b' '
    with path.open('xb') as f:
        f.write(struct.pack('<4sII',b'glTF',2,12+8+len(js)+8+len(binchunk)))
        f.write(struct.pack('<I4s',len(js),b'JSON'));f.write(js)
        f.write(struct.pack('<I4s',len(binchunk),b'BIN\x00'));f.write(binchunk)
    if struct.unpack_from('<I',path.read_bytes(),8)[0]!=path.stat().st_size:raise ValueError('glb length mismatch')
    tmp.unlink()

def build_facades(source,outdir,lat=21.4839,lon=39.1875,radius_m=500):
    source=Path(source);outdir=Path(outdir)
    d=json.loads(source.read_text(encoding='utf-8'));origin=d['origin_wgs84']
    ox=(lon-origin['lon'])*111320*math.cos(math.radians(origin['lat']))*100
    oy=(lat-origin['lat'])*110540*100
    w,s,g=geo.Mesh(),geo.Mesh(),geo.Mesh()
    count=0;decorated=[];windows=0;rails=0;doors=0
    for bd in d['buildings']:
        ring=[tuple(map(float,p)) for p in bd.get('footprint_cm',[])]
        if len(ring)>1 and ring[0]==ring[-1]:ring.pop()
        if len(ring)<3:continue
        cent=((min(p[0] for p in ring)+max(p[0] for p in ring))/2,
              (min(p[1] for p in ring)+max(p[1] for p in ring))/2)
        if math.hypot(cent[0]-ox,cent[1]-oy)>radius_m*100:continue
        if abs(geo.area2(ring))<1e5:continue
        if geo.area2(ring)<0:ring.reverse()
        try:geo.triangulate_polygon(ring)
        except ValueError:continue
        h=max(2.4,min(350,float(bd.get('height_m') or 9.6)))
        count+=1;edges=[]
        for i,a in enumerate(ring):
            b=ring[(i+1)%len(ring)]
            size=math.hypot((b[0]-a[0])/100,(b[1]-a[1])/100)
            if size<3.8:continue
            t,n=wall_axes(a,b)
            st=((a[0]-ox)/100,0,-(a[1]-oy)/100)
            box(s,st,t,n,.1,size-.1,h-.04,h+.55,.02,.18)
            rails+=1;edges.append((size,a,b))
        if not edges:continue
        length,a,b=max(edges,key=lambda e:(min(e[0],24),-abs(e[0]-12)))
        t,n=wall_axes(a,b);st=((a[0]-ox)/100,0,-(a[1]-oy)/100)
        num=min(3,max(1,int((length-1.6)/2.7)))
        floors=min(4,max(1,int(h/3)));made=0
        for floor in range(floors):
            bot=1.4+floor*3.02;top=bot+1.56
            if top>=h-.65:continue
            for j in range(num):
                center=length*(j+1)/(num+1);half=min(.48,length/(num+1)*.28)
                l,r=center-half,center+half
                if l<.6 or r>length-.6:continue
                box(g,st,t,n,l+.06,r-.06,bot+.10,top-.10,.034,.048)
                for ll,rr,bb,tt in ((l,l+.1,bot,top),(r-.1,r,bot,top),
                                     (l,r,bot,bot+.1),(l,r,top-.1,top)):
                    box(w,st,t,n,ll,rr,bb,tt,.05,.245)
                for f in (1/3,2/3):
                    q=l+(r-l)*f
                    box(w,st,t,n,q-.026,q+.026,bot+.12,top-.12,.246,.291)
                mid=(bot+top)/2
                box(w,st,t,n,l+.1,r-.1,mid-.029,mid+.029,.247,.292)
                box(s,st,t,n,l-.09,r+.09,bot-.17,bot-.035,.02,.26)
                windows+=1;made+=1
        if made:
            decorated.append(bd.get('osm_id'))
            if length>4.1 and h>=3.5:
                mid=length/2
                box(w,st,t,n,mid-.75,mid+.75,.08,2.25,.04,.12)
                box(s,st,t,n,mid-.88,mid+.88,2.23,2.35,.05,.25)
                doors+=1
    if not decorated:raise ValueError('no eligible facades in this OSM sector')
    dest=outdir/NAME
    if dest.exists():raise FileExistsError(str(dest))
    outdir.mkdir(parents=True,exist_ok=True)
    write_materials_glb(dest,[('Hijazi_Procedural_Rawashin',w),
                              ('Hijazi_Procedural_StoneTrim',s),
                              ('Hijazi_Procedural_WindowGlass',g)])
    report={'schema':'naris.level001.review04.facades','source_cache_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'license':d.get('license'),'source_buildings_selected':count,'decorated_buildings':len(decorated),
        'decorated_osm_ids':decorated,'window_modules':windows,'shopfronts':doors,'parapet_edges':rails,
        'max_outward_projection_m':MAX_PROJECTION,'detail_triangles':w.triangles+s.triangles+g.triangles,
        'glb_size_bytes':dest.stat().st_size,'glb_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
        'model_anchor_world_cm':{'x':ox,'y':oy,'z':0},'photomatch_approved':False,
        'historical_facades_verified':False,'collision_tested':False,'navigation_tested':False,
        'unreal_import_tested':False,'multiplayer_tested':False,'performance_measured':False,
        'production_approved':False,
        'note':'visual art only; all OSM polygons remain untouched and existing Unreal maps unmodified'}
    man=outdir/'JED_AlBalad_ArchitecturalDetails_V4_manifest.json'
    if man.exists():raise FileExistsError(str(man))
    man.write_text(json.dumps(report,indent=2),encoding='utf-8')
    return report

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('outdir')
    o=p.parse_args();print(json.dumps(build_facades(o.source,o.outdir),indent=2))
