"""Run inside Unreal Editor. Set NARIS_EXPANSION_EXCHANGE to exported pack root."""
import json
import os
from pathlib import Path
import sys
import unreal

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE))
import naris_import_blender_exchange as bridge

def main():
    value=os.environ.get('NARIS_EXPANSION_EXCHANGE','').strip()
    if not value:raise RuntimeError('Set NARIS_EXPANSION_EXCHANGE to the Blender export root')
    base=Path(value).resolve()
    pack=json.loads((ROOT/'assets/w04-expansion/manifest.json').read_text())
    pending=[]
    for item in pack['assets']:
        manifest=base/item['id']/(item['id']+'_blender_manifest.json')
        if not manifest.is_file():raise FileNotFoundError(manifest)
        data=json.loads(manifest.read_text())
        if data.get('status')!='pass' or data.get('asset_id')!=item['id']:
            raise ValueError('Invalid exchange manifest: '+str(manifest))
        if not manifest.with_name(item['id']+'.fbx').is_file():raise FileNotFoundError('Missing FBX: '+item['id'])
        dest='/Game/NARIS/Imported/W04/'+item['id']
        if unreal.EditorAssetLibrary.does_directory_exist(dest):
            raise RuntimeError('Destination already exists; refusing batch overwrite: '+dest)
        pending.append(manifest)
    keys=('NARIS_EXCHANGE_MANIFEST','NARIS_MASTER_REGISTRY')
    previous={k:os.environ.get(k) for k in keys}
    completed=[]
    report=base/'unreal-expansion-result.json'
    try:
        os.environ[keys[1]]=str(ROOT/'data/MASTER_ASSET_REGISTRY.json')
        for manifest in pending:
            os.environ[keys[0]]=str(manifest);bridge.main()
            completed.append(manifest.parent.name)
            report.write_text(json.dumps({'status':'in_progress','imported':completed},indent=2))
        report.write_text(json.dumps({'status':'pass','imported':completed},indent=2))
    except Exception as error:
        report.write_text(json.dumps({'status':'fail','imported':completed,'error':str(error)},indent=2))
        raise
    finally:
        for key,value in previous.items():
            if value is None:os.environ.pop(key,None)
            else:os.environ[key]=value

if __name__=='__main__':main()
