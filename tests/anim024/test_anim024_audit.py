"""ANIM-024 source contract tests; real original GLB optional on CI."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'/'assetforge'))
from anim024_audit import inspect_gltf,gate,inspect_file
class AnimationContracts(unittest.TestCase):
    def test_missing_attack_blocks_minimum_coverage(self):
        c={k:True for k in ('idle','walk','run','dodge','block','death')}
        r=gate(c)
        self.assertFalse(r['minimum_named_clip_coverage'])
        self.assertIn('attack',r['missing'])
    def test_all_names_do_not_certify_runtime(self):
        r=gate({k:True for k in ('idle','walk','run','attack','dodge','block','death')})
        self.assertTrue(r['minimum_named_clip_coverage'])
        self.assertFalse(r['production_ready'])
    def test_one_chest_idle_cannot_pass(self):
        d={'nodes':[{'name':'chest'}],
           'animations':[{'name':'A_Character1_Idle',
                          'channels':[{'target':{'node':0,'path':'rotation'}}]}]}
        r=inspect_gltf(d)
        self.assertEqual(r['clip_count'],1)
        self.assertEqual(r['clips'][0]['animated_nodes'],['chest'])
        self.assertEqual(len(r['gate']['missing']),6)
    def test_no_animation_is_blocked(self):
        r=inspect_gltf({'nodes':[],'animations':[]})
        self.assertEqual(r['clip_count'],0)
        self.assertFalse(r['gate']['minimum_named_clip_coverage'])
    def test_invalid_target_rejected(self):
        with self.assertRaises(ValueError):
            inspect_gltf({'nodes':[],'animations':[{'channels':[{'target':{'node':2,'path':'rotation'}}]}]})
    def test_dev_only_name_cannot_satisfy_production_gate(self):
        document={'nodes':[], 'animations':[
            {'name':'DEV_ONLY_Walk_InPlace',
             'extras':{'naris_dev_only':True,'production_approved':False},'channels':[]},
            {'name':'A_Dev_Attack',
             'extras':{'production_approved':False},'channels':[]},
            {'name':'A_Idle','channels':[]}]}
        report=inspect_gltf(document)
        self.assertTrue(report['named_clip_coverage']['idle'])
        self.assertFalse(report['named_clip_coverage']['walk'])
        self.assertFalse(report['named_clip_coverage']['attack'])
        self.assertFalse(report['gate']['minimum_named_clip_coverage'])

    def test_real_source_when_present(self):
        source=os.environ.get('NARIS_ANIM024_SOURCE')
        if not source:self.skipTest('Original user GLB not present in GitHub CI')
        r=inspect_file(Path(source))
        self.assertEqual(r['clip_count'],1)
        self.assertEqual(r['clips'][0]['animated_nodes'],['chest'])
        self.assertFalse(r['gate']['minimum_named_clip_coverage'])
if __name__=='__main__':unittest.main()
