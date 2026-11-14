import unittest
import numpy as np
from char022_cloth_topology import clean_candidate, topology

class Tests(unittest.TestCase):
    def test_duplicate_and_small_island(self):
        p=np.array([[0,0,0],[1,0,0],[0,1,0],[1,1,0],[3,0,0],[4,0,0],[3,1,0]],float)
        f=np.array([[0,1,2],[2,1,3],[2,1,0],[4,5,6]])
        result=clean_candidate(p,f,min_faces=2)
        self.assertEqual(result['before']['duplicate_faces'],1)
        self.assertEqual(result['after']['faces'],2)
        self.assertEqual(result['after']['components'],1)
        self.assertEqual(result['removed_duplicate_ids'],[2])
        self.assertEqual(result['removed_island_ids'],[3])
        np.testing.assert_array_equal(result['face_ids'],[0,1])
    def test_nonmanifold_remains_blocked(self):
        p=np.array([[0,0,0],[1,0,0],[0,1,0],[0,-1,0],[0,0,1]],float)
        f=np.array([[0,1,2],[1,0,3],[0,1,4]])
        r=clean_candidate(p,f,min_faces=1)
        self.assertEqual(r['after']['nonmanifold_edges'],1)
        self.assertFalse(r['topology_pass'])
    def test_weld_and_representative_mapping(self):
        p=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,0]],float)
        r=clean_candidate(p,np.array([[3,1,2]]),min_faces=1)
        self.assertEqual(len(r['positions']),3)
        np.testing.assert_array_equal(r['positions'],p[r['source_vertex_ids']])
    def test_invalid_index(self):
        with self.assertRaises(ValueError):clean_candidate(np.zeros((3,3)),np.array([[0,1,3]]),min_faces=1)
    def test_degenerate_removed(self):
        p=np.array([[0,0,0],[1,0,0],[0,1,0]],float)
        r=clean_candidate(p,np.array([[0,1,2],[0,0,1]]),min_faces=1)
        self.assertEqual(r['removed_degenerate_ids'],[1])
        self.assertEqual(r['after']['degenerate_faces'],0)
    def test_winding_conflict(self):
        p=np.array([[0,0,0],[1,0,0],[0,1,0],[1,1,0]],float)
        f=np.array([[0,1,2],[1,2,3]])
        self.assertEqual(topology(p,f)['orientation_conflicts'],1)
    def test_source_immutable(self):
        p=np.array([[0,0,0],[1,0,0],[0,1,0]],float);f=np.array([[0,1,2],[2,1,0]])
        pc=p.copy();fc=f.copy();clean_candidate(p,f,min_faces=1)
        np.testing.assert_array_equal(pc,p);np.testing.assert_array_equal(fc,f)
    def test_empty_candidate_rejected(self):
        with self.assertRaises(ValueError):clean_candidate(np.array([[0,0,0],[1,0,0],[0,1,0]],float),np.array([[0,1,2]]),min_faces=2)
if __name__=='__main__':unittest.main()
