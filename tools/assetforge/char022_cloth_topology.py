"""CHAR-022: review-only simulation topology cleanup; never mutate render GLB."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np

SOURCE_SHA='8ee9a1577836373e2764fc75ceddbb21329806f6938a751dab499edc6ca3d887'

def validate(p,f):
    if p.ndim!=2 or p.shape[1]!=3 or not len(p) or not np.isfinite(p).all():raise ValueError('invalid positions')
    if f.ndim!=2 or f.shape[1]!=3 or not len(f) or f.dtype.kind not in 'iu' or f.min()<0 or f.max()>=len(p):raise ValueError('invalid faces')

def components(f,n):
    parent=list(range(n))
    def root(i):
        while parent[i]!=i:
            parent[i]=parent[parent[i]];i=parent[i]
        return i
    for a,b,c in f.tolist():
        x,y,z=root(a),root(b),root(c);parent[y]=x;parent[z]=x
    _,lab=np.unique([root(int(a)) for a in f[:,0]],return_inverse=True)
    return lab,np.bincount(lab)

def topology(p,f):
    validate(p,f)
    oriented=np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]])
    edges=np.sort(oriented,axis=1)
    u,inv,c=np.unique(edges,axis=0,return_inverse=True,return_counts=True)
    direction=np.where(oriented[:,0]<oriented[:,1],1,-1)
    balance=np.bincount(inv,weights=direction,minlength=len(u))
    boundary=u[c==1];degree=np.bincount(boundary.ravel(),minlength=len(p))
    area2=np.linalg.norm(np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]]),axis=1)
    lab,sizes=components(f,len(p))
    return {'vertices':int(len(np.unique(f))), 'faces':len(f),'components':len(sizes),'component_faces':sorted(sizes.tolist(),reverse=True),
            'boundary_edges':int((c==1).sum()),'branching_boundary_vertices':int((degree>2).sum()),
            'nonmanifold_edges':int((c>2).sum()),'orientation_conflicts':int(((c==2)&(np.abs(balance)>0)).sum()),
            'duplicate_faces':len(f)-len(np.unique(np.sort(f,axis=1),axis=0)), 'degenerate_faces':int((area2<=1e-12).sum())}

def clean_candidate(p,f,min_faces=100,weld_grid=1e-6):
    p=np.asarray(p,dtype=float);f=np.asarray(f);validate(p,f)
    if min_faces<1 or not np.isfinite(weld_grid) or weld_grid<=0:raise ValueError('invalid cleanup settings')
    # Quantized-cell welding is deliberately not a distance-based weld.
    _,first,inv=np.unique(np.round(p/weld_grid).astype(np.int64),axis=0,return_index=True,return_inverse=True)
    wp=p[first];wf=inv[f];before=topology(wp,wf)
    area2=np.linalg.norm(np.cross(wp[wf[:,1]]-wp[wf[:,0]],wp[wf[:,2]]-wp[wf[:,0]]),axis=1)
    valid=np.flatnonzero(area2>1e-12);deg=np.flatnonzero(area2<=1e-12)
    if not len(valid):raise ValueError('no valid faces')
    _,first_face=np.unique(np.sort(wf[valid],axis=1),axis=0,return_index=True)
    unique=valid[np.sort(first_face)];dups=np.setdiff1d(valid,unique)
    lab,sizes=components(wf[unique],len(wp));keep=sizes[lab]>=min_faces
    ids=unique[keep];islands=unique[~keep]
    if not len(ids):raise ValueError('all components below minimum size')
    used,remap=np.unique(wf[ids],return_inverse=True);out=remap.reshape(-1,3)
    after=topology(wp[used],out)
    passed=not any(after[k] for k in ['nonmanifold_edges','orientation_conflicts','duplicate_faces','degenerate_faces','branching_boundary_vertices'])
    return {'positions':wp[used],'faces':out,'source_vertex_ids':first[used],'face_ids':ids,'before':before,'after':after,
            'removed_degenerate_ids':deg.tolist(),'removed_duplicate_ids':dups.tolist(),'removed_island_ids':islands.tolist(),'topology_pass':passed}

def main():
    from char022_repair_skin import read_glb,array
    a=argparse.ArgumentParser();a.add_argument('source',type=Path);a.add_argument('output_dir',type=Path);args=a.parse_args()
    if hashlib.sha256(args.source.read_bytes()).hexdigest()!=SOURCE_SHA:raise SystemExit('source hash mismatch')
    if args.output_dir.exists():raise SystemExit('refusing overwrite')
    d,b=read_glb(args.source);pr=d['meshes'][0]['primitives']
    if len(pr)!=2 or pr[1].get('extras',{}).get('naris_section')!='Cape_Candidate_Review':raise SystemExit('unexpected candidate')
    p=array(d,b,pr[1]['attributes']['POSITION']);f=array(d,b,pr[1]['indices']).reshape(-1,3)
    r=clean_candidate(p,f);args.output_dir.mkdir(parents=True)
    with (args.output_dir/'cape_simulation_review.obj').open('x') as o:
        o.write('# REVIEW ONLY; glTF Y-up source coordinates; no material or cloth weights\n')
        for v in r['positions']:o.write('v %.9g %.9g %.9g\n'%tuple(v))
        for t in r['faces']:o.write('f %d %d %d\n'%tuple(t+1))
    mapping={'source_vertex_ids':r['source_vertex_ids'].tolist(),'source_cape_section_face_ids':r['face_ids'].tolist()}
    (args.output_dir/'mapping.json').write_text(json.dumps(mapping,separators=(',',':'))+'\n')
    report={k:v for k,v in r.items() if k not in ['positions','faces','source_vertex_ids','face_ids']}
    report.update({'id':'CHAR-022-CLOTH-QA','source_sha256':SOURCE_SHA,'weld_grid_source_units':1e-6,'min_component_faces':100,'simulation_status':'REVIEW_ONLY_BLOCKED','render_glb_modified':False,'physics_test':'NOT_RUN','pin_weights':'NOT_AUTHORED','ue_import':'NOT_RUN'})
    (args.output_dir/'qa_report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['before','after','topology_pass','simulation_status']},indent=2))
if __name__=='__main__':main()
