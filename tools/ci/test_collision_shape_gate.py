"""Collision-count behavior with Unreal import stubbed; not engine execution."""
import importlib.util
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

path=Path(__file__).resolve().parents[2]/'unreal/NARIS_W04/Content/Python/naris_validate_production_assets.py'
spec=importlib.util.spec_from_file_location('shape_gate',path)
gate=importlib.util.module_from_spec(spec)
with patch.dict(sys.modules, {'unreal':SimpleNamespace()}):
    spec.loader.exec_module(gate)

class ShapeGateTests(unittest.TestCase):
    def test_zero_shapes_rejected(self):
        self.assertTrue(gate.collision_count_errors(0,0))
    def test_box_only_accepted(self):
        self.assertEqual(gate.collision_count_errors(0,1),[])
    def test_convex_only_accepted(self):
        self.assertEqual(gate.collision_count_errors(2,0),[])
    def test_negative_query_fails_even_when_other_count_positive(self):
        for counts in ((-1,2),(2,-1),(-1,-1)):
            self.assertTrue(gate.collision_count_errors(*counts))

if __name__=='__main__': unittest.main()
