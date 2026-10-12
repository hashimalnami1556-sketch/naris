"""Submit the exact owner-requested sampling workflows to an installed ComfyUI."""
import argparse
import json
from pathlib import Path
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[2]


def request(server, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(server.rstrip('/') + path, data=data,
        headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)


def workflows(checkpoint, upscaler, info):
    available = lambda node, field: info[node]['input']['required'][field][0]
    for node, field, value in [('CheckpointLoaderSimple','ckpt_name',checkpoint),
        ('UpscaleModelLoader','model_name',upscaler),('KSampler','sampler_name','dpmpp_2m'),
        ('KSampler','scheduler','karras')]:
        if value not in available(node,field):
            raise ValueError(f'{node}.{field} does not offer {value!r}')
    batch = []
    for path in sorted((ROOT/'assets/intake/w04-20261011/generation').glob('*.api.json')):
        workflow=json.loads(path.read_text())
        workflow['1']['inputs']['ckpt_name']=checkpoint
        workflow['8']['inputs']['model_name']=upscaler
        for node in workflow.values():
            if node['class_type'] not in info:
                raise ValueError('Missing ComfyUI node ' + node['class_type'])
        batch.append((path.stem,workflow))
    if not batch: raise ValueError('No generation workflows found')
    return batch


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--server',default='http://127.0.0.1:8188')
    parser.add_argument('--checkpoint',required=True)
    parser.add_argument('--upscaler',required=True,help='Installed 2x model; factor must be verified separately')
    parser.add_argument('--validate-only',action='store_true')
    args=parser.parse_args()
    info=request(args.server,'/object_info')
    batch=workflows(args.checkpoint,args.upscaler,info)
    if args.validate_only:
        print(f'{len(batch)} workflows compatible with installed node/model names; no jobs submitted')
    else:
        records=[];client=str(uuid.uuid4())
        output=ROOT/'unreal/NARIS_W04/Saved/NARIS/Intake/comfy-requests.json'
        output.parent.mkdir(parents=True,exist_ok=True)
        # Checkpoint each accepted request; never describe queue acceptance as generated output.
        for name, workflow in batch:
            result=request(args.server,'/prompt',{'prompt':workflow,'client_id':client})
            if result.get('node_errors') or not result.get('prompt_id'):
                raise RuntimeError('Workflow rejected: ' + json.dumps(result))
            records.append({'name':name,'prompt_id':result['prompt_id'],'status':'queued',
                'checkpoint':args.checkpoint,'upscaler':args.upscaler,'workflow':workflow})
            output.write_text(json.dumps(records,indent=2)+'\n')
            print(name + ': queued ' + result['prompt_id'])
        print('Generation completion and output inspection are still required. See ComfyUI history.')
