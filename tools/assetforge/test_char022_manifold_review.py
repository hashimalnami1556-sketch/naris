import unittest
import numpy as np
from manifold_review import repair, pin_profile, prune_islands, capsule_review

class RepairTests(unittest.TestCase):
    def test_nonmanifold_removal(self):
        p=np.array([[0,0,0],[1,0,0],[0,1,0],[0,-1,0],[0,0,1],[2,0,0],[2,1,0]],float)
        f=np.array([[0,1,2],[1,0,3],[0,1,4],[1,5,6]])
        r=repair(p,f);self.assertEqual(r['removed_faces'],[0,1,2]);self.assertTrue(r['topology_pass'])
    def test_bowtie(self):
        p=np.array([[0,0,0],[1,0,0],[0,1,0],[-1,0,0],[0,-1,0]],float)
        f=np.array([[0,1,2],[0,3,4]])
        r=repair(p,f);self.assertEqual(len(r['positions']),6);self.assertTrue(r['topology_pass']);self.assertEqual(len(r['faces']),2)
    def test_orientation(self):
        p=np.array([[0,0,0],[1,0,0],[0,1,0],[1,1,0]],float);f=np.array([[0,1,2],[1,2,3]])
        r=repair(p,f);self.assertEqual(r['after']['orientation_conflicts'],0);self.assertEqual(len(r['flipped_faces']),1)
    def test_mapping_immutable(self):
        p=np.array([[0,0,0],[1,0,0],[0,1,0],[-1,0,0],[0,-1,0]],float);f=np.array([[0,1,2],[0,3,4]]);orig=f.copy()
        r=repair(p,f);np.testing.assert_array_equal(r['positions'],p[r['input_vertex_ids']]);np.testing.assert_array_equal(f,orig);np.testing.assert_array_equal(np.sort(r['input_vertex_ids'][r['faces']],axis=1),np.sort(f[r['input_face_ids']],axis=1))
    def test_no_empty(self):
        p=np.array([[0,0,0],[1,0,0],[0,1,0],[0,-1,0],[0,0,1]],float)
        with self.assertRaises(ValueError):repair(p,np.array([[0,1,2],[1,0,3],[0,1,4]]))
    def test_prune_preserves_face_and_vertex_mapping(self):
        p=np.array([[0,0,0],[1,0,0],[0,1,0],[1,1,0],[3,0,0],[4,0,0],[3,1,0]],float);f=np.array([[0,1,2],[2,1,3],[4,5,6]])
        r=repair(p,f);q=prune_islands(r,2);self.assertEqual(q['after']['faces'],2);self.assertEqual(q['removed_island_faces'],[2]);np.testing.assert_array_equal(q['positions'],p[q['input_vertex_ids']]);self.assertTrue(q['topology_pass'])
    def test_pins_and_unanchored(self):
        p=np.array([[0,.7,0],[.1,.7,0],[0,.6,0],[0,.1,0],[.1,.1,0],[0,.2,0]],float);f=np.array([[0,1,2],[3,4,5]])
        r=pin_profile(p,f,np.array([[0,.7,0]]),.04,.20,.12)
        self.assertEqual(r['max_distance'][0],0);self.assertEqual(r['unanchored_components'],[1]);self.assertFalse(r['pin_gate'])
    def test_pin_bounds(self):
        p=np.array([[0,.7,0],[.1,.7,0],[0,.6,0]],float);f=np.array([[0,1,2]])
        r=pin_profile(p,f,np.array([[0,.7,0]]),.04,.2,.12);self.assertTrue(r['pin_gate']);self.assertTrue(np.all((r['max_distance']>=0)&(r['max_distance']<=.12)))
class CapsuleReviewTests(unittest.TestCase):
    def test_segment_projection_and_clamp(self):
        p=np.array([[0,0,0],[.5,.2,0],[2,0,0]])
        r=capsule_review(p,[('leg',[0,0,0],[1,0,0],.1)])
        np.testing.assert_allclose(r['clearance'],[-.1,.1,.9]);self.assertEqual(r['summary'][0]['vertices_inside'],1)
    def test_overlapping_capsules(self):
        p=np.array([[.1,0,0],[1,0,0]])
        r=capsule_review(p,[('a',[0,0,0],[0,1,0],.2),('b',[1,0,0],[1,1,0],.3)])
        np.testing.assert_allclose(r['clearance'],[-.1,-.3]);self.assertEqual(r['inside_any'],2)
    def test_zero_length_rejected(self):
        with self.assertRaises(ValueError):capsule_review(np.array([[0,0,0.]]),[('bad',[0,0,0],[0,0,0],.1)])
    def test_negative_radius_rejected(self):
        with self.assertRaises(ValueError):capsule_review(np.array([[0,0,0.]]),[('bad',[0,0,0],[1,0,0],-.1)])
if __name__=='__main__':unittest.main()
