"""CHAR-022: repair audited 18-joint GLB prototype, without editing source art."""
import argparse, copy, hashlib, json, struct
from pathlib import Path
import numpy as np

def read_glb(path):
    b=Path(path).read_bytes()
    magic,ver,total=struct.unpack_from('<4sII',b)
    if (magic,ver,total)!=(b'glTF',2,len(b)): raise ValueError('invalid GLB header')
    n,typ=struct.unpack_from('<I4s',b,12)
    if typ!=b'JSON': raise ValueError('invalid JSON chunk')
    k=20+n
    m,typ=struct.unpack_from('<I4s',b,k)
    if typ!=b'BIN\0' or k+8+m!=len(b): raise ValueError('invalid BIN chunk')
    return json.loads(b[20:k]),b[k+8:]

def array(doc,blob,i):
    a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']]
    dt=np.dtype({5126:'<f4',5121:'u1',5123:'<u2',5125:'<u4'}[a['componentType']])
    d={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']]
    off=v.get('byteOffset',0)+a.get('byteOffset',0)
    stride=v.get('byteStride',d*dt.itemsize)
    return np.ndarray((a['count'],d),dtype=dt,buffer=blob,offset=off,strides=(stride,dt.itemsize))

def world_matrices(doc):
    nodes=doc['nodes'];out={};parent={}
    for i,n in enumerate(nodes):
        for ch in n.get('children',[]):
            if ch in parent: raise ValueError('multiple parents')
            parent[ch]=i
    def get(i,seen=()):
        if i in seen: raise ValueError('cycle')
        if i not in out:
            n=nodes[i]
            if any(x in n for x in ('matrix','rotation','scale')):
                raise ValueError('only audited translation-only bind pose supported')
            m=np.eye(4);m[:3,3]=n.get('translation',[0,0,0])
            out[i]=get(parent[i],seen+(i,))@m if i in parent else m
        return out[i]
    for i in range(len(nodes)): get(i)
    return out

def audit(doc,blob):
    if len(doc.get('skins',[]))!=1: raise ValueError('expected exact prototype one skin')
    skin=doc['skins'][0];joint_ids=skin['joints']
    mesh_ids=[i for i,n in enumerate(doc['nodes']) if 'mesh' in n]
    if len(mesh_ids)!=1: raise ValueError('expected one mesh node')
    node=doc['nodes'][mesh_ids[0]]
    p=doc['meshes'][node['mesh']]['primitives'][0];attrs=p['attributes']
    j=array(doc,blob,attrs['JOINTS_0']);w=array(doc,blob,attrs['WEIGHTS_0'])
    positions=array(doc,blob,attrs['POSITION']);idx=array(doc,blob,p['indices'])
    mat=array(doc,blob,skin['inverseBindMatrices']);world=world_matrices(doc)
    if not np.isfinite(w).all() or np.any(w<0) or int(j.max())>=len(joint_ids) or not np.allclose(w.sum(axis=1),1,atol=1e-5):
        raise ValueError('invalid weights or joint indices')
    if len(j)!=len(positions) or len(w)!=len(positions) or len(mat)!=len(joint_ids) or idx.max()>=len(positions):
        raise ValueError('inconsistent mesh/skin counts')
    err=max(float(np.abs(world[k]@mat[i].reshape(4,4).T-np.eye(4)).max()) for i,k in enumerate(joint_ids))
    return {'mesh_node':mesh_ids[0],'skin_bound':node.get('skin')==0,
        'scene_root_mesh':mesh_ids[0] in doc['scenes'][doc.get('scene',0)]['nodes'],
        'joints':len(joint_ids),'vertices':len(positions),'triangles':len(idx)//3,
        'animation_count':len(doc.get('animations',[])),
        'weight_sum_max_error':float(np.abs(w.sum(axis=1)-1).max()),
        'bind_identity_max_error':err,'materials':len(doc.get('materials',[]))}

def repair(doc,blob):
    before=audit(doc,blob)
    if before['skin_bound'] or before['joints']!=18 or before['mesh_node']!=18:
        raise ValueError('unexpected prototype layout; refuse mutation')
    d=copy.deepcopy(doc);result=bytearray(blob);mesh=before['mesh_node']
    skin=d['skins'][0];world=world_matrices(doc)
    a=array(d,result,skin['inverseBindMatrices'])
    for i,k in enumerate(skin['joints']):
        a[i]=np.linalg.inv(world[k]).T.reshape(16)
    for n in d['nodes']:
        if mesh in n.get('children',[]): n['children'].remove(mesh)
    d['scenes'][d.get('scene',0)]['nodes'].append(mesh)
    d['nodes'][mesh]['skin']=0
    after=audit(d,result)
    if not after['skin_bound'] or not after['scene_root_mesh'] or after['bind_identity_max_error']>1e-6:
        raise ValueError('repair failed')
    return d,bytes(result)

def write_glb(path,doc,blob):
    raw=json.dumps(doc,separators=(',',':'),ensure_ascii=False).encode()
    raw+=b' '*(-len(raw)%4);blob+=b'\0'*(-len(blob)%4)
    content=struct.pack('<I4s',len(raw),b'JSON')+raw+struct.pack('<I4s',len(blob),b'BIN\0')+blob
    Path(path).write_bytes(struct.pack('<4sII',b'glTF',2,len(content)+12)+content)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('source',type=Path);p.add_argument('output',type=Path)
    p.add_argument('--report',type=Path,required=True);args=p.parse_args()
    if args.source.resolve()==args.output.resolve() or args.output.exists():
        raise SystemExit('Refusing overwrite')
    d,b=read_glb(args.source);a=audit(d,b);e,c=repair(d,b)
    write_glb(args.output,e,c);rd,rb=read_glb(args.output);z=audit(rd,rb)
    ib=d['accessors'][d['skins'][0]['inverseBindMatrices']]
    v=d['bufferViews'][ib['bufferView']]
    o=v.get('byteOffset',0)+ib.get('byteOffset',0);end=o+ib['count']*64
    assert b[:o]==rb[:o] and b[end:]==rb[end:],'non-bind binary bytes changed'
    report={'id':'CHAR-022','before':a,'after':z,
        'source_sha256':hashlib.sha256(args.source.read_bytes()).hexdigest(),
        'output_sha256':hashlib.sha256(args.output.read_bytes()).hexdigest(),
        'non_bind_binary_bytes_unchanged':True,
        'geometry_material_animation_metadata_unchanged':all(d[k]==rd[k] for k in ['meshes','materials','animations','images','textures','accessors']),
        'ue_cloth_test':'NOT_RUN','ue_import':'NOT_RUN','production_rig':'NOT_COMPLETE'}
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__': main()
