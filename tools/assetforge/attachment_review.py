"""Review-only attachment profile from original body/cape interface.
No render mesh mutation, rig correction, or Chaos Cloth simulation.
"""
import heapq
import numpy as np
from char022_cloth_topology import validate, components
from manifold_review import edge_uses


def attachment_profile(p, f, source_ids, shared, torso_weights, min_height=.67,
                       min_weight=.5, fade_distance=.20, max_distance=.12):
    p=np.asarray(p,dtype=float); f=np.asarray(f);validate(p,f)
    ids=np.asarray(source_ids);shared=np.asarray(shared);w=np.asarray(torso_weights,dtype=float)
    n=len(p)
    if ids.shape!=(n,) or ids.dtype.kind not in 'iu' or ids.min()<0:raise ValueError('invalid source lineage')
    if shared.shape!=(n,) or shared.dtype.kind!='b':raise ValueError('invalid shared mask')
    if w.shape!=(n,) or not np.isfinite(w).all() or np.any((w<0)|(w>1+1e-6)):raise ValueError('invalid torso weights')
    if not all(np.isfinite(x) for x in (min_height,min_weight,fade_distance,max_distance)) or not 0<=min_weight<=1 or fade_distance<=0 or max_distance<=0:raise ValueError('invalid thresholds')
    e=edge_uses(f)
    if any(len(v)>2 for v in e.values()):raise ValueError('nonmanifold input')
    boundary=np.zeros(n,bool)
    for (a,b),uses in e.items():
        if len(uses)==1:boundary[[a,b]]=True
    pinned=boundary&shared&(p[:,1]>=min_height)&(w>=min_weight)
    lab,sizes=components(f,n);simulate=np.zeros(n,bool);summary=[]
    for i,size in enumerate(sizes):
        v=np.unique(f[lab==i]);count=int(pinned[v].sum());simulate[v]=count>0
        summary.append(dict(component=i,faces=int(size),vertices=len(v),pins=count,policy='SIMULATION_REVIEW' if count else 'KEEP_ORIGINAL_SKINNED_STATIC'))
    # Dijkstra along actual mesh edges; disconnected parts cannot inherit pins.
    adj=[[] for _ in range(n)]
    for a,b in e:
        distance=float(np.linalg.norm(p[a]-p[b]));adj[a].append((b,distance));adj[b].append((a,distance))
    dist=np.full(n,np.inf);q=[]
    for v in np.flatnonzero(pinned):dist[v]=0;heapq.heappush(q,(0.,int(v)))
    while q:
        d,v=heapq.heappop(q)
        if d!=dist[v]:continue
        for b,c in adj[v]:
            nd=d+c
            if nd<dist[b]:dist[b]=nd;heapq.heappush(q,(nd,b))
    if np.any(simulate&~np.isfinite(dist)):raise ValueError('unreachable active vertices')
    values=np.zeros(n);values[simulate]=np.minimum(dist[simulate]/fade_distance,1)*max_distance
    return dict(pinned=pinned,simulate=simulate,max_distance=values,geodesic_distance=dist,components=summary,
                candidate_gate=bool(pinned.any()),boundary=boundary,source_vertex_ids=ids.copy())
