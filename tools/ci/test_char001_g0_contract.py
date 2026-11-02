from pathlib import Path
import json, unittest
ROOT=Path(__file__).resolve().parents[2]
class Char001G0Contract(unittest.TestCase):
    def test_numeric_reconciliation(self):
        d=json.loads((ROOT/'data/char001_skeleton_contract.json').read_text())
        self.assertEqual(d['authoring_entities'],92)
        self.assertEqual(d['runtime_bones'],87)
        self.assertEqual(d['skin_affecting_bones'],83)
        self.assertEqual(d['primary_deform_bones'],67)
        self.assertEqual(d['twist_deform_bones'],16)
        self.assertEqual(len(d['helpers']),4)
        self.assertEqual(len(d['sockets']),5)
        self.assertEqual(d['runtime_bones'], d['skin_affecting_bones']+len(d['helpers']))
        self.assertEqual(d['authoring_entities'],d['runtime_bones']+len(d['sockets']))
        self.assertEqual(d['export_policy']['max_influences_per_vertex'],4)
        self.assertFalse(d['export_policy']['control_rig_exported'])
    def test_stage_g1a_never_auto_approves_visual(self):
        d=json.loads((ROOT/'data/char001_skeleton_contract.json').read_text())
        self.assertEqual(d['current_stage'],'G1-A')
        self.assertNotEqual(d['gate_status'],'PASS')
        self.assertFalse(d['blender_runtime_verified'])
        self.assertFalse(d['unreal_runtime_verified'])
    def test_source_hash_locked(self):
        d=json.loads((ROOT/'data/char001_skeleton_contract.json').read_text())
        self.assertEqual(d['source_glb_sha256'],'06c07d245c3830bfac6b473b8ca24852171bd3185fb5e1e902b387d1ed02ecdf')
if __name__=='__main__': unittest.main()
