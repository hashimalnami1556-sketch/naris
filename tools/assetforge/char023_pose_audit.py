"""Offline glTF skin vs virtual hand socket audit, pinned original sword.
No Unreal Socket/cloth/combat animation is created or tested.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
from char023_weapon_review import read_glb, accessor_array, audit_source

def rotation(q):
    q=np.asarray(q,dtype=float)
    if q.shape!=(4,) or not np.isfinite(q).all() or np.linalg.norm(q)<1e-12:
        raise ValueError('Invalid glTF xyzw quaternion')
    x,y,z,w=q/np.linalg.norm(q)
    return np.array([
        [1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
        [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
        [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]],dtype=float)

def slerp(a,b,t):
    if not 0<=t<=1:raise ValueError('Interpolation outside range')
    a=np.asarray(a,float);b=np.asarray(b,float)
    a=a/np.linalg.norm(a);b=b/np.linalg.norm(b)
    dot=float(a@b)
    if dot<0:b=-b;dot=-dot
    if dot>.9995:
        q=a+t*(b-a)
        return q/np.linalg.norm(q)
    omega=np.arccos(np.clip(dot,-1,1))
    return (np.sin((1-t)*omega)*a+np.sin(t*omega)*b)/np.sin(omega)

def animation_rotations(doc,blob,t):
    if len(doc.get('animations',[]))!=1:raise ValueError('Expected exactly source Idle')
    anim=doc['animations'][0]
    if len(anim['channels'])!=1 or len(anim['samplers'])!=1:raise ValueError('Unexpected animation channels')
    c=anim['channels'][0];s=anim['samplers'][c['sampler']]
    if c['target']['path']!='rotation' or s.get('interpolation','LINEAR')!='LINEAR':
        raise ValueError('Only LINEAR quaternion channel supported')
    if doc['nodes'][c['target']['node']].get('name')!='chest':
        raise ValueError('Unexpected animation target')
    times=accessor_array(doc,blob,s['input']).ravel().astype(float)
    values=accessor_array(doc,blob,s['output']).astype(float)
    if len(times)!=len(values) or len(times)<2 or np.any(np.diff(times)<=0):
        raise ValueError('Invalid sampler')
    if t<times[0] or t>times[-1]:raise ValueError('Sample outside original Idle')
    if t==times[-1]:q=values[-1]
    else:
        k=int(np.searchsorted(times,t,side='right')-1)
        q=slerp(values[k],values[k+1],(t-times[k])/(times[k+1]-times[k]))
    return {c['target']['node']:q}

def world_matrices(doc,rotations=None):
    rotations=rotations or {}
    nodes=doc['nodes'];parent={}
    for i,n in enumerate(nodes):
        for child in n.get('children',[]):
            if child in parent:raise ValueError('Non-tree node hierarchy')
            parent[child]=i
    cache={}
    def solve(i,stack=()):
        if i in stack:raise ValueError('Node cycle')
        if i not in cache:
            n=nodes[i]
            if 'matrix' in n:raise ValueError('Matrix nodes not supported in pinned rig')
            tr=np.asarray(n.get('translation',[0,0,0]),float)
            sc=np.asarray(n.get('scale',[1,1,1]),float)
            if tr.shape!=(3,) or sc.shape!=(3,) or not np.isfinite(tr).all() or not np.isfinite(sc).all():
                raise ValueError('Invalid TRS')
            m=np.eye(4)
            m[:3,:3]=rotation(rotations.get(i,n.get('rotation',[0,0,0,1])))@np.diag(sc)
            m[:3,3]=tr
            cache[i]=solve(parent[i],stack+(i,))@m if i in parent else m
        return cache[i]
    for i in range(len(nodes)):solve(i)
    return cache

def joint_matrices(doc,blob,pose):
    skin=doc['skins'][0]
    bind_world=world_matrices(doc)
    pose_world=world_matrices(doc,pose)
    ibm=accessor_array(doc,blob,skin['inverseBindMatrices']).astype(float)
    j=np.array(skin['joints'],dtype=int)
    mats=np.stack([pose_world[int(i)]@ibm[k].reshape(4,4).T for k,i in enumerate(j)])
    residual=max(float(np.abs(bind_world[int(i)]@ibm[k].reshape(4,4).T-np.eye(4)).max())
                 for k,i in enumerate(j))
    return mats,bind_world,pose_world,residual

def skin_subset(doc,blob,ids,mats):
    pr=doc['meshes'][0]['primitives'][0]
    p=accessor_array(doc,blob,pr['attributes']['POSITION'])[ids].astype(float)
    j=accessor_array(doc,blob,pr['attributes']['JOINTS_0'])[ids].astype(int)
    w=accessor_array(doc,blob,pr['attributes']['WEIGHTS_0'])[ids].astype(float)
    ph=np.c_[p,np.ones(len(p))]
    result=np.zeros((len(p),4),dtype=float)
    for k in range(4):
        result+=np.einsum('nij,nj->ni',mats[j[:,k]],ph)*w[:,k,None]
    return result[:,:3]

def rigid_from_hand(rest_positions,hand_bind,hand_pose):
    p=np.asarray(rest_positions,float)
    if p.ndim!=2 or p.shape[1]!=3:raise ValueError('Invalid source positions')
    pts=np.c_[p,np.ones(len(p))]
    return (hand_pose@np.linalg.inv(hand_bind)@pts.T).T[:,:3]

def edge_strain(faces,vertex_ids,rest,posed,min_edge=1e-5):
    lut={int(v):i for i,v in enumerate(vertex_ids)}
    edges=set()
    for a,b,c in faces:
        for u,v in ((a,b),(b,c),(c,a)):
            u,v=sorted((lut[int(u)],lut[int(v)]));edges.add((u,v))
    ed=np.asarray(sorted(edges),dtype=int)
    length=np.linalg.norm(rest[ed[:,0]]-rest[ed[:,1]],axis=1)
    pos_length=np.linalg.norm(posed[ed[:,0]]-posed[ed[:,1]],axis=1)
    selection=length>=min_edge
    strain=np.abs(pos_length[selection]-length[selection])/length[selection]
    if not len(strain):raise ValueError('No measurable edges')
    return {'measured_edges':int(selection.sum()),
        'max_relative_edge_change':float(strain.max()),
        'mean_relative_edge_change':float(strain.mean()),
        'p95_relative_edge_change':float(np.quantile(strain,.95))}

def evaluate(path,samples=(0.,.75,1.5),synthetic_degrees=(0.,90.,180.,270.,360.)):
    path=Path(path);source=path.read_bytes()
    d,b=read_glb(path)
    pr,f,lab,mask=audit_source(d,b,hashlib.sha256(source).hexdigest())
    selected=f[mask['guard']|mask['blade']]
    vertex_ids=np.unique(selected)
    p=accessor_array(d,b,pr['attributes']['POSITION'])[vertex_ids].astype(float)
    joints=d['skins'][0]['joints']
    hand_node=next(i for i in joints if d['nodes'][i].get('name')=='hand_L')
    grip=np.array([-0.21847540140151978,.41860198974609375,.0351867601275444])
    bind=world_matrices(d)
    hand_bind=bind[hand_node]
    offset=np.linalg.inv(hand_bind)@np.r_[grip,1.]
    result=[]
    for t in samples:
        pose=animation_rotations(d,b,t)
        skin_mats,_,posed,err=joint_matrices(d,b,pose)
        skinned=skin_subset(d,b,vertex_ids,skin_mats)
        rigid=rigid_from_hand(p,hand_bind,posed[hand_node])
        actual_grip=(posed[hand_node]@offset)[:3]
        projected_grip=(posed[hand_node]@np.linalg.inv(hand_bind)@np.r_[grip,1.])[:3]
        assert np.allclose(actual_grip,projected_grip,atol=1e-10)
        e0=edge_strain(selected,vertex_ids,p,skinned)
        e1=edge_strain(selected,vertex_ids,p,rigid)
        result.append({'source_idle_time_s':float(t),'original_skinned':e0,'rigid_hand_mount':e1,
            'mean_displacement_original_vs_hand_mount':float(np.linalg.norm(skinned-rigid,axis=1).mean()),
            'max_displacement_original_vs_hand_mount':float(np.linalg.norm(skinned-rigid,axis=1).max()),
            'grip_socket_world':actual_grip.tolist(),'bind_identity_error':err})
    turns=[]
    hand_base=world_matrices(d)[hand_node]
    for degree in synthetic_degrees:
        a=np.deg2rad(degree)
        wrist=np.eye(4)
        wrist[:3,:3]=rotation([0,0,np.sin(a/2),np.cos(a/2)])
        moved=hand_base@wrist
        pts=rigid_from_hand(p,hand_bind,moved)
        e=edge_strain(selected,vertex_ids,p,pts)
        grip_expected=(moved@offset)[:3]
        grip_actual=(moved@np.linalg.inv(hand_bind)@np.r_[grip,1.])[:3]
        turns.append({'wrist_rotation_degrees_synthetic':float(degree),
            'max_relative_edge_change':e['max_relative_edge_change'],
            'grip_constraint_error':float(np.linalg.norm(grip_expected-grip_actual))})
    grip_matrix=np.eye(4);grip_matrix[:3,3]=grip
    return {'id':'CHAR-023-POSE-VERIFY','source_sha256':hashlib.sha256(source).hexdigest(),
        'source_animation':'A_Character1_Idle','source_animated_node':'chest',
        'hand_mount_parent':'hand_L','hand_socket_offset_glTF_Y_up':offset[:3].tolist(),
        'hand_socket_matrix_row_major_glTF_Y_up':(np.linalg.inv(hand_bind)@grip_matrix).tolist(),
        'sampled_original_idle':result,'synthetic_wrist_turns':turns,
        'evaluated_sword_vertices':len(vertex_ids),'evaluated_sword_faces':len(selected),
        'engine_import':'NOT_RUN','weapon_socket_in_unreal':'NOT_CREATED',
        'combat_animations':'NOT_PRESENT','360_actor_runtime':'NOT_RUN',
        'visual_grip_approval':False,'release_approved':False,
        'limitations':'Only source Idle and synthetic isolated wrist rotations. Rigidness does not prove grip/hand clipping, combat coverage or correct original weapon component selection.'}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',required=True,type=Path)
    ap.add_argument('--output',required=True,type=Path)
    a=ap.parse_args()
    if a.output.exists():raise SystemExit('Refusing to overwrite evidence')
    r=evaluate(a.source)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'samples':r['sampled_original_idle'],
        'synthetic_wrist_turns':r['synthetic_wrist_turns']},indent=2))

if __name__=='__main__':main()
