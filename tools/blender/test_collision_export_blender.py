"""Run with Blender --background --python this_file.py from the repository root.
Creates a synthetic wall/UCX fixture in a temporary directory; never edits source assets.
"""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import bpy

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'docs/changes/ENV-003'

def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

current = load(ROOT/'tools/blender/naris_export.py', 'current_export')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
bpy.ops.mesh.primitive_cube_add()
wall = bpy.context.object
wall.name = 'SM_TestWall_01'
wall['naris_asset_id'] = 'NARIS-W04-ENV-WALL-0001'
bpy.ops.mesh.primitive_cube_add()
helper = bpy.context.object
helper.name = 'UCX_SM_TestWall_01_00'
helper.parent = wall
for uv in list(helper.data.uv_layers):
    helper.data.uv_layers.remove(uv)
assert not current.validate_object(helper)
assert not current.validate_collision_bindings([wall, helper])
result = {'blender':bpy.app.version_string, 'fixture':'synthetic cubes, not production collision', 'unreal':'NOT_RUN'}
old_path = Path('/tmp/naris_export_before.py')
if old_path.exists():
    old = load(old_path, 'before_export')
    result['before_issues'] = old.validate_object(helper)
    assert any('UV' in issue for issue in result['before_issues'])
with tempfile.TemporaryDirectory() as td:
    registry = Path(td)/'registry.json'
    registry.write_text(json.dumps({'assets':[{'id':wall['naris_asset_id'],'world':'W04'}]}))
    aid = wall['naris_asset_id']
    current.parse_args = lambda: SimpleNamespace(out=td, registry=str(registry), asset_id=aid, no_fbx=False, no_gltf=False)
    assert current.main() == 0
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(Path(td)/(aid+'.glb')))
    glb_names = sorted(o.name for o in bpy.context.scene.objects if o.type=='MESH')
    assert glb_names == ['SM_TestWall_01'], glb_names
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(Path(td)/(aid+'.fbx')))
    fbx_names = sorted(o.name for o in bpy.context.scene.objects if o.type=='MESH')
    assert fbx_names == ['SM_TestWall_01', 'UCX_SM_TestWall_01_00'], fbx_names
    result.update(glb_meshes=glb_names, fbx_meshes=fbx_names, roundtrip_assertions='passed')
OUT.mkdir(parents=True, exist_ok=True)
(OUT/'blender-roundtrip.json').write_text(json.dumps(result,indent=2)+'\n')
print('ENV003_BLENDER_ROUNDTRIP '+json.dumps(result))
