import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'blender/audit_char001_glb.py'

class Char001GlbBehavior(unittest.TestCase):
    def fixture(self):
        return {'nodes': [{'name': 'root', 'children': list(range(1, 92))}] +
                [{'name': f'bone_{i}'} for i in range(1, 92)],
                'skins': [{'joints': list(range(92))}]}

    def run_audit(self, doc):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'candidate.gltf'
            path.write_text(json.dumps(doc))
            return subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)

    def test_reference_structure(self):
        self.assertEqual(self.run_audit(self.fixture()).returncode, 0)

    def test_rejects_prototype_count(self):
        doc = self.fixture(); doc['skins'][0]['joints'] = list(range(18))
        result = self.run_audit(doc)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('92 unique', result.stdout)

    def test_rejects_duplicate_joint(self):
        doc = self.fixture(); doc['skins'][0]['joints'][-1] = 0
        self.assertNotEqual(self.run_audit(doc).returncode, 0)

    def test_rejects_invalid_indices(self):
        for value in (-1, 200):
            doc = self.fixture(); doc['skins'][0]['joints'][-1] = value
            result = self.run_audit(doc)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn('invalid joint', result.stdout)

    def test_rejects_cycle_and_multiple_parent(self):
        doc = self.fixture(); doc['nodes'][1]['children'] = [0]
        self.assertIn('cycle', self.run_audit(doc).stdout)
        doc = self.fixture(); doc['nodes'][1]['children'] = [2]
        self.assertIn('multiple parents', self.run_audit(doc).stdout)

    def test_rejects_controls_and_nonfinite(self):
        doc = self.fixture(); doc['nodes'][1]['name'] = 'CTRL_hand'
        self.assertNotEqual(self.run_audit(doc).returncode, 0)
        doc = self.fixture(); doc['nodes'][1]['translation'] = [float('nan'), 0, 0]
        self.assertNotEqual(self.run_audit(doc).returncode, 0)
