"""Actual-source tests. GitHub CI records an explicit SKIP when no GLB is available."""
import os,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"/"assetforge"))
from char023_pose_audit import evaluate

class OriginalIdleRigEvidence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        p=os.environ.get('NARIS_CHAR023_SOURCE')
        if not p or not Path(p).is_file():
            raise unittest.SkipTest('Actual user source GLB not available in repo CI; use NARIS_CHAR023_SOURCE')
        cls.result=evaluate(Path(p))
    def test_original_animations_not_invented(self):
        self.assertEqual(self.result['source_animated_node'],'chest')
        self.assertEqual([x['source_idle_time_s'] for x in self.result['sampled_original_idle']],[0,.75,1.5])
    def test_real_sword_has_weighted_edge_distortion(self):
        mid=self.result['sampled_original_idle'][1]
        self.assertGreater(mid['original_skinned']['max_relative_edge_change'],.1)
        self.assertLess(mid['rigid_hand_mount']['max_relative_edge_change'],1e-9)
    def test_virtual_socket_grip_constraint_under_turns(self):
        self.assertEqual(len(self.result['synthetic_wrist_turns']),5)
        self.assertLess(max(x['grip_constraint_error'] for x in self.result['synthetic_wrist_turns']),1e-8)
    def test_ue_socket_remains_unverified(self):
        self.assertEqual(self.result['engine_import'],'NOT_RUN')
        self.assertFalse(self.result['visual_grip_approval'])

if __name__=='__main__':unittest.main()
