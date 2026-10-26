from __future__ import annotations
import importlib.util
from pathlib import Path
import unittest

SOURCE=Path(__file__).resolve().parents[2]/'unreal/NARIS_W04/Content/Python/naris_shipping_map_rules.py'
spec=importlib.util.spec_from_file_location('shipping_rules',SOURCE)
rules=importlib.util.module_from_spec(spec)
spec.loader.exec_module(rules)
REQ={'required_actor_labels':['PlayerStart','Boss'],'zones':[{'label':'ZONE_A'}], 'required_actor_classes':['SkyLight'], 'required_actor_label_classes':{'PlayerStart':'PlayerStart','Boss':'BoneBeastBoss'},'forbidden_actor_labels':['RuntimeSmokeDirector'],'forbidden_label_prefixes':['DEV_','BLOCKOUT_']}
ACTORS=[{'label':'PlayerStart','class_names':['PlayerStart'],'static_mesh_paths':[]},{'label':'Boss','class_names':['BoneBeastBoss'],'static_mesh_paths':[]},{'label':'ZONE_A','class_names':['TargetPoint'],'static_mesh_paths':[]},{'label':'Sky','class_names':['SkyLight'],'static_mesh_paths':[]}]
class ShippingSnapshotTests(unittest.TestCase):
 def test_valid_snapshot(self):self.assertEqual(rules.evaluate_snapshot(REQ,ACTORS)['errors'],[])
 def test_missing_zone(self):self.assertIn('ZONE_A',rules.evaluate_snapshot(REQ,ACTORS[:2])['missing_labels'])
 def test_spoofed_actor_label(self):
  actors=[dict(a) for a in ACTORS];actors[1]['class_names']=['TargetPoint'];self.assertTrue(rules.evaluate_snapshot(REQ,actors)['class_mismatches'])
 def test_duplicate_required_label(self):self.assertIn('Boss',rules.evaluate_snapshot(REQ,ACTORS+[ACTORS[1]])['duplicate_required_labels'])
 def test_blockout_prefix(self):self.assertTrue(rules.evaluate_snapshot(REQ,ACTORS+[{'label':'BLOCKOUT_Floor','class_names':[],'static_mesh_paths':[]}])['errors'])
 def test_review_prefix(self):self.assertTrue(rules.evaluate_snapshot(REQ,ACTORS+[{'label':'REVIEW_Rock','class_names':[],'static_mesh_paths':[]}])['errors'])
 def test_renamed_basic_shape_still_rejected(self):self.assertTrue(rules.evaluate_snapshot(REQ,ACTORS+[{'label':'FinalFloor','class_names':['StaticMeshActor'],'static_mesh_paths':['/Engine/BasicShapes/Cube.Cube']}])['prototype_meshes'])
 def test_missing_classes(self):self.assertIn('SkyLight',rules.evaluate_snapshot(REQ,ACTORS[:-1])['missing_actor_classes'])
 def test_empty_contract_rejected(self):self.assertTrue(rules.evaluate_snapshot({},ACTORS)['errors'])
 def test_blueprint_subclass_can_pass(self):
  actors=[dict(a) for a in ACTORS];actors[1]['class_names']=['BP_Boss_C','BoneBeastBoss'];self.assertFalse(rules.evaluate_snapshot(REQ,actors)['errors'])
if __name__=='__main__':unittest.main()
