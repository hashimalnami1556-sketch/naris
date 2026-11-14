"""Conservative review-only mesh repair. Never modifies render source.
Drops faces incident to nonmanifold edges, splits disconnected vertex fans,
then orients each connected face component. No surface filling or re-welding.
"""
from collections import defaultdict, deque
import numpy as np
from char022_cloth_topology import topology, validate, components

def edge_uses(f):
    e=defaultdict(list)
    for i,t in enumerate(f.tolist()):
        for a,b in zip(t,t[1:]+t[:1]):e[min(a,b),max(a,b)].append((i,1 if a<b else -1))
    return e

def repair(p,f):
    p=np.asarray(p,dtype=float);f=np.asarray(f);validate(p,f)
    before=topology(p,f);e=edge_uses(f)
    remove=sorted({i for uses in e.values() if len(uses)>2 for i,_ in uses})
    keep=np.ones(len(f),bool);keep[remove]=False;ids=np.flatnonzero(keep)
    if not len(ids):raise ValueError('no faces survive')
    g=f[ids].copy();e=edge_uses(g)
    incident=defaultdict(list);adj=defaultdict(lambda:defaultdict(list))
    for i,t in enumerate(g.tolist()):
        for v in t:incident[v].append(i)
    for (a,b),uses in e.items():
        if len(uses)==2:
            i,j=uses[0][0],uses[1][0]
            for v in (a,b):adj[v][i].append(j);adj[v][j].append(i)
    newp=[];source=[];out=g.copy()
    for v,faces in sorted(incident.items()):
        remaining=set(faces)
        while remaining:
            seed=min(remaining);remaining.remove(seed);q=[seed];fan=[]
            while q:
                i=q.pop();fan.append(i)
                for j in adj[v][i]:
                    if j in remaining:remaining.remove(j);q.append(j)
            k=len(newp);newp.append(p[v]);source.append(v)
            for i in fan:out[i,g[i]==v]=k
    newp=np.asarray(newp);source=np.asarray(source,dtype=np.int64)
    neighbors=defaultdict(list)
    for uses in edge_uses(out).values():
        if len(uses)==2:
            (i,a),(j,b)=uses;different=int(a==b)
            neighbors[i].append((j,different));neighbors[j].append((i,different))
    parity=np.full(len(out),-1,dtype=int);conflicts=set()
    for seed in range(len(out)):
        if parity[seed]>=0:continue
        parity[seed]=0;q=deque([seed])
        while q:
            i=q.popleft()
            for j,d in neighbors[i]:
                expected=parity[i]^d
                if parity[j]<0:parity[j]=expected;q.append(j)
                elif parity[j]!=expected:conflicts.add(tuple(sorted((i,j))))
    flipped=np.flatnonzero(parity==1);out[flipped]=out[flipped][:,[0,2,1]]
    after=topology(newp,out)
    passed=not conflicts and not any(after[k] for k in ['nonmanifold_edges','orientation_conflicts','duplicate_faces','degenerate_faces','branching_boundary_vertices'])
    return dict(positions=newp,faces=out,input_vertex_ids=source,input_face_ids=ids,before=before,after=after,removed_faces=remove,flipped_faces=ids[flipped].tolist(),orientation_parity_conflicts=len(conflicts),topology_pass=bool(passed))

def pin_profile(p,f,anchors,pin_radius=.04,fade_radius=.20,max_distance=.12):
    """Provisional source-coordinate distance profile, not authored cloth weights."""
    p=np.asarray(p,float);f=np.asarray(f);anchors=np.asarray(anchors,float);validate(p,f)
    if anchors.ndim!=2 or anchors.shape[1]!=3 or not len(anchors) or not np.isfinite(anchors).all() or not 0<pin_radius<fade_radius or max_distance<=0:raise ValueError('invalid anchors/settings')
    distance=np.linalg.norm(p[:,None,:]-anchors[None,:,:],axis=2).min(axis=1)
    values=np.clip((distance-pin_radius)/(fade_radius-pin_radius),0,1)*max_distance
    lab,sizes=components(f,len(p));result=[]
    for i in range(len(sizes)):
        verts=np.unique(f[lab==i]);count=int((values[verts]==0).sum())
        result.append({'component':i,'faces':int(sizes[i]),'vertices':len(verts),'pinned_vertices':count,'min_anchor_distance':float(distance[verts].min())})
    unanchored=[r['component'] for r in result if not r['pinned_vertices']]
    return {'max_distance':values,'components':result,'unanchored_components':unanchored,'pin_gate':not unanchored}

def prune_islands(r,min_faces=100):
    """Review-only filter; keep exact input face and vertex lineage."""
    if min_faces<1:raise ValueError('invalid minimum')
    f=r['faces'];p=r['positions'];lab,sizes=components(f,len(p));keep=sizes[lab]>=min_faces
    if not keep.any():raise ValueError('no component survives')
    used,inv=np.unique(f[keep],return_inverse=True);out=inv.reshape(-1,3);after=topology(p[used],out)
    return dict(r,positions=p[used],faces=out,input_vertex_ids=r['input_vertex_ids'][used],input_face_ids=r['input_face_ids'][keep],after=after,removed_island_faces=r['input_face_ids'][~keep].tolist(),topology_pass=bool(r['topology_pass'] and not any(after[k] for k in ['nonmanifold_edges','orientation_conflicts','duplicate_faces','degenerate_faces','branching_boundary_vertices'])))

def capsule_review(p,capsules):
    """Rest-pose vertex clearance against provisional capsules, not cloth simulation."""
    p=np.asarray(p,float)
    if p.ndim!=2 or p.shape[1]!=3 or not len(p) or not np.isfinite(p).all() or not capsules:raise ValueError('invalid capsule input')
    minimum=np.full(len(p),np.inf);report=[]
    for name,a,b,radius in capsules:
        a=np.asarray(a,float);b=np.asarray(b,float);v=b-a
        if a.shape!=(3,) or b.shape!=(3,) or not np.isfinite(a).all() or not np.isfinite(b).all() or not np.isfinite(radius) or radius<=0 or np.dot(v,v)<=0:raise ValueError('invalid capsule')
        t=np.clip(((p-a)@v)/np.dot(v,v),0,1);closest=a+t[:,None]*v
        gap=np.linalg.norm(p-closest,axis=1)-radius
        minimum=np.minimum(minimum,gap)
        report.append(dict(name=name,start=a.tolist(),end=b.tolist(),radius=float(radius),vertices_inside=int((gap<0).sum()),minimum_clearance=float(gap.min())))
    return dict(clearance=minimum,summary=report,inside_any=int((minimum<0).sum()))
