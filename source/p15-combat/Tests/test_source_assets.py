import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile
import unittest

from glb_fixtures import encode, mesh, skinned

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('source_assets_tests', ROOT / 'Unreal/source_assets.py')
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
spec = importlib.util.spec_from_file_location('verify_sources_tests', ROOT / 'Scripts/verify_sources.py')
V = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V)


class SourceAssetTests(unittest.TestCase):
    def audit(self, pair):
        return S.GLB(encode(*pair)).audit()

    def test_triangle_passes(self):
        report = self.audit(mesh())
        self.assertTrue(report['verified'])
        self.assertEqual(report['triangles'], 1)
        self.assertFalse(report['combat_ready'])

    def test_wrong_declared_length(self):
        raw = bytearray(encode(*mesh()))
        struct.pack_into('<I', raw, 8, len(raw) + 4)
        with self.assertRaises(ValueError):
            S.GLB(raw)

    def test_wrong_version(self):
        raw = bytearray(encode(*mesh()))
        struct.pack_into('<I', raw, 4, 1)
        with self.assertRaises(ValueError):
            S.GLB(raw)

    def test_truncated_chunk(self):
        raw = bytearray(encode(*mesh()))
        struct.pack_into('<I', raw, 12, len(raw))
        with self.assertRaises(ValueError):
            S.GLB(raw)

    def test_misaligned_chunk(self):
        raw = bytearray(encode(*mesh()))
        struct.pack_into('<I', raw, 12, 1)
        with self.assertRaises(ValueError):
            S.GLB(raw)

    def test_external_image(self):
        doc, binary = mesh()
        doc['images'] = [{'uri': '../texture.png'}]
        with self.assertRaises(ValueError):
            self.audit((doc, binary))

    def test_view_out_of_bounds(self):
        doc, binary = mesh()
        doc['bufferViews'][0]['byteLength'] = 100
        with self.assertRaises(ValueError):
            self.audit((doc, binary))

    def test_accessor_out_of_bounds(self):
        doc, binary = mesh()
        doc['accessors'][0]['count'] = 4
        with self.assertRaises(ValueError):
            self.audit((doc, binary))

    def test_invalid_stride(self):
        doc, binary = mesh()
        doc['bufferViews'][0]['byteStride'] = 8
        with self.assertRaises(ValueError):
            self.audit((doc, binary))

    def test_nonfinite_position(self):
        doc, binary = mesh()
        binary = struct.pack('<f', float('nan')) + binary[4:]
        with self.assertRaises(ValueError):
            self.audit((doc, binary))

    def test_negative_accessor(self):
        doc, binary = mesh()
        doc['meshes'][0]['primitives'][0]['attributes']['POSITION'] = -1
        with self.assertRaises(ValueError):
            self.audit((doc, binary))

    def test_negative_buffer_view(self):
        doc, binary = mesh()
        doc['accessors'][0]['bufferView'] = -1
        with self.assertRaises(ValueError):
            self.audit((doc, binary))

    def test_negative_mesh(self):
        doc, binary = mesh()
        doc['nodes'][0]['mesh'] = -1
        with self.assertRaises(ValueError):
            self.audit((doc, binary))

    def test_cycle(self):
        doc, binary = mesh()
        doc['nodes'][0]['children'] = [0]
        with self.assertRaises(ValueError):
            self.audit((doc, binary))

    def test_multiple_parents(self):
        doc, binary = mesh()
        doc['nodes'] += [{'children': [0]}, {'children': [0]}]
        with self.assertRaises(ValueError):
            self.audit((doc, binary))

    def test_unattached_skin_fails_gate(self):
        report = self.audit(skinned())
        self.assertFalse(report['verified'])
        self.assertIn('Skin 0 is not attached to a mesh node', report['errors'])

    def test_incorrect_inverse_bind_fails_gate(self):
        report = self.audit(skinned(bound=True))
        self.assertFalse(report['verified'])
        self.assertGreater(report['rest_bind_max_error'], .1)

    def test_correct_skin_passes(self):
        report = self.audit(skinned(bound=True, good_bind=True))
        self.assertTrue(report['verified'])
        self.assertEqual(report['rest_bind_max_error'], 0)

    def test_repair_attaches_skin_and_writes_column_major_bind(self):
        raw = encode(*skinned())
        repaired = S.GLB(S.repair_single_skin(raw))
        self.assertEqual(repaired.doc['nodes'][2]['skin'], 0)
        self.assertEqual(repaired.values(3)[0], (1,0,0,0,0,1,0,0,0,0,1,0,-.5,0,0,1))
        self.assertTrue(repaired.audit()['verified'])
        for i in (0, 1, 2):
            self.assertEqual(repaired.values(i), S.GLB(raw).values(i))

    def test_repair_is_idempotent(self):
        once = S.repair_single_skin(encode(*skinned()))
        self.assertEqual(S.repair_single_skin(once), once)

    def test_repair_refuses_ambiguous_ownership(self):
        doc, binary = skinned()
        doc['nodes'].append({'mesh': 0})
        with self.assertRaises(ValueError):
            S.repair_single_skin(encode(doc, binary))

    def test_zero_weights_fail(self):
        doc, binary = skinned(bound=True, good_bind=True)
        offset = doc['bufferViews'][2]['byteOffset']
        binary = binary[:offset] + struct.pack('<f', 0) + binary[offset+4:]
        with self.assertRaises(ValueError):
            self.audit((doc, binary))

    def test_out_of_range_joint_fails(self):
        doc, binary = skinned(bound=True, good_bind=True)
        offset = doc['bufferViews'][1]['byteOffset']
        binary = binary[:offset] + b'\xff' + binary[offset+1:]
        with self.assertRaises(ValueError):
            self.audit((doc, binary))

    def test_versioned_contract_requires_digest(self):
        with self.assertRaises(ValueError):
            S.normalize_spec({'schema_version': 2, 'assets': {'a.glb': {'required_classes': []}}})

    def test_legacy_contract_preserved(self):
        self.assertEqual(S.normalize_spec({'a.glb': ['StaticMesh']})['a.glb']['required_classes'], ['StaticMesh'])


class SourceContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.asset = self.root / 'a.glb'
        self.asset.write_bytes(encode(*mesh()))
        self.contract = {'schema_version': 2, 'assets': {'a.glb': {
            'sha256': hashlib.sha256(self.asset.read_bytes()).hexdigest(), 'required_classes': ['StaticMesh']}}}

    def test_exact_sources_pass(self):
        self.assertTrue(V.verify(self.root, self.contract)['verified'])

    def test_changed_source_fails(self):
        self.asset.write_bytes(self.asset.read_bytes() + b'\0')
        with self.assertRaises(ValueError):
            V.verify(self.root, self.contract)

    def test_extra_source_fails(self):
        (self.root / 'extra.glb').write_bytes(self.asset.read_bytes())
        with self.assertRaises(ValueError):
            V.verify(self.root, self.contract)

    def test_empty_source_fails(self):
        self.asset.unlink()
        with self.assertRaises(ValueError):
            V.verify(self.root, self.contract)

    def test_class_only_contract_rejected_for_build(self):
        with self.assertRaises(ValueError):
            V.verify(self.root, {'a.glb': ['StaticMesh']})
