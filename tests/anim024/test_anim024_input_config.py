"""Regression contract for ANIM-024 W04 input map after real UE5.7 PIE failed.

Source-only checks. A separate real Unreal commandlet run is required for PIE proof.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "unreal" / "NARIS_W04" / "Config" / "DefaultInput.ini"


class W04InputConfigRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = INPUT.read_text(encoding="utf-8")
        cls.actions = [line for line in cls.text.splitlines() if line.startswith("+ActionMappings=")]
        cls.axes = [line for line in cls.text.splitlines() if line.startswith("+AxisMappings=")]

    def test_keys_are_serialized_as_unreal_scalars_not_json_objects(self):
        self.assertNotIn('Key=(KeyName=', self.text)
        self.assertNotIn('Key=()', self.text)
        self.assertFalse(re.search(r'Key=\\s*(?:\\(|\\s*$)', self.text))

    def test_input_mapping_list_has_no_escaped_newlines(self):
        self.assertNotIn(r"\\n+", self.text)
        self.assertNotIn(r"\\n", self.text)

    def test_controls_are_not_silently_deleted_by_repair(self):
        self.assertEqual(len(self.actions), 43)
        self.assertEqual(len(self.axes), 14)
        for line in self.actions + self.axes:
            self.assertRegex(line, r'Key=[A-Za-z0-9_]+')
        self.assertTrue(any('ActionName="LightAttack",Key=LeftMouseButton' in x for x in self.actions))
        self.assertTrue(any('ActionName="Jump",Key=SpaceBar' in x for x in self.actions))
        self.assertTrue(any('AxisName="MoveForward",Key=W,Scale=1.0' in x for x in self.axes))
        self.assertTrue(any('AxisName="MoveRight",Key=D,Scale=1.0' in x for x in self.axes))

    def test_axis_key_scale_pairs_are_unique(self):
        entries = []
        for line in self.axes:
            axis = re.search(r'AxisName="([^"]+)"', line)
            key = re.search(r'Key=([A-Za-z0-9_]+)', line)
            scale = re.search(r'Scale=([-+0-9.]+)', line)
            self.assertIsNotNone(axis)
            self.assertIsNotNone(key)
            self.assertIsNotNone(scale)
            entries.append((axis.group(1), key.group(1), float(scale.group(1))))
        self.assertEqual(len(entries), len(set(entries)))

if __name__ == "__main__":
    unittest.main()
