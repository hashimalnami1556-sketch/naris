#!/usr/bin/env python3
import json, math, sys
from pathlib import Path

def die(msg): print("FAIL:",msg); raise SystemExit(1)
if len(sys.argv)!=2: die("usage: audit_char001_glb.py <file.glb|file.gltf>")
p=Path(sys.argv[1])
if not p.exists(): die("file missing")
raw=p.read_bytes()
if p.suffix.lower()==".glb":
 import struct
 if raw[:4]!=b"glTF": die("bad GLB magic")
 version,length=struct.unpack_from("<II",raw,4)
 if version!=2 or length!=len(raw): die("bad GLB header")
 off=12; doc=None
 while off<len(raw):
  n,t=struct.unpack_from("<II",raw,off); off+=8
  chunk=raw[off:off+n]; off+=n
  if t==0x4E4F534A: doc=json.loads(chunk.decode("utf-8").rstrip("\x00 \t\r\n"))
 if doc is None: die("JSON chunk missing")
else: doc=json.loads(raw.decode("utf-8"))
nodes=doc.get("nodes",[]); skins=doc.get("skins",[])
names=[n.get("name","") for n in nodes]
dups=sorted({n for n in names if n and names.count(n)>1})
if dups: die("duplicate node names: "+",".join(dups[:20]))
if not skins: die("no skin")
joints=set()
for s in skins: joints.update(s.get("joints",[]))
if not joints: die("skin has zero joints")
control=[names[i] for i in joints if i<len(names) and any(k in names[i].lower() for k in ("ctrl","control","ik_target","pole"))]
if control: die("control/helper-like nodes exported as skin joints: "+",".join(control[:20]))
roots=[]
parents={}
for i,n in enumerate(nodes):
 for c in n.get("children",[]): parents[c]=i
for j in joints:
 if j not in parents or parents[j] not in joints: roots.append(j)
if len(roots)!=1: die(f"skin root count={len(roots)}")
for i,n in enumerate(nodes):
 for key in ("translation","rotation","scale","matrix"):
  vals=n.get(key,[])
  if any(not math.isfinite(float(v)) for v in vals): die(f"nonfinite transform node {i}")
print(json.dumps({"status":"STRUCTURAL_GLTF_PASS","nodes":len(nodes),"skin_joints":len(joints),"skin_root":names[roots[0]] if roots[0]<len(names) else roots[0],"duplicate_names":0,"control_skin_joints":0},indent=2))
