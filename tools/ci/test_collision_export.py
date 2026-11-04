"""Behavioral regressions for Blender exchange; fake bpy is not DCC evidence."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location('collision_export_under_test', ROOT / 'tools/blender/naris_export.py')
EXPORTER = importlib.util.module_from_spec(SPEC)
with patch.dict(sys.modules, {'bpy': NS()}):
    SPEC.loader.exec_module(EXPORTER)


def obj(name, uv=True, kind='MESH'):
    o = NS(name=name, type=kind, scale=(1.,1.,1.), rotation_euler=(0.,0.,0.), location=(0.,0.,0.), data=NS(polygons=[1], uv_layers=[NS(name='UVMap')] if uv else [], materials=[]), selected=False)
    o.select_set = lambda value: setattr(o, 'selected', value)
    return o


class CollisionExportTests(unittest.TestCase):
    def test_collision_does_not_require_uv(self):
        for prefix in EXPORTER.COLLISION_PREFIXES:
            self.assertEqual(EXPORTER.validate_object(obj(prefix+'Wall_00', uv=False)), [])

    def test_render_mesh_still_requires_uv(self):
        self.assertTrue(EXPORTER.validate_object(obj('Wall', uv=False)))

    def test_numbered_and_exact_targets(self):
        for helper in ('UCX_SM_Wall_01', 'UCX_SM_Wall_01_00'):
            self.assertEqual(EXPORTER.validate_collision_bindings([obj('SM_Wall_01'), obj(helper)]), [])

    def test_mismatch_and_blender_duplicate_suffix_rejected(self):
        for helper in ('UCX_Wall_00', 'UCX_SM_Wall_01_00.001'):
            self.assertTrue(EXPORTER.validate_collision_bindings([obj('SM_Wall_01'), obj(helper)]))

    def test_empty_helper_and_nonmesh_rejected(self):
        o = obj('UCX_Wall_00', uv=False)
        o.data.polygons = []
        self.assertTrue(EXPORTER.validate_object(o))
        self.assertTrue(EXPORTER.validate_object(obj('UBX_Wall_00', kind='EMPTY')))
        self.assertTrue(EXPORTER.validate_collision_bindings([obj('UCX_Wall_00')]))

    def test_fbx_keeps_helpers_glb_excludes_them(self):
        selected = [obj('Wall'), obj('UCX_Wall_00', uv=False)]
        calls = {}
        fake = NS(data=NS(filepath='fixture.blend'), context=NS(selected_objects=[], view_layer=NS(objects=NS(active=None))), ops=NS(export_scene=NS(fbx=lambda **kw: calls.update(fbx=[o.name for o in selected if o.selected]), gltf=lambda **kw: calls.update(glb=[o.name for o in selected if o.selected]))))
        with tempfile.TemporaryDirectory() as td:
            registry = Path(td)/'registry.json'
            aid = 'NARIS-W04-ENV-WALL-0001'
            registry.write_text(json.dumps({'assets':[{'id':aid,'world':'W04'}]}))
            args = NS(out=td, registry=str(registry), asset_id=aid, no_fbx=False, no_gltf=False)
            with patch.object(EXPORTER, 'bpy', fake), patch.object(EXPORTER, 'parse_args', return_value=args), patch.object(EXPORTER, 'select_asset_objects', return_value=(selected, [])):
                self.assertEqual(EXPORTER.main(), 0)
        self.assertEqual(calls, {'fbx':['Wall','UCX_Wall_00'], 'glb':['Wall']})


if __name__ == '__main__':
    unittest.main()
