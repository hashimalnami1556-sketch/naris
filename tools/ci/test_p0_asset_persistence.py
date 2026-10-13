"""Execute production recovery code against a fake Unreal library, not an engine."""
import ast,json,pathlib,sys,tempfile,types,unittest
from unittest.mock import patch
ROOT=pathlib.Path(__file__).resolve().parents[2]
ACTIVE='/Game/NARIS/Characters/HeroV3/SK_NARIS_AshenVessel_v3'
ARCHIVE='/Game/NARIS/Characters/HeroV3/Archive/SK_NARIS_AshenVessel_v3_PreP0'
CANDIDATE='/Game/NARIS/Characters/HeroProduction/SK_NARIS_AshenVessel_Production'
class Library:
 def __init__(self,assets,save=True,asset_save=True):self.assets=dict(assets);self.save=save;self.asset_save=asset_save;self.saves=0
 def does_asset_exist(self,path):return path in self.assets
 def make_directory(self,path):return True
 def rename_asset(self,a,b):
  if a not in self.assets or b in self.assets:return False
  self.assets[b]=self.assets.pop(a);return True
 def save_directory(self,*args):
  self.saves+=1
  if isinstance(self.save,Exception):raise self.save
  return self.save
 def save_loaded_asset(self,*args):return self.asset_save
class AssetPersistenceTests(unittest.TestCase):
 def rollback(self,library):
  source=(ROOT/'tools/unreal/p0_05_rollback_hero.py').read_text()
  tree=ast.parse(source)
  with tempfile.TemporaryDirectory() as directory:
   for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='PROJECT_ROOT' for t in node.targets):node.value=ast.Call(func=ast.Name(id='Path',ctx=ast.Load()),args=[ast.Constant(directory)],keywords=[])
   ast.fix_missing_locations(tree)
   unreal=types.SimpleNamespace(EditorAssetLibrary=library,log=lambda x:None)
   with patch.dict(sys.modules,{'unreal':unreal}):
    try:exec(compile(tree,'rollback.py','exec'),{})
    except RuntimeError:pass
   return json.loads((pathlib.Path(directory)/'Reports/P0-05_rollback.json').read_text())
 def test_success_requires_persisted_recovery(self):
  lib=Library({ACTIVE:'new',ARCHIVE:'baseline'});r=self.rollback(lib)
  self.assertEqual(r['status'],'PASS');self.assertTrue(r['persisted']);self.assertEqual(lib.assets[ACTIVE],'baseline');self.assertEqual(lib.assets[CANDIDATE],'new')
 def test_false_save_rejects_rollback_success(self):
  lib=Library({ACTIVE:'new',ARCHIVE:'baseline'},save=False);r=self.rollback(lib)
  self.assertEqual(r['status'],'FAIL');self.assertFalse(r['rolled_back']);self.assertEqual(r['reason'],'rollback_save_failed');self.assertEqual(lib.assets[ACTIVE],'baseline')
 def test_save_exception_is_reported(self):
  r=self.rollback(Library({ACTIVE:'new',ARCHIVE:'baseline'},save=OSError('disk full')))
  self.assertEqual(r['status'],'FAIL');self.assertIn('disk full',r['save_error'])
 def test_missing_active_restore_is_also_saved(self):
  lib=Library({ARCHIVE:'baseline'});r=self.rollback(lib)
  self.assertTrue(r['persisted']);self.assertEqual(lib.saves,1)
 def test_missing_archive_cannot_claim_recovery(self):
  lib=Library({ACTIVE:'baseline'});r=self.rollback(lib)
  self.assertEqual(r['status'],'FAIL');self.assertEqual(lib.assets[ACTIVE],'baseline');self.assertEqual(lib.saves,0)
 def promotion_save_block(self,library):
  tree=ast.parse((ROOT/'tools/unreal/p0_05_promote_hero.py').read_text());index=next(i for i,n in enumerate(tree.body) if isinstance(n,ast.FunctionDef) and n.name=='recover_after_save_failure')
  # Execute the real save/recovery block without bypassing any approval in Unreal.
  block=ast.Module(body=tree.body[index:index+3],type_ignores=[]);failure={}
  def fail(reason,extra):failure.update(reason=reason,**extra);raise RuntimeError(reason)
  env={'unreal':types.SimpleNamespace(EditorAssetLibrary=library),'ACTIVE':ACTIVE,'ARCHIVE':ARCHIVE,'CANDIDATE':CANDIDATE,'promoted':object(),'fail':fail}
  with self.assertRaises(RuntimeError):exec(compile(block,'promotion-save.py','exec'),env)
  return failure
 def test_failed_promotion_save_restores_baseline(self):
  lib=Library({ACTIVE:'new',ARCHIVE:'baseline'},asset_save=False);r=self.promotion_save_block(lib)
  self.assertTrue(r['rolled_back']);self.assertFalse(r['critical']);self.assertEqual(lib.assets[ACTIVE],'baseline')
 def test_failed_recovery_save_is_critical(self):
  lib=Library({ACTIVE:'new',ARCHIVE:'baseline'},save=False,asset_save=False);r=self.promotion_save_block(lib)
  self.assertFalse(r['rolled_back']);self.assertTrue(r['critical'])
if __name__=='__main__':unittest.main()
