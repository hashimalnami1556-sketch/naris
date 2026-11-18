"""Render original source Idle skinned vs virtual hand-rigid sword at t=.75.
CPU-only orthographic visualization; NOT a screenshot of Unreal.
"""
import argparse, io, json
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from char023_weapon_review import read_glb,accessor_array,audit_source,sha
from char023_pose_audit import animation_rotations,joint_matrices,skin_subset,rigid_from_hand

def basecolor(doc,blob,pr):
    texid=doc['materials'][pr['material']]['pbrMetallicRoughness']['baseColorTexture']['index']
    img=doc['images'][doc['textures'][texid]['source']]
    v=doc['bufferViews'][img['bufferView']];off=v.get('byteOffset',0)
    return np.asarray(Image.open(io.BytesIO(blob[off:off+v['byteLength']])).convert('RGB'))

def render(p,faces,colors,axis,w=570,h=700):
    if axis=='front':x=p[:,0];y=p[:,1];depth=p[:,2]
    elif axis=='right':x=-p[:,2];y=p[:,1];depth=p[:,0]
    else:raise ValueError('Unknown axis')
    pts=np.c_[w/2+x*h*.87,h*.96-y*h*.87]
    im=Image.new('RGB',(w,h),'#252b35');draw=ImageDraw.Draw(im)
    for i in np.argsort(depth[faces].mean(axis=1)):
        draw.polygon([tuple(np.int32(v)) for v in pts[faces[i]]],fill=tuple(int(c) for c in colors[i]))
    return im

def create(source:Path,output:Path,report:Path):
    if output.exists() or report.exists():
        raise ValueError('Refusing to overwrite existing evidence')
    doc,blob=read_glb(source)
    pr,faces,labels,masks=audit_source(doc,blob,sha(source.read_bytes()))
    p=accessor_array(doc,blob,pr['attributes']['POSITION']).astype(float)
    uv=accessor_array(doc,blob,pr['attributes']['TEXCOORD_0'])[faces].mean(axis=1)%1
    tex=basecolor(doc,blob,pr)
    colors=tex[(uv[:,1]*(tex.shape[0]-1)).astype(int),(uv[:,0]*(tex.shape[1]-1)).astype(int)].copy()
    t=.75
    mats,bind,posed,err=joint_matrices(doc,blob,animation_rotations(doc,blob,t))
    before=skin_subset(doc,blob,np.arange(len(p)),mats)
    after=before.copy()
    selected=np.unique(faces[masks['blade']|masks['guard']])
    hand=next(i for i in doc['skins'][0]['joints'] if doc['nodes'][i].get('name')=='hand_L')
    after[selected]=rigid_from_hand(p[selected],bind[hand],posed[hand])
    delta=np.linalg.norm(before[selected]-after[selected],axis=1)
    per_vertex=np.zeros(len(p));per_vertex[selected]=delta
    by_face=np.zeros(len(faces))
    by_face[masks['guard']|masks['blade']]=per_vertex[faces[masks['guard']|masks['blade']]].mean(axis=1)
    heat=np.clip(by_face/max(float(by_face.max()),1e-12),0,1)
    heat_colors=(np.array([36,54,66])[None,:]*(1-heat[:,None])+np.array([245,100,44])[None,:]*heat[:,None]).astype(np.uint8)
    heat_colors[~(masks['guard']|masks['blade'])]=[65,71,79]
    width,height,gap,row_gap,header,foot=570,700,20,65,105,70
    sheet=Image.new('RGB',(width*3+gap*4,2*(height+row_gap)+header+foot),'#161b22')
    d=ImageDraw.Draw(sheet)
    d.text((gap,20),'CALL OF NARIS | CHAR-023 | ORIGINAL IDLE FRAME 0.75s',fill='#f7f7f9')
    d.text((gap,50),'Original weighted sword vs virtual hand_L rigid mount; CPU only, NOT Unreal.',fill='#adb8c6')
    for row,axis in enumerate(('front','right')):
        columns=[(render(before,faces,colors,axis,width,height),'BEFORE | SKIN'),
                 (render(after,faces,colors,axis,width,height),'AFTER | RIGID'),
                 (render(after,faces,heat_colors,axis,width,height),'SWORD POSE DELTA HEAT')]
        for col,(im,label) in enumerate(columns):
            x=gap+col*(width+gap);y=header+row*(height+row_gap)
            sheet.paste(im,(x,y+25));d.text((x,y+4),axis.upper()+' | '+label,fill='#f2f6fc')
    d.text((gap,sheet.height-foot+12),f'Weapon vertex position delta: mean {float(delta.mean()):.5f}, max {float(delta.max()):.5f} glTF source units.',fill='#b6c2d2')
    d.text((gap,sheet.height-foot+36),'Heat shows DIFFERENCE in predictions, NOT combat validation, clipping or Unreal evidence.',fill='#b6c2d2')
    output.parent.mkdir(parents=True,exist_ok=True);report.parent.mkdir(parents=True,exist_ok=True)
    sheet.save(output)
    summary={'source_animation':'A_Character1_Idle','time_seconds':t,
             'weapon_vertex_count':len(selected),
             'mean_displacement_source_units':float(delta.mean()),
             'max_displacement_source_units':float(delta.max()),
             'max_bind_identity_error':err,
             'unreal_render':False,'source_geometry_preserved':True}
    report.write_text(json.dumps(summary,indent=2)+'\n')
    return summary

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--source',type=Path,required=True)
    a.add_argument('--output',type=Path,required=True)
    a.add_argument('--report',type=Path,required=True)
    args=a.parse_args()
    print(json.dumps(create(args.source,args.output,args.report),indent=2))

if __name__=='__main__':main()
