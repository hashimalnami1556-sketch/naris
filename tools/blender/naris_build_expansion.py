"""Build one source mesh in a fresh background Blender process, then use canonical exporter."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import naris_export

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--asset-id',required=True)
    parser.add_argument('--out',required=True)
    args=parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    manifest=json.loads((ROOT/'assets/w04-expansion/manifest.json').read_text())
    matches=[a for a in manifest['assets'] if a['id']==args.asset_id]
    if len(matches)!=1:raise ValueError('Unknown or duplicate source ID')
    item=matches[0]; source=(ROOT/item['mesh']).resolve()
    if not source.is_relative_to(ROOT/'assets/w04-expansion'):raise ValueError('Source outside pack')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Source checksum mismatch')
    # Dedicated CLI only: never clear an interactive user's scene.
    if not bpy.app.background:raise RuntimeError('Run in a fresh background Blender process')
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    data=json.loads(source.read_text());mesh=bpy.data.meshes.new(args.asset_id)
    mesh.from_pydata(data['vertices'],[],data['faces']);mesh.update()
    obj=bpy.data.objects.new(args.asset_id,mesh);bpy.context.collection.objects.link(obj)
    obj.select_set(True);bpy.context.view_layer.objects.active=obj
    bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1.0
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(island_margin=.03);bpy.ops.object.mode_set(mode='OBJECT')
    obj['naris_asset_id']=args.asset_id;obj['production_status']='blockout'
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/(args.asset_id+'.blend')))
    sys.argv=['naris_export','--','--out',str(out),'--asset-id',args.asset_id,'--registry',str(ROOT/'data/MASTER_ASSET_REGISTRY.json')]
    return naris_export.main()

if __name__=='__main__':raise SystemExit(main())
