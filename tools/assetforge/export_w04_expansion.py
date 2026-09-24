"""Host-side sequential launcher; failures stop the batch and preserve prior outputs."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--blender',required=True,help='Path to Blender executable')
    p.add_argument('--out',required=True)
    p.add_argument('--asset-id',help='Export one ID; omission exports the whole source pack')
    args=p.parse_args()
    assets=json.loads((ROOT/'assets/w04-expansion/manifest.json').read_text())['assets']
    if args.asset_id:
        assets=[a for a in assets if a['id']==args.asset_id]
        if not assets:p.error('Asset ID is not in the expansion pack')
    out=Path(args.out).resolve();out.mkdir(parents=True,exist_ok=True)
    for a in assets:
        target=out/a['id']
        if target.exists():raise FileExistsError(f'Refusing to overwrite export directory: {target}')
        subprocess.run([args.blender,'--background','--factory-startup','--python-exit-code','1','--python',str(ROOT/'tools/blender/naris_build_expansion.py'),'--','--asset-id',a['id'],'--out',str(target)],check=True)
    print(f'Exported {len(assets)} Blender exchange packages')

if __name__=='__main__':main()
