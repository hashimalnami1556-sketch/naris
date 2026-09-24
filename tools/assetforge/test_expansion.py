import collections
import hashlib
import json
import math
from pathlib import Path
import tempfile
import unittest
from expand_w04 import ROOT, PACK, build, generate, FAMILIES

class ExpansionTests(unittest.TestCase):
    def test_every_mesh_is_finite_closed_and_non_degenerate(self):
        for family in FAMILIES:
            for v in range(1,6):
                mesh=build(family,v);edges=collections.Counter()
                self.assertTrue(all(math.isfinite(c) for p in mesh.vertices for c in p))
                self.assertGreater(len(mesh.faces),0)
                for face in mesh.faces:
                    self.assertEqual(len(face),len(set(face)))
                    for a,b in zip(face,face[1:]+face[:1]):edges[tuple(sorted((a,b)))]+=1
                    a,b,c=[mesh.vertices[i] for i in face[:3]]
                    u=[b[i]-a[i] for i in range(3)];w=[c[i]-a[i] for i in range(3)]
                    cross=[u[1]*w[2]-u[2]*w[1],u[2]*w[0]-u[0]*w[2],u[0]*w[1]-u[1]*w[0]]
                    self.assertGreater(sum(x*x for x in cross),1e-12)
                self.assertEqual(set(edges.values()),{2},(family,v))
    def test_registry_checksums_and_distinct_geometry(self):
        manifest=json.loads((ROOT/PACK/'manifest.json').read_text())
        registry=json.loads((ROOT/'data/MASTER_ASSET_REGISTRY.json').read_text())['assets']
        ids=[a['id'] for a in registry];hashes=[]
        self.assertEqual(len(manifest['assets']),97)
        for asset in manifest['assets']:
            self.assertEqual(ids.count(asset['id']),1)
            raw=(ROOT/asset['mesh']).read_bytes();digest=hashlib.sha256(raw).hexdigest()
            self.assertEqual(digest,asset['sha256']);hashes.append(digest)
            obj=ROOT/PACK/(asset['id']+'.obj')
            self.assertIn('\nf ',obj.read_text())
        self.assertEqual(len(set(hashes)),97)
    def test_generation_is_idempotent_and_preserves_prior_records(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);(root/'data').mkdir()
            path=root/'data/MASTER_ASSET_REGISTRY.json'
            old={'id':'keep','status':'concept','notes':'preserve'}
            path.write_text(json.dumps({'assets':[old]}))
            generate(root);first=path.read_bytes();generate(root)
            self.assertEqual(first,path.read_bytes())
            self.assertEqual(json.loads(first)['assets'][0],old)

if __name__=='__main__':unittest.main()
