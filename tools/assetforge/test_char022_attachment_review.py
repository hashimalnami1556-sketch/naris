import unittest
import numpy as np
from attachment_review import attachment_profile

class AttachmentTests(unittest.TestCase):
    def setUp(self):
        self.p=np.array([[0,.7,0],[1,.7,0],[0,.6,0],[2,.3,0],[3,.3,0],[2,.2,0]],float)
        self.f=np.array([[0,1,2],[3,4,5]])
        self.ids=np.arange(6);self.shared=np.array([True,True,False,True,True,True]);self.w=np.ones(6)
    def run_profile(self,**kw):
        return attachment_profile(self.p,self.f,self.ids,self.shared,self.w,**kw)
    def test_exact_upper_boundary_pins(self):
        r=self.run_profile();np.testing.assert_array_equal(r['pinned'],[True,True,False,False,False,False])
    def test_lower_component_excluded(self):
        r=self.run_profile();np.testing.assert_array_equal(r['simulate'],[True,True,True,False,False,False]);self.assertTrue(r['candidate_gate'])
    def test_geodesic_ramp(self):
        r=self.run_profile();self.assertAlmostEqual(r['max_distance'][2],.06);self.assertTrue(np.all(r['max_distance'][3:]==0))
    def test_no_pins_fail_closed(self):
        r=self.run_profile(min_height=1.0);self.assertFalse(r['candidate_gate']);self.assertFalse(r['simulate'].any())
    def test_weights_filter(self):
        self.w[0]=.1;r=self.run_profile();self.assertFalse(r['pinned'][0]);self.assertTrue(r['pinned'][1])
    def test_nonshared_filter(self):
        self.shared[1]=False;r=self.run_profile();self.assertFalse(r['pinned'][1]);self.assertTrue(r['pinned'][0])
    def test_geometry_unchanged(self):
        before=self.p.copy();faces=self.f.copy();self.run_profile();np.testing.assert_array_equal(self.p,before);np.testing.assert_array_equal(self.f,faces)
    def test_invalid_weights(self):
        self.w[0]=1.1
        with self.assertRaises(ValueError):self.run_profile()
    def test_invalid_mapping(self):
        self.ids[0]=-1
        with self.assertRaises(ValueError):self.run_profile()
    def test_internal_vertex_not_pin(self):
        p=np.array([[0,.7,0],[1,.7,0],[1,.7,1],[0,.7,1],[.5,.7,.5]])
        f=np.array([[0,1,4],[1,2,4],[2,3,4],[3,0,4]])
        r=attachment_profile(p,f,np.arange(5),np.ones(5,bool),np.ones(5));self.assertFalse(r['pinned'][4])
if __name__=='__main__':unittest.main()
