"""Byte-level intake regressions: corrupt geometry must not reach the editor."""
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('audit_glb', ROOT / 'tools/intake/audit_glb.py')
module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)


def glb(indices=(0, 1, 2), vertex_count=3):
    binary = struct.pack('<9f3H', 0,0,0, 1,0,0, 0,1,0, *indices)
    doc = {'asset':{'version':'2.0'},'buffers':[{'byteLength':len(binary)}],
        'bufferViews':[{'buffer':0,'byteOffset':0,'byteLength':36},{'buffer':0,'byteOffset':36,'byteLength':6}],
        'accessors':[{'bufferView':0,'componentType':5126,'count':vertex_count,'type':'VEC3'},
                     {'bufferView':1,'componentType':5123,'count':3,'type':'SCALAR'}],
        'meshes':[{'primitives':[{'attributes':{'POSITION':0},'indices':1}]}]}
    encoded=json.dumps(doc).encode(); encoded += b' ' * (-len(encoded)%4)
    binary+=b'\0'*(-len(binary)%4)
    body=struct.pack('<II',len(encoded),0x4E4F534A)+encoded+struct.pack('<II',len(binary),0x004E4942)+binary
    return struct.pack('<4sII',b'glTF',2,12+len(body))+body


class UploadedAssetTests(unittest.TestCase):
    def inspect(self, data):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.glb';p.write_bytes(data);return module.audit(p)

    def test_valid_triangle(self):
        self.assertEqual(self.inspect(glb())['triangles'],1)

    def test_reject_outside_indices(self):
        with self.assertRaisesRegex(ValueError,'triangle indices'):self.inspect(glb((0,1,9)))

    def test_reject_accessor_overflow(self):
        with self.assertRaisesRegex(ValueError,'buffer view'):self.inspect(glb(vertex_count=4))

    def test_reject_truncated_container(self):
        with self.assertRaisesRegex(ValueError,'header'):self.inspect(glb()[:-4])

    def test_uploaded_bytes_match_manifest(self):
        manifest=json.loads((ROOT/'data/intake/w04-20261011.json').read_text())
        for asset in manifest['assets']:
            with self.subTest(asset=asset['slug']):
                actual=module.audit(ROOT/asset['source'])
                self.assertEqual(actual,asset['audit'])
                self.assertFalse(actual['production_approved'])

    def test_usd_correction_preserves_original_bytes(self):
        folder=ROOT/'assets/intake/w04-20261011'
        self.assertEqual((folder/'source-mislabeled.usdz').read_bytes(),(folder/'source-corrected.usdc').read_bytes())
        self.assertTrue((folder/'source-corrected.usdc').read_bytes().startswith(b'PXR-USDC'))




queue_spec = importlib.util.spec_from_file_location('queue_comfy', ROOT / 'tools/intake/queue_comfy_generation.py')
queue = importlib.util.module_from_spec(queue_spec); queue_spec.loader.exec_module(queue)


class GenerationReceiptTests(unittest.TestCase):
    def test_second_run_does_not_repeat_accepted_jobs(self):
        calls=[]
        def send(*args):
            calls.append(args); return {'prompt_id': str(len(calls))}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'receipts.json'; batch=[('one',{'seed':1}),('two',{'seed':2})]
            queue.submit_batch(batch,'http://localhost:8188',p,send)
            queue.submit_batch(batch,'http://localhost:8188/',p,send)
            self.assertEqual(len(calls),2)
            self.assertEqual(len(json.loads(p.read_text())),2)

    def test_network_uncertainty_is_not_retried(self):
        calls=[]
        def send(*args):
            calls.append(args); raise TimeoutError('Accepted response may have been lost')
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'receipts.json'; batch=[('one',{'seed':1})]
            with self.assertRaises(TimeoutError):queue.submit_batch(batch,'http://localhost',p,send)
            self.assertEqual(json.loads(p.read_text())[0]['status'],'submitting')
            with self.assertRaisesRegex(RuntimeError,'Unresolved'):queue.submit_batch(batch,'http://localhost',p,send)
            self.assertEqual(len(calls),1)

    def test_legacy_receipt_and_changed_seed(self):
        calls=[]
        def send(*args):
            calls.append(args); return {'prompt_id':'new'}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'receipts.json'
            p.write_text(json.dumps([{'name':'old','workflow':{'seed':1},'prompt_id':'existing','status':'queued'}]))
            queue.submit_batch([('old',{'seed':1}),('new',{'seed':2})],'http://localhost',p,send)
            self.assertEqual(len(calls),1)
            self.assertEqual(json.loads(p.read_text())[0]['prompt_id'],'existing')

    def test_invalid_journal_is_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'receipts.json';p.write_text('{invalid')
            with self.assertRaises(ValueError):queue.submit_batch([], 'http://localhost', p, lambda *a:None)
            self.assertEqual(p.read_text(),'{invalid')

    def test_lock_prevents_concurrent_submit(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'receipts.json';lock=Path(str(p)+'.lock');lock.write_text('occupied')
            with self.assertRaisesRegex(RuntimeError,'holds'):queue.submit_batch([], 'http://localhost', p, lambda *a:None)
            self.assertEqual(lock.read_text(),'occupied')

    def test_rejection_retains_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'receipts.json'
            with self.assertRaisesRegex(RuntimeError,'rejected'):
                queue.submit_batch([('one',{'seed':1})],'http://localhost',p,lambda *a:{'node_errors':{'5':'missing model'}})
            self.assertEqual(json.loads(p.read_text())[0]['status'],'rejected')

if __name__=='__main__':unittest.main()
