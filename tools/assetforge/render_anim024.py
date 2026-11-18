"""Render actual CPU skin poses from the dev-only GLB, not Unreal screenshots."""
import argparse, io, json, math, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from anim024_dev_motion import sample_pose, world_transforms
from char023_weapon_review import read_glb, accessor_array

def pose_vertices(doc,blob,clip_name,t):
    pose=sample_pose(doc,blob,clip_name,t)
    world=world_transforms(doc,pose)
    original=doc['meshes'][0]['primitives'][0]
    attrs=original['attributes'];skin=doc['skins'][0]
    p=accessor_array(doc,blob,attrs['POSITION']).astype(float)
    j=accessor_array(doc,blob,attrs['JOINTS_0']).astype(int)
    w=accessor_array(doc,blob,attrs['WEIGHTS_0']).astype(float)
    inv=accessor_array(doc,blob,skin['inverseBindMatrices']).astype(float)
    mats=np.stack([world[int(bone)]@inv[k].reshape(4,4).T for k,bone in enumerate(skin['joints'])])
    ph=np.c_[p,np.ones(len(p))]
    out=np.zeros((len(p),4))
    for k in range(4):
        out+=np.einsum('nij,nj->ni',mats[j[:,k]],ph)*w[:,k,None]
    if not np.isfinite(out).all():raise ValueError('Non-finite deformed vertex')
    return out[:,:3]

def texture_colors(doc,blob):
    prim=doc['meshes'][0]['primitives'][0];attrs=prim['attributes']
    tri=accessor_array(doc,blob,prim['indices']).astype(int).reshape(-1,3)
    uv=accessor_array(doc,blob,attrs['TEXCOORD_0']).astype(float)
    base=doc['materials'][prim['material']]['pbrMetallicRoughness']['baseColorTexture']['index']
    img=doc['images'][doc['textures'][base]['source']];view=doc['bufferViews'][img['bufferView']]
    start=view.get('byteOffset',0);source=blob[start:start+view['byteLength']]
    tex=np.asarray(Image.open(io.BytesIO(source)).convert('RGB'))
    coord=np.mod(uv[tri].mean(axis=1),1)
    col=tex[(coord[:,1]*(tex.shape[0]-1)).astype(int),(coord[:,0]*(tex.shape[1]-1)).astype(int)]
    return tri,col

def frame(p,tri,colors, width=470, height=530, view='front', downsample=1):
    if view=='front':x=p[:,0];y=p[:,1];d=p[:,2]
    elif view=='right':x=-p[:,2];y=p[:,1];d=p[:,0]
    else:raise ValueError(view)
    screen=np.c_[width*.5+x*height*.83,height*.96-y*height*.83]
    ids=np.arange(0,len(tri),downsample)
    depth=d[tri[ids]].mean(axis=1)
    ids=ids[np.argsort(depth)]
    image=Image.new('RGB',(width,height),(22,27,36))
    draw=ImageDraw.Draw(image)
    for idx in ids:
        poly=[(round(screen[v,0]),round(screen[v,1])) for v in tri[idx]]
        draw.polygon(poly,fill=tuple(int(c) for c in colors[idx]))
    return image

def label_frame(img,label):
    result=Image.new('RGB',(img.width,img.height+42),'#101820')
    d=ImageDraw.Draw(result);d.text((12,10),label,fill='#eff5f7')
    result.paste(img,(0,42))
    return result

def main():
    a=argparse.ArgumentParser()
    a.add_argument('--source',type=Path,required=True)
    a.add_argument('--outdir',type=Path,required=True)
    args=a.parse_args();d,b=read_glb(args.source)
    args.outdir.mkdir(parents=True,exist_ok=True)
    tri,col=texture_colors(d,b)
    shots=[];labels=[]
    name_times=[('Walk',.25),('Run',.22),('LightAttack',.5),('Dodge',.31),('Block',.43),('Jump',.48),('Death',1.07)]
    original=pose_vertices(d,b,'A_Character1_Idle',0.)
    for name,t in name_times:
        clip=next(a['name'] for a in d['animations'] if a['name'].startswith('DEV_ONLY_'+name+'_'))
        q=pose_vertices(d,b,clip,t)
        dev=frame(q,tri,col,440,510,downsample=1)
        base=frame(original,tri,col,440,510,downsample=1)
        shots.append((base,dev,name,t))
    # Seven rows, same camera/real source geometry
    gap=14;W=2*440+3*gap;H=7*(510+62)+8*gap+90
    img=Image.new('RGB',(W,H),'#131b24');draw=ImageDraw.Draw(img)
    draw.text((gap,17),'NARIS ANIM-024 | ACTUAL GLB SKIN PREVIEW | NOT UNREAL',fill='#f2f4f5')
    draw.text((gap,46),'Left: source Idle. Right: deterministic DEV-ONLY clip. Same camera & source mesh.',fill='#acb9c8')
    for i,(baseline,dev,name,t) in enumerate(shots):
        y=90+gap+i*(510+62+gap)
        img.paste(label_frame(baseline,'ORIGINAL IDLE | t=0'),(gap,y))
        img.paste(label_frame(dev,f'DEV {name} | t={t:.2f} sec'),(440+2*gap,y))
    path=args.outdir/'anim024_original_vs_dev_storyboard.png';img.save(path)
    # Four-second software preview: two seconds Walk, two seconds Run.
    tmp=args.outdir/'frames';tmp.mkdir(exist_ok=True)
    clip_data=[('Walk',1.),('Run',.8)]
    fps=12;N=48
    for i in range(N):
        seg=0 if i<N//2 else 1
        kind,dur=clip_data[seg];j=i if seg==0 else i-N//2
        t=((j/fps)%dur)
        clip=next(a['name'] for a in d['animations'] if a['name'].startswith('DEV_ONLY_'+kind+'_'))
        p=pose_vertices(d,b,clip,t)
        v=frame(p,tri,col,520,650,downsample=2)
        canvas=Image.new('RGB',(520,706),'#101820');canvas.paste(v,(0,56))
        ImageDraw.Draw(canvas).text((13,18),f'ANIM-024 | DEV {kind} | {i/fps:.2f}s | NOT GAMEPLAY',fill='#f5f5f5')
        canvas.save(tmp/f'{i:03d}.png')
    video=args.outdir/'anim024_walk_run_software_preview.mp4'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate',str(fps),'-i',str(tmp/'%03d.png'),
                    '-c:v','libx264','-pix_fmt','yuv420p','-crf','22',str(video)],check=True)
    print(json.dumps({'storyboard':str(path),'motion_preview':str(video),'frames':N,
                      'frame_rate':fps,'source':'original GLB, CPU skinning, software render',
                      'is_unreal_screenshot':False},indent=2))

if __name__=='__main__':main()
