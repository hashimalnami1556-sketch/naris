"""Consolidate rigid/TRS GLB skins, preserving source bind transforms and motion.
Only handles unit-scale, rigid transforms and LINEAR/STEP samplers. Unsupported
sources fail rather than silently degrading. Geometry-derived pivots are provisional.
No external dependencies; no production/engine approval is implied.
"""
import argparse,bisect,copy,hashlib,json,math,pathlib,struct
I=[1.,0,0,0,0,1.,0,0,0,0,1.,0,0,0,0,1.]
SIZE={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
FORM={5121:'B',5123:'H',5125:'I',5126:'f'}
def mul(a,b):return [sum(a[r*4+k]*b[k*4+c] for k in range(4))for r in range(4)for c in range(4)]
def inverse(a):
 r=[a[c*4+r] if r<3 and c<3 else I[r*4+c] for r in range(4)for c in range(4)]
 for i in range(3):r[i*4+3]=-sum(r[i*4+j]*a[j*4+3]for j in range(3))
 return r
def translate(v):
 a=I[:]
 for i in range(3):a[i*4+3]=v[i]
 return a
def quaternion(m):
 trace=m[0]+m[5]+m[10]
 if trace>0:
  s=math.sqrt(trace+1)*2;q=[(m[9]-m[6])/s,(m[2]-m[8])/s,(m[4]-m[1])/s,.25*s]
 else:
  i=max(range(3),key=lambda i:m[i*4+i]);j=(i+1)%3;k=(i+2)%3;s=math.sqrt(1+m[i*4+i]-m[j*4+j]-m[k*4+k])*2
  q=[0.,0.,0.,0.];q[i]=.25*s;q[j]=(m[j*4+i]+m[i*4+j])/s;q[k]=(m[k*4+i]+m[i*4+k])/s;q[3]=(m[k*4+j]-m[j*4+k])/s
 norm=math.sqrt(sum(x*x for x in q));return [x/norm for x in q]
def matrix(node):
 if 'matrix'in node:return [node['matrix'][c*4+r]for r in range(4)for c in range(4)]
 if any(abs(x-1)>1e-5 for x in node.get('scale',[1,1,1])):raise ValueError('non-unit scale unsupported')
 x,y,z,w=node.get('rotation',[0,0,0,1]);a=[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),0,2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),0,2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y),0,0,0,0,1]
 for i,t in enumerate(node.get('translation',[0,0,0])):a[i*4+3]=t
 return a
def read(path):
 raw=pathlib.Path(path).read_bytes()
 if struct.unpack_from('<4sII',raw)!=(b'glTF',2,len(raw)):raise ValueError('invalid GLB header')
 off=12;doc=None;binary=None
 while off<len(raw):
  length,kind=struct.unpack_from('<II',raw,off);chunk=raw[off+8:off+8+length];off+=8+length
  if kind==0x4e4f534a:doc=json.loads(chunk)
  elif kind==0x004e4942:binary=chunk
 if doc is None or binary is None:raise ValueError('missing chunks')
 return doc,binary
def values(d,b,index):
 a=d['accessors'][index]
 if 'sparse'in a:raise ValueError('sparse accessor unsupported')
 v=d['bufferViews'][a['bufferView']]
 if v.get('buffer',0)!=0:raise ValueError('external buffer unsupported')
 fmt='<'+FORM[a['componentType']]*SIZE[a['type']];size=struct.calcsize(fmt);stride=v.get('byteStride',size);offset=v.get('byteOffset',0)+a.get('byteOffset',0)
 return [list(struct.unpack_from(fmt,b,offset+i*stride))for i in range(a['count'])]
def append(d,b,rows,kind,ctype=5126):
 while len(b)%4:b.append(0)
 fmt='<'+FORM[ctype]*SIZE[kind];data=b''.join(struct.pack(fmt,*r)for r in rows)
 view=len(d['bufferViews']);d['bufferViews'].append({'buffer':0,'byteOffset':len(b),'byteLength':len(data)});b.extend(data)
 index=len(d['accessors']);accessor={'bufferView':view,'componentType':ctype,'count':len(rows),'type':kind}
 if kind=='SCALAR':accessor.update(min=[min(r[0]for r in rows)],max=[max(r[0]for r in rows)])
 d['accessors'].append(accessor);return index
def sample(times,rows,t,path,mode):
 if t<=times[0]:return rows[0][:]
 if t>=times[-1]:return rows[-1][:]
 i=bisect.bisect_right(times,t)-1
 if mode=='STEP':return rows[i][:]
 f=(t-times[i])/(times[i+1]-times[i]);a=rows[i];b=rows[i+1]
 if path=='rotation':
  dot=sum(x*y for x,y in zip(a,b))
  if dot<0:b=[-x for x in b];dot=-dot
  if dot<.9995:
   angle=math.acos(min(1,dot));s=math.sin(angle);return [(math.sin((1-f)*angle)*x+math.sin(f*angle)*y)/s for x,y in zip(a,b)]
 out=[x+(y-x)*f for x,y in zip(a,b)]
 if path=='rotation':
  norm=math.sqrt(sum(x*x for x in out));out=[x/norm for x in out]
 return out
def globals_at(d,b,clip=None,t=0):
 nodes=copy.deepcopy(d['nodes'])
 if clip:
  for c in clip['channels']:
   s=clip['samplers'][c['sampler']];mode=s.get('interpolation','LINEAR');path=c['target']['path']
   if mode not in ['LINEAR','STEP'] or path not in ['translation','rotation']:raise ValueError('unsupported animation sampler/path')
   ts=[r[0]for r in values(d,b,s['input'])];rs=values(d,b,s['output']);nodes[c['target']['node']][path]=sample(ts,rs,t,path,mode)
 parents={}
 for i,n in enumerate(nodes):
  for child in n.get('children',[]):
   if child in parents:raise ValueError('multiple parents')
   parents[child]=i
 memo={};visiting=set()
 def get(i):
  if i in visiting:raise ValueError('node cycle')
  if i not in memo:
   visiting.add(i);local=matrix(nodes[i]);memo[i]=mul(get(parents[i]),local)if i in parents else local;visiting.remove(i)
  return memo[i]
 return [get(i)for i in range(len(nodes))]
def anatomical(name,names):
 n=name.lower().removeprefix('j_')
 if n in ['root','pelvis']:p='root' if n=='pelvis' else None
 elif n in ['spine','torso_obsidian']:p='pelvis'
 elif n=='head':p='torso_obsidian' if 'j_torso_obsidian'in names else 'spine'
 elif n=='jaw' or n.startswith(('horn_base','eye')):p='head'
 elif n.startswith('horn_tip'):p=n.replace('horn_tip','horn_base')
 elif n.startswith(('pauldron','upper_arm')):p='torso_obsidian'
 elif n.startswith('forearm'):p=n.replace('forearm','upper_arm')
 elif n.startswith('claw'):p=n.replace('claw','forearm')
 elif n.startswith('thigh') or n.startswith('leg'):p='pelvis'
 elif n.startswith('shin'):p=n.replace('shin','thigh')
 elif n.startswith('foot'):p=n.replace('foot','shin')
 elif n.startswith('arm'):p='spine'
 elif n.startswith('magma'):p='torso_obsidian'
 elif n=='loincloth':p='pelvis'
 else:p=None
 return names.get('j_'+p)if p else None
def unify(source,destination,hz=60):
 if hz<=0:raise ValueError('hz must be positive')
 if pathlib.Path(source).resolve()==pathlib.Path(destination).resolve():raise ValueError('preserve original source')
 src,original=read(source);d=copy.deepcopy(src);b=bytearray(original);skins=src.get('skins',[])
 if not skins:raise ValueError('no skins')
 joints=[];ibm={};mesh_nodes=[(i,n)for i,n in enumerate(src['nodes'])if 'mesh'in n and 'skin'in n]
 for skin in skins:
  mats=values(src,original,skin['inverseBindMatrices'])if 'inverseBindMatrices'in skin else [I for _ in skin['joints']]
  for j,m in zip(skin['joints'],mats):
   row=[m[c*4+r]for r in range(4)for c in range(4)]
   if j in ibm and ibm[j]!=row:raise ValueError('joint with conflicting bind matrices')
   if j not in joints:joints.append(j)
   ibm[j]=row
 source_parents={c:i for i,n in enumerate(src['nodes']) for c in n.get('children',[])}
 def ancestors(j):
  chain=[j]
  while chain[-1] in source_parents:chain.append(source_parents[chain[-1]])
  return chain
 common=next((n for n in ancestors(joints[0]) if all(n in ancestors(j) for j in joints)),None)
 detached_root=mesh_nodes[0][0] if common is None and len(mesh_nodes)==1 else None
 root_driver=common if common is not None else detached_root
 def root_world(world):return world[root_driver] if root_driver is not None else I
 rest=globals_at(src,original);pivots={j:[0.,0.,0.]for j in joints}
 # Rigid per-part skins use geometry-derived provisional joint locations.
 if len(skins)>1:
  for _,node in mesh_nodes:
   skin=skins[node['skin']]
   if len(skin['joints'])!=1:raise ValueError('multi-skin repair limited to rigid one-joint parts')
   positions=[v for prim in src['meshes'][node['mesh']]['primitives']for v in values(src,original,prim['attributes']['POSITION'])]
   pivots[skin['joints'][0]]=[sum(v[k]for v in positions)/len(positions)for k in range(3)]
 root=len(d['nodes']);d['nodes'].append({'name':'NARIS_Root','children':[]})
 names={d['nodes'][j].get('name','').lower():j for j in joints}
 parents={j:anatomical(d['nodes'][j].get('name',''),names) for j in joints}
 for j in joints:
  if parents[j] is None:parents[j]=root
 def desired(world,j):
  w=mul(root_world(world),world[j]) if detached_root is not None else world[j]
  return mul(w,translate(pivots[j]))
 for j in joints:
  # Remove old placements of joints from their original parents.
  for n in d['nodes']:n['children']=[c for c in n.get('children',[])if c!=j]
 for j in joints:d['nodes'][parents[j]].setdefault('children',[]).append(j)
 for scene in d.get('scenes',[]):scene['nodes']=[n for n in scene.get('nodes',[])if n not in joints]+[root]
 def local(world,j):return mul(inverse(desired(world,parents[j]) if parents[j]!=root else root_world(world)),desired(world,j))
 rm=root_world(rest);d['nodes'][root]['translation']=[rm[3],rm[7],rm[11]];d['nodes'][root]['rotation']=quaternion(rm)
 for j in joints:
  n=d['nodes'][j];m=local(rest,j);n.pop('matrix',None);n.pop('scale',None);n['translation']=[m[3],m[7],m[11]];n['rotation']=quaternion(m)
 # Mesh placement animation used to be a joint ancestor. Bake it into the rig;
 # keep mesh nodes in scene for skinning but remove their old animated transforms.
 for _,node in mesh_nodes:
  node_index=next(i for i,n in enumerate(src['nodes'])if n is node)
  out=d['nodes'][node_index];out['skin']=0
  for key in ['matrix','translation','rotation','scale']:out.pop(key,None)
  for prim in d['meshes'][node['mesh']]['primitives']:
   old=values(src,original,prim['attributes']['JOINTS_0']);weights=values(src,original,prim['attributes']['WEIGHTS_0']);mapping=skins[node['skin']]['joints'];rows=[[joints.index(mapping[k])+1 if w>0 else 0 for k,w in zip(row,ws)]for row,ws in zip(old,weights)]
   prim['attributes']['JOINTS_0']=append(d,b,rows,'VEC4',5123)
 for index,_ in mesh_nodes:
  for n in d['nodes']:
   if 'children'in n:n['children']=[c for c in n['children']if c!=index]
  for scene in d.get('scenes',[]):
   if index not in scene['nodes']:scene['nodes'].append(index)
 matrices=[I]+[mul(translate([-v for v in pivots[j]]),ibm[j])for j in joints]
 acc=append(d,b,[[m[r*4+c]for c in range(4)for r in range(4)]for m in matrices],'MAT4')
 d['skins']=[{'name':'NARIS_Unified_Provisional','skeleton':root,'joints':[root]+joints,'inverseBindMatrices':acc}]
 d['animations']=[]
 for clip in src.get('animations',[]):
  times=sorted(set(t[0]for s in clip['samplers']for t in values(src,original,s['input'])))
  if any(s.get('interpolation','LINEAR')!='LINEAR' for s in clip['samplers']):raise ValueError('rebake currently requires LINEAR sampling')
  duration=times[-1];times=sorted(set(struct.unpack('<f',struct.pack('<f',t))[0]for t in times+[min(duration,k/hz)for k in range(math.ceil(duration*hz)+1)]));ta=append(d,b,[[t]for t in times],'SCALAR');rows={j:[]for j in [root]+joints}
  for t in times:
   world=globals_at(src,original,clip,t)
   rm=root_world(world);rows[root].append(([rm[3],rm[7],rm[11]],quaternion(rm)))
   for j in joints:
    m=local(world,j);rows[j].append(([m[3],m[7],m[11]],quaternion(m)))
  out={'name':clip.get('name','Animation'),'samplers':[],'channels':[]}
  for j in [root]+joints:
   for k,(path,kind)in enumerate([('translation','VEC3'),('rotation','VEC4')]):
    data=[row[k]for row in rows[j]]
    if k:
     for i in range(1,len(data)):
      if sum(a*c for a,c in zip(data[i-1],data[i]))<0:data[i]=[-a for a in data[i]]
    oa=append(d,b,data,kind);si=len(out['samplers']);out['samplers'].append({'input':ta,'output':oa,'interpolation':'LINEAR'});out['channels'].append({'sampler':si,'target':{'node':j,'path':path}})
  d['animations'].append(out)
 d.setdefault('extras',{})['NARISRepair']={'source_sha256':hashlib.sha256(pathlib.Path(source).read_bytes()).hexdigest(),'status':'provisional_rig_not_production_approved','method':'single_skin_hierarchy_rebake','hz':hz,'rigid_part_weights_retained':len(skins)>1,'root_motion_migrated_from_detached_mesh':detached_root is not None,'root_driver_node':root_driver}
 for mesh in d['meshes']:
  for prim in mesh['primitives']:
   for acc_index in prim['attributes'].values():d['bufferViews'][d['accessors'][acc_index]['bufferView']]['target']=34962
   if 'indices' in prim:d['bufferViews'][d['accessors'][prim['indices']]['bufferView']]['target']=34963
 for node in d['nodes']:
  if node.get('children')==[]:node.pop('children')
 d['buffers'][0]['byteLength']=len(b)
 js=json.dumps(d,separators=(',',':')).encode();js+=b' '*((-len(js))%4);b.extend(b'\0'*((-len(b))%4));raw=struct.pack('<4sII',b'glTF',2,28+len(js)+len(b))+struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(b),0x004e4942)+b
 pathlib.Path(destination).write_bytes(raw)
 return {'source':str(source),'output':str(destination),'skin_count_before':len(skins),'skin_count_after':1,'joints_after':len(joints)+1,'animation_count':len(d['animations']),'production_approved':False}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('source');p.add_argument('destination');p.add_argument('--hz',type=int,default=60);a=p.parse_args()
 if a.hz<=0:raise ValueError('hz must be positive')
 if pathlib.Path(a.source).resolve()==pathlib.Path(a.destination).resolve():raise ValueError('preserve original source')
 print(json.dumps(unify(a.source,a.destination,a.hz),indent=2))
