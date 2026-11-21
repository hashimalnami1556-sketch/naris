"""NARIS ANIM-024: additive, preview-only original-rig motion curves.

Seven procedural TECHNICAL TEST animations for the pinned CHAR-023 body-only
review GLB. They do not constitute authored, production-ready motion, IK,
root motion, montage notifies, or Unreal integration. Never overwrite input.
"""
import argparse, copy, hashlib, json, math
from pathlib import Path
import numpy as np
from char023_weapon_review import read_glb, write_glb, accessor_array

PINNED_BODY_SHA = '2fc95a46ba69f23c4365390bea277f185bc83e187286140d56d22aa080e0780d'
REQUIRED = ('idle','walk','run','attack','dodge','block','death')
KINDS = {
    'Walk': {'duration':1.0,'loop':True},
    'Run': {'duration':.8,'loop':True},
    'LightAttack': {'duration':.8,'loop':False},
    'Dodge': {'duration':.7,'loop':False},
    'Block': {'duration':.8,'loop':False},
    'Jump': {'duration':.9,'loop':False},
    'Death': {'duration':1.2,'loop':False},
}
BONES = ('pelvis','chest','neck','upper_arm_L','lower_arm_L',
         'upper_arm_R','lower_arm_R','thigh_L','calf_L','foot_L',
         'thigh_R','calf_R','foot_R')
FPS = 30

def _qaxis(deg,axis):
    rad=math.radians(float(deg))*.5
    s=math.sin(rad)
    a=np.zeros(4,dtype=float);a[axis]=s;a[3]=math.cos(rad)
    return a

def quaternion_x(deg):return _qaxis(deg,0)
def _quaternion_y(deg):return _qaxis(deg,1)
def _quaternion_z(deg):return _qaxis(deg,2)

def _product(a,b):
    x,y,z,w=a;x2,y2,z2,w2=b
    return np.array([w*x2+x*w2+y*z2-z*y2,w*y2-x*z2+y*w2+z*x2,
                     w*z2+x*y2-y*x2+z*w2,w*w2-x*x2-y*y2-z*z2])

def _euler(x=0.,y=0.,z=0.):
    q=_product(_product(_quaternion_y(y),quaternion_x(x)),_quaternion_z(z))
    return (q/np.linalg.norm(q)).tolist()

def _smooth(u):
    u=np.clip(u,0,1)
    return float(u*u*(3-2*u))

def _pulse(u,rise,hold,fall):
    if u<rise:return _smooth(u/rise)
    if u<hold:return 1.
    if u<fall:return 1.-_smooth((u-hold)/(fall-hold))
    return 0.

def motion_profile(kind,u):
    """Fractions in [0,1]. In-place preview only. glTF Y-up bone rotations."""
    if kind not in KINDS or not 0<=u<=1:
        raise ValueError('Unknown action or time fraction')
    q={name:[0.,0.,0.,1.] for name in BONES}
    pelvis_y=0.
    if kind in ('Walk','Run'):
        p=2*np.pi*u;run=kind=='Run'
        swing=np.sin(p);swing2=np.cos(p)
        stride=57 if run else 35
        knee=65 if run else 38
        arm=39 if run else 25
        q['thigh_L']=_euler(x=stride*swing)
        q['thigh_R']=_euler(x=-stride*swing)
        q['calf_L']=_euler(x=-knee*max(0,swing2))
        q['calf_R']=_euler(x=-knee*max(0,-swing2))
        q['foot_L']=_euler(x=-12*swing)
        q['foot_R']=_euler(x=12*swing)
        q['upper_arm_L']=_euler(x=-arm*swing,z=5)
        q['upper_arm_R']=_euler(x=arm*swing,z=-5)
        q['lower_arm_L']=_euler(x=-8 if run else -4)
        q['lower_arm_R']=_euler(x=-8 if run else -4)
        q['chest']=_euler(y=4*swing,z=2.8*swing)
        pelvis_y=(.026 if run else .014)*(1.-np.cos(2*p))*.5
    elif kind=='LightAttack':
        wind=_pulse(u,.22,.30,.43)
        strike=_pulse(u,.37,.49,.72)
        q['chest']=_euler(x=8*strike,y=20*(strike-wind))
        q['upper_arm_L']=_euler(x=-(22*wind+78*strike),z=25*(wind-strike))
        q['lower_arm_L']=_euler(x=-35*wind+27*strike)
        q['upper_arm_R']=_euler(x=8*wind-15*strike,z=-8*wind)
        q['thigh_L']=_euler(x=14*strike)
        q['thigh_R']=_euler(x=-10*strike)
        pelvis_y=-.024*strike
    elif kind=='Dodge':
        crouch=_pulse(u,.15,.38,.85)
        q['chest']=_euler(x=30*crouch,y=7*np.sin(np.pi*u))
        q['thigh_L']=_euler(x=38*crouch)
        q['thigh_R']=_euler(x=38*crouch)
        q['calf_L']=_euler(x=-53*crouch)
        q['calf_R']=_euler(x=-53*crouch)
        q['upper_arm_L']=_euler(x=23*crouch)
        q['upper_arm_R']=_euler(x=23*crouch)
        pelvis_y=-.055*crouch
    elif kind=='Block':
        hold=_pulse(u,.19,.68,.98)
        q['chest']=_euler(x=-10*hold)
        q['upper_arm_L']=_euler(x=-55*hold,z=-18*hold)
        q['upper_arm_R']=_euler(x=-42*hold,z=15*hold)
        q['lower_arm_L']=_euler(x=-42*hold)
        q['lower_arm_R']=_euler(x=-35*hold)
    elif kind=='Jump':
        crouch=_pulse(u,.12,.21,.32)
        rise=_pulse(u,.36,.48,.67)
        land=_pulse(u,.73,.83,.95)
        q['thigh_L']=_euler(x=18*crouch-12*rise+15*land)
        q['thigh_R']=_euler(x=18*crouch-12*rise+15*land)
        q['calf_L']=_euler(x=-32*crouch+10*rise-27*land)
        q['calf_R']=_euler(x=-32*crouch+10*rise-27*land)
        q['upper_arm_L']=_euler(x=-25*rise)
        q['upper_arm_R']=_euler(x=-25*rise)
        pelvis_y=-.025*crouch+.065*rise-.020*land
    elif kind=='Death':
        fade=_smooth(u/.86)
        q['chest']=_euler(x=62*fade,z=27*fade)
        q['pelvis']=_euler(x=20*fade,z=12*fade)
        q['neck']=_euler(x=-17*fade)
        q['upper_arm_L']=_euler(x=45*fade,z=-25*fade)
        q['upper_arm_R']=_euler(x=37*fade,z=22*fade)
        q['thigh_L']=_euler(x=27*fade)
        q['thigh_R']=_euler(x=21*fade)
        q['calf_L']=_euler(x=-38*fade)
        q['calf_R']=_euler(x=-30*fade)
        pelvis_y=-.115*fade
    if kind=='Death' and u==1:
        assert pelvis_y<-.1
    q['pelvis_t']=float(pelvis_y)
    return q

def _append_float_accessor(doc,bin_data,arr):
    data=np.ascontiguousarray(arr,dtype='<f4')
    if data.ndim==1:typ='SCALAR';count=len(data)
    elif data.ndim==2 and data.shape[1] in (3,4):typ=f'VEC{data.shape[1]}';count=len(data)
    else:raise ValueError('Expected float time/vec3/vec4')
    if not len(data) or not np.isfinite(data).all():raise ValueError('Bad animation float data')
    bin_data.extend(b'\0'*(-len(bin_data)%4));off=len(bin_data)
    bin_data.extend(data.tobytes())
    v=len(doc['bufferViews'])
    doc['bufferViews'].append({'buffer':0,'byteOffset':off,'byteLength':data.nbytes})
    a={'bufferView':v,'componentType':5126,'count':count,'type':typ}
    if typ=='SCALAR':
        a['min']=[float(np.min(data))];a['max']=[float(np.max(data))]
    doc['accessors'].append(a)
    return len(doc['accessors'])-1

def build_preview(doc,blob,source_sha):
    if source_sha!=PINNED_BODY_SHA:raise ValueError('Source digest mismatch; refuse writing')
    if len(doc.get('animations',[]))!=1 or doc['animations'][0].get('name')!='A_Character1_Idle':
        raise ValueError('Original Idle not as audited')
    if len(doc.get('skins',[]))!=1 or len(doc['skins'][0]['joints'])!=18:
        raise ValueError('Production target mismatch')
    bone_ids={n['name']:i for i,n in enumerate(doc['nodes']) if 'name' in n}
    if not set(BONES).issubset(bone_ids):raise ValueError('Missing source bone(s)')
    out=copy.deepcopy(doc);bin_data=bytearray(blob)
    clip_report={}
    base_pelvis=np.asarray(doc['nodes'][bone_ids['pelvis']]['translation'],dtype=float)
    for name,setting in KINDS.items():
        times=np.linspace(0,setting['duration'],int(round(setting['duration']*FPS))+1,dtype='<f4')
        times[-1]=setting['duration']
        norm=times/setting['duration']
        profiles=[motion_profile(name,float(u)) for u in norm]
        anim={'name':f'DEV_ONLY_{name}'+('_InPlace' if setting['loop'] else '_Preview'),
              'samplers':[],'channels':[],
              'extras':{'naris_dev_only':True,'production_approved':False,
                        'root_motion':'NONE_PREVIEW_IN_PLACE','loop':setting['loop'],
                        'animation_source':'deterministic procedural test, NOT mocap or authored production'}}
        timeline=_append_float_accessor(out,bin_data,times)
        for bone in BONES:
            values=np.asarray([prof[bone] for prof in profiles],dtype='<f4')
            norms=np.linalg.norm(values,axis=1)
            if max(abs(norms-1))>1e-6:raise AssertionError('Non-unit quaternion')
            if np.allclose(values,[[0,0,0,1]],atol=1e-7):continue
            a=_append_float_accessor(out,bin_data,values)
            s=len(anim['samplers']);anim['samplers'].append({'input':timeline,'output':a,'interpolation':'LINEAR'})
            anim['channels'].append({'sampler':s,'target':{'node':bone_ids[bone],'path':'rotation'}})
        trans=np.array([base_pelvis+np.array([0.,p['pelvis_t'],0.]) for p in profiles],dtype='<f4')
        if np.ptp(trans[:,1])>1e-6:
            a=_append_float_accessor(out,bin_data,trans)
            s=len(anim['samplers']);anim['samplers'].append({'input':timeline,'output':a,'interpolation':'LINEAR'})
            anim['channels'].append({'sampler':s,'target':{'node':bone_ids['pelvis'],'path':'translation'}})
        if not anim['channels']:raise AssertionError('No channels')
        out['animations'].append(anim)
        clip_report[name]={'name':anim['name'],'duration_s':float(times[-1]),'frames':len(times),
                           'channels':len(anim['channels']),'loop':setting['loop']}
    out['buffers'][0]['byteLength']=len(bin_data)
    if out['animations'][0]!=doc['animations'][0]:raise AssertionError('Original Idle changed')
    if blob!=bytes(bin_data[:len(blob)]):raise AssertionError('Original bin changed')
    if out['skins']!=doc['skins'] or out['meshes']!=doc['meshes'] or out['nodes']!=doc['nodes']:
        raise AssertionError('Original mesh/rig changed')
    report={'id':'ANIM-024-DEV-CURVES','status':'DEV_ONLY_NO_PRODUCTION_APPROVAL',
      'source_sha256':source_sha,'original_animation_preserved':True,
      'original_geometry_binary_prefix_preserved':True,'original_rig_preserved':True,
      'clips':clip_report,'production_approved':False,
      'root_motion':'NOT_AUTHORED','foot_ik':'NOT_AUTHORED','combat_notifies':'NOT_AUTHORED',
      'engine_import':'NOT_RUN','PIE':'NOT_RUN','network':'NOT_RUN','BuildCookRun':'NOT_RUN',
      'limitations':['In-place procedural test cycles may exhibit foot slide/clipping',
        'Does not replace licensed or authored locomotion/combat',
        'No root-motion, attack notifies, hit windows, IK, retarget assets, or Unreal animation blueprint',
        'Source was already the CHAR-023 swordless review body; weapon attach untested'],
      'rollback':'Discard new review GLB; preserve source GLB and original animation.'}
    return out,bytes(bin_data),report

def sample_pose(doc,blob,clip_name,t):
    anim=next((a for a in doc['animations'] if a['name']==clip_name),None)
    if anim is None:raise ValueError('Unknown animation')
    channels={}
    for ch in anim['channels']:
        samp=anim['samplers'][ch['sampler']]
        times=accessor_array(doc,blob,samp['input']).reshape(-1).astype(float)
        values=accessor_array(doc,blob,samp['output']).astype(float)
        if t<times[0]-1e-7 or t>times[-1]+1e-7:raise ValueError('Time outside clip')
        if t<=times[0]:v=values[0]
        elif t>=times[-1]:v=values[-1]
        else:
            i=int(np.searchsorted(times,t,side='right')-1)
            f=(t-times[i])/(times[i+1]-times[i]);v=values[i]*(1-f)+values[i+1]*f
            if ch['target']['path']=='rotation':v=v/np.linalg.norm(v)
        channels[(ch['target']['node'],ch['target']['path'])]=v
    return channels

def _rot(q):
    x,y,z,w=np.asarray(q,dtype=float)/np.linalg.norm(q)
    return np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],
     [2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],
     [2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])

def world_transforms(doc,channel_pose):
    nodes=doc['nodes'];parent={}
    for i,n in enumerate(nodes):
        for c in n.get('children',[]):
            if c in parent:raise ValueError('Non-tree hierarchy')
            parent[c]=i
    cache={}
    def world(i,stack=()):
        if i in stack:raise ValueError('Bone cycle')
        if i not in cache:
            node=nodes[i];rot=channel_pose.get((i,'rotation'),node.get('rotation',[0,0,0,1]))
            trans=np.asarray(channel_pose.get((i,'translation'),node.get('translation',[0,0,0])),dtype=float)
            m=np.eye(4);m[:3,:3]=_rot(rot);m[:3,3]=trans
            cache[i]=world(parent[i],stack+(i,))@m if i in parent else m
        return cache[i]
    return {i:world(i) for i in range(len(nodes))}

def evaluate_motion(doc,blob):
    names={n['name']:i for i,n in enumerate(doc['nodes']) if 'name' in n}
    values={}
    for anim in doc['animations'][1:]:
        name=anim['name']
        times=accessor_array(doc,blob,anim['samplers'][0]['input']).ravel().astype(float)
        positions=[]
        for t in times:
            wm=world_transforms(doc,sample_pose(doc,blob,name,float(t)))
            positions.append(np.array([wm[names['foot_L']][:3,3],wm[names['foot_R']][:3,3]]))
        arr=np.stack(positions)
        root_count=sum(1 for c in anim['channels'] if c['target']['node']==names['root'] and c['target']['path']=='translation')
        values[name]={'time_range_s':[float(times[0]),float(times[-1])],
            'foot_L_range_source_units':float(np.ptp(arr[:,0,:],axis=0).max()),
            'foot_R_range_source_units':float(np.ptp(arr[:,1,:],axis=0).max()),
            'root_translation_channel_count':root_count,
            'foot_ik_test':'NOT_PERFORMED','ground_contact':'NOT_VALIDATED'}
    return values

def audit_preview(doc):
    production=[];dev=[]
    for a in doc.get('animations',[]):
        if a.get('extras',{}).get('naris_dev_only') or not a.get('extras',{}).get('production_approved',True):
            dev.append(a['name']);continue
        lower=a['name'].casefold()
        for name in REQUIRED:
            if name in lower and name not in production:production.append(name)
    return {'production_names_present':production,
            'excluded_dev_clips':dev,
            'missing_required':[n for n in REQUIRED if n not in production],
            'ready_for_release':False}

def main():
    p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--report',type=Path,required=True)
    args=p.parse_args()
    if args.source.resolve()==args.output.resolve() or args.output.exists() or args.report.exists():
        raise SystemExit('Will not overwrite existing assets or evidence')
    src=args.source.read_bytes();d,b=read_glb(args.source)
    new,bin_data,report=build_preview(d,b,hashlib.sha256(src).hexdigest())
    args.output.parent.mkdir(parents=True,exist_ok=True);args.report.parent.mkdir(parents=True,exist_ok=True)
    write_glb(args.output,new,bin_data)
    rd,rb=read_glb(args.output)
    if rd['animations'][:len(d['animations'])]!=d['animations']:
        raise AssertionError('Original animation was not preserved after serialize')
    if rb[:len(b)]!=b:raise AssertionError('Original binary altered')
    report['output_sha256']=hashlib.sha256(args.output.read_bytes()).hexdigest()
    report['source_foot_motion_metrics']=evaluate_motion(rd,rb)
    report['coverage']=audit_preview(rd)
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'output':str(args.output),'sha256':report['output_sha256'],
         'clip_count':len(rd['animations']),'production_ready':False,'coverage':report['coverage']},indent=2))
if __name__=='__main__':main()
