"""Submit the exact owner-requested sampling workflows to an installed ComfyUI."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.request
import uuid

ROOT = Path(__file__).resolve().parents[2]


def workflow_key(workflow):
    return hashlib.sha256(json.dumps(workflow, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def save_records(path, records):
    temporary = path.with_name(path.name + '.tmp')
    with temporary.open('w', encoding='utf-8') as handle:
        json.dump(records, handle, indent=2)
        handle.write('\n')
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def submit_batch(batch, server, output, send):
    """Resume accepted jobs; checkpoint intent before POST to avoid blind retries."""
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    lock = output.with_name(output.name + '.lock')
    try:
        descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise RuntimeError('Another runner or an interrupted run holds ' + str(lock)) from exc
    os.close(descriptor)
    try:
        records = json.loads(output.read_text(encoding='utf-8')) if output.exists() else []
        if not isinstance(records, list) or any(not isinstance(r, dict) or not isinstance(r.get('workflow'), dict) for r in records):
            raise ValueError('Invalid receipt journal; refusing to replace it')
        server = server.rstrip('/')
        pending = []
        for name, workflow in batch:
            key = workflow_key(workflow)
            # Legacy receipts omitted server; conservatively retain them as sent.
            matches = [r for r in records if workflow_key(r['workflow']) == key
                       and r.get('server', server).rstrip('/') == server]
            if matches:
                if any(not r.get('prompt_id') for r in matches):
                    raise RuntimeError('Unresolved submission for ' + name + '; inspect ComfyUI history and the journal before retrying')
                print(name + ': already submitted; skipped')
                continue
            pending.append((name, workflow, key))
        client = str(uuid.uuid4())
        for name, workflow, key in pending:
            record = {'name': name, 'status': 'submitting', 'server': server,
                'workflow_key': key, 'workflow': workflow, 'client_id': client}
            records.append(record)
            save_records(output, records)
            # A connection loss may occur after acceptance. Leave intent unresolved,
            # rather than automatically retrying a potentially accepted generation.
            result = send(server, '/prompt', {'prompt': workflow, 'client_id': client})
            if result.get('node_errors') or not result.get('prompt_id'):
                record['status'] = 'rejected'; record['response'] = result
                save_records(output, records)
                raise RuntimeError('Workflow rejected: ' + json.dumps(result))
            record.update(prompt_id=result['prompt_id'], status='queued')
            save_records(output, records)
            print(name + ': queued ' + result['prompt_id'])
        return records
    finally:
        lock.unlink()


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
        output=ROOT/'unreal/NARIS_W04/Saved/NARIS/Intake/comfy-requests.json'
        submit_batch(batch, args.server, output, request)
        print('Generation completion and output inspection are still required. See ComfyUI history.')
