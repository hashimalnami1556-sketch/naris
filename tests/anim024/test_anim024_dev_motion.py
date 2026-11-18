"""ANIM-024: source-independent contracts for non-shipping motion profiles.

Original-GLB integration is covered by the external user handoff; no fake
asset is substituted for the original in CI.
"""
import math,sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools'/'assetforge'))
from anim024_dev_motion import (KINDS,BONES,motion_profile,quaternion_x,
    world_transforms,audit_preview,build_preview,_append_float_accessor)

class PreviewMotionContracts(unittest.TestCase):
    def test_seven_preview_actions_are_distinct(self):
        self.assertEqual(set(KINDS),{'Walk','Run','LightAttack','Dodge','Block','Jump','Death'})
    def test_motion_profiles_have_only_unit_quaternions(self):
        for name in KINDS:
            for u in np.linspace(0,1,21):
                profile=motion_profile(name,float(u))
                for bone in BONES:
                    self.assertAlmostEqual(np.linalg.norm(profile[bone]),1,places=6)
    def test_walk_run_are_loopable(self):
        for name in ('Walk','Run'):
            a=motion_profile(name,0)
            b=motion_profile(name,1)
            for k in a:
                np.testing.assert_allclose(a[k],b[k],atol=1e-12)
    def test_action_start_and_end_return_to_neutral(self):
        for name in ('LightAttack','Dodge','Block','Jump'):
            a=motion_profile(name,0)
            b=motion_profile(name,1)
            for bone in BONES:
                np.testing.assert_allclose(a[bone],b[bone],atol=1e-12)
    def test_death_has_nonlooping_final_pose(self):
        self.assertFalse(KINDS['Death']['loop'])
        self.assertLess(motion_profile('Death',1)['pelvis_t'],-.1)
    def test_action_rejects_out_of_range(self):
        with self.assertRaises(ValueError):motion_profile('Walk',1.1)
    def test_quaternion_x_90(self):
        np.testing.assert_allclose(quaternion_x(90),[math.sqrt(.5),0,0,math.sqrt(.5)],atol=1e-12)
    def test_world_pose_hierarchy(self):
        doc={'nodes':[{'name':'root','children':[1],'translation':[1,0,0]},
                      {'name':'foot_L','translation':[0,-1,0]}]}
        world=world_transforms(doc,{})
        np.testing.assert_allclose(world[1][:3,3],[1,-1,0])
    def test_dev_clips_are_never_production_coverage(self):
        doc={'animations':[{'name':'A_Idle'},
             {'name':'DEV_ONLY_Walk_InPlace','extras':{'naris_dev_only':True}},
             {'name':'A_Attack','extras':{'production_approved':False}}]}
        report=audit_preview(doc)
        self.assertEqual(report['production_names_present'],['idle'])
        self.assertEqual(len(report['excluded_dev_clips']),2)
        self.assertFalse(report['ready_for_release'])
    def test_pinned_source_prevents_unrecognized_rebuilds(self):
        with self.assertRaises(ValueError):build_preview({},b'', 'not-an-approved-digest')
    def test_animation_accessors_are_finite(self):
        doc={'accessors':[],'bufferViews':[]}
        binary=bytearray(b'abcd')
        with self.assertRaises(ValueError):_append_float_accessor(doc,binary,np.array([float('nan')]))
    def test_original_gameplay_not_claimed(self):
        self.assertNotIn('PIE',KINDS)
        self.assertFalse(any(x['loop'] for x in KINDS.values() if x is KINDS['Death']))

if __name__=='__main__':unittest.main()
