import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]

def module(name, path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result

RULES=module('stage29_rules','unreal/NARIS_W04/Content/Python/naris_stage29_rules.py')
REMAP=module('stage29_remap','tools/assets/remap_stage29_zones.py')
FOLDER=ROOT/'unreal/NARIS_W04/Content/NARIS/W04/Production/Stage29'
DATA=json.loads((FOLDER/'placements_corrected.json').read_text())
RECEIVED=json.loads((FOLDER/'placements_received.json').read_text())
POLICY=json.loads((FOLDER/'placement_policy.json').read_text())['roles']
LAYOUT=json.loads((ROOT/'NARIS_MASTER/09_WORLD/Ashen_Forest/LEVEL_LAYOUT.json').read_text())

class Stage29PlacementTests(unittest.TestCase):
    def test_corrected_candidate_obeys_world_and_zone_contracts(self):
        self.assertEqual(RULES.validate_manifest(DATA,LAYOUT,POLICY),[])

    def test_received_manifest_fails_every_zone(self):
        errors=RULES.validate_manifest(RECEIVED,LAYOUT,POLICY)
        self.assertEqual(sum('outside its declared' in e for e in errors),136)

    def test_translation_preserves_identity_scale_rotation_and_local_spacing(self):
        new=REMAP.remap(RECEIVED,LAYOUT)
        for zone in LAYOUT['zones']:
            rows=[(a,b)for a,b in zip(RECEIVED['placements'],new['placements'])if a['zone']==zone['id']]
            reference=None
            for a,b in rows:
                self.assertEqual(a['id'],b['id']);self.assertEqual(a['source'],b['source'])
                self.assertEqual(a['transform']['scale'],b['transform']['scale'])
                self.assertEqual(a['transform']['rotation_deg'],b['transform']['rotation_deg'])
                delta=[b['transform']['location_cm'][i]-a['transform']['location_cm'][i] for i in range(3)]
                if reference is None:reference=delta
                for x,y in zip(reference,delta):self.assertAlmostEqual(x,y)
                self.assertEqual(delta[2],0)

    def test_rejects_nonfinite_negative_duplicate_and_bad_zone(self):
        for field,value in [('location_cm',[float('nan'),0,0]),('scale',[-1,1,1]),('rotation_deg',[0,0])]:
            bad=copy.deepcopy(DATA);bad['placements'][0]['transform'][field]=value
            self.assertTrue(RULES.validate_manifest(bad,LAYOUT,POLICY))
        bad=copy.deepcopy(DATA);bad['placements'][1]['id']=bad['placements'][0]['id']
        self.assertTrue(RULES.validate_manifest(bad,LAYOUT,POLICY))

    def test_asset_resolution_never_chooses_first_suffix_match(self):
        self.assertIsNone(RULES.resolve_asset('Wolf',['/Game/Wolf_A.Wolf_A','/Game/Wolf_B.Wolf_B']))
        self.assertEqual(RULES.resolve_asset('Wolf',['/Game/Wolf.Wolf']),'/Game/Wolf.Wolf')
        self.assertIsNone(RULES.resolve_asset('Wolf',['/Game/Wolf.Wolf','/Game/Other/Wolf.Wolf']))

    def test_source_pass_and_editor_only_results_cannot_pass_g1(self):
        for report in ({},{'engine_executed':True,'mode':'dry_run','map_saved':False,'elements':[]}):
            self.assertEqual(RULES.decide_g1(report)['decision'],'G1 BLOCKED')

    def complete_report(self):
        rows=[dict(id=p['id'],status='placed',**{k:True for k in ('bounds_ok','materials_assigned','collision_ok','ground_ok','scale_ok','rotation_ok')})for p in DATA['placements']]
        review=dict(run_id='run-a',visible_element_ids=[r['id']for r in rows],**{k:'PASS' for k in ('pie_visibility','visual_materials','streaming_culling','ground_traversal','material_budget')})
        return dict(engine_executed=True,mode='apply',map_saved=True,run_id='run-a',elements=rows,runtime_review=review)

    def test_partial_stale_and_missing_runtime_evidence_block_g1(self):
        good=self.complete_report();self.assertEqual(RULES.decide_g1(good)['decision'],'G1 PASS')
        bad=copy.deepcopy(good);bad['elements'].pop();self.assertEqual(RULES.decide_g1(bad)['decision'],'G1 FAIL')
        bad=copy.deepcopy(good);bad['runtime_review']['run_id']='old-run';self.assertEqual(RULES.decide_g1(bad)['decision'],'G1 FAIL')
        bad=copy.deepcopy(good);bad['runtime_review']['visible_element_ids'].pop();self.assertEqual(RULES.decide_g1(bad)['decision'],'G1 FAIL')
        bad=copy.deepcopy(good);bad['engine_executed']=False;self.assertEqual(RULES.decide_g1(bad)['decision'],'G1 BLOCKED')


class Stage29MutationBoundaryTests(unittest.TestCase):
    def test_missing_assets_prevent_every_map_mutation(self):
        import sys,tempfile,types
        from unittest.mock import MagicMock,patch
        ue=types.ModuleType('unreal')
        levels=MagicMock();levels.is_in_play_in_editor.return_value=False
        actors=MagicMock();static=MagicMock()
        ue.LevelEditorSubsystem=type('LevelEditorSubsystem',(),{})
        ue.EditorActorSubsystem=type('EditorActorSubsystem',(),{})
        ue.StaticMeshEditorSubsystem=type('StaticMeshEditorSubsystem',(),{})
        ue.MaterialInstance=type('MaterialInstance',(),{})
        ue.get_editor_subsystem=lambda cls:{ue.LevelEditorSubsystem:levels,ue.EditorActorSubsystem:actors,ue.StaticMeshEditorSubsystem:static}[cls]
        ue.EditorLoadingAndSavingUtils=MagicMock()
        ue.EditorLoadingAndSavingUtils.get_dirty_map_packages.return_value=[]
        ue.EditorLoadingAndSavingUtils.get_dirty_content_packages.return_value=[]
        registry=MagicMock();registry.get_assets_by_path.return_value=[]
        ue.AssetRegistryHelpers=MagicMock();ue.AssetRegistryHelpers.get_asset_registry.return_value=registry
        ue.EditorAssetLibrary=MagicMock();ue.EditorAssetLibrary.does_asset_exist.return_value=True
        ue.log=MagicMock()
        ue.SystemLibrary=MagicMock();ue.SystemLibrary.get_engine_version.return_value='fake-test-no-engine'
        with tempfile.TemporaryDirectory() as saved,patch.dict(sys.modules,{'unreal':ue}):
            ue.Paths=types.SimpleNamespace(project_dir=lambda:str(ROOT/'unreal/NARIS_W04'),project_saved_dir=lambda:saved)
            importer=module('stage29_engine_test','unreal/NARIS_W04/Content/Python/naris_stage29_place.py')
            report=importer.execute(apply=True,template='/Game/Ground')
            self.assertTrue(report['errors']);self.assertFalse(report['map_saved'])
            levels.new_level.assert_not_called();levels.new_level_from_template.assert_not_called()
            levels.save_current_level.assert_not_called();actors.spawn_actor_from_object.assert_not_called()
            self.assertEqual(len(list(Path(saved).glob('TestReports/stage29_g1_*.json'))),1)

if __name__=='__main__':unittest.main()
