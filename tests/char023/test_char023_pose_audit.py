"""Synthetic glTF pose contracts; no Unreal runtime required."""
import sys, unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/"tools"/"assetforge"))
from char023_pose_audit import rotation,slerp,world_matrices,rigid_from_hand,edge_strain

class PoseMathContracts(unittest.TestCase):
    def test_quaternion_z_90(self):
        q=[0,0,np.sin(np.pi/4),np.cos(np.pi/4)]
        np.testing.assert_allclose(rotation(q)@np.array([1,0,0]),[0,1,0],atol=1e-12)
    def test_normalizes_quaternion(self):
        np.testing.assert_allclose(rotation([0,0,0,9]),np.eye(3),atol=1e-12)
    def test_rejects_bad_quaternion(self):
        with self.assertRaises(ValueError):rotation([0,0,0,0])
    def test_slerp_midpoint(self):
        q=slerp([0,0,0,1],[0,0,1,0],.5)
        np.testing.assert_allclose(rotation(q)@np.array([1,0,0]),[0,1,0],atol=1e-12)
    def test_shortest_quat_sign(self):
        np.testing.assert_allclose(rotation(slerp([0,0,0,1],[0,0,0,-1],.3)),np.eye(3),atol=1e-12)
    def test_parent_rotation_affects_child(self):
        d={'nodes':[{'children':[1], 'translation':[2,0,0]}, {'translation':[1,0,0]}]}
        q=[0,0,np.sin(np.pi/4),np.cos(np.pi/4)]
        out=world_matrices(d,{0:q})
        np.testing.assert_allclose(out[1][:3,3],[2,1,0],atol=1e-12)
    def test_cycle_is_rejected(self):
        with self.assertRaises(ValueError):world_matrices({'nodes':[{'children':[1]},{'children':[0]}]})
    def test_rigid_hand_mounted_points_rotate_without_stretch(self):
        p=np.array([[1,0,0],[2,0,0],[1,1,0]],float)
        bind=np.eye(4);bind[:3,3]=[.3,0,0]
        R=np.eye(4);R[:3,:3]=rotation([0,0,np.sin(np.pi/4),np.cos(np.pi/4)]);R[:3,3]=[1,2,0]
        moved=rigid_from_hand(p,bind,R)
        self.assertLess(edge_strain(np.array([[0,1,2]]),np.arange(3),p,moved)['max_relative_edge_change'],1e-12)
        np.testing.assert_allclose(moved[0],R[:3,:3]@(p[0]-bind[:3,3])+R[:3,3])
    def test_detects_edge_stretch(self):
        p=np.array([[0,0,0],[1,0,0],[0,1,0]],float)
        after=p.copy();after[1]=[1.25,0,0]
        self.assertGreater(edge_strain(np.array([[0,1,2]]),np.arange(3),p,after)['max_relative_edge_change'],.20)
    def test_rigid_360_returns_bind_geometry(self):
        p=np.array([[0,0,1],[0,1,0]],float)
        h=np.eye(4);h[:3,3]=[.2,.1,.3]
        angle=np.pi*2;turn=np.eye(4)
        turn[:3,:3]=rotation([0,0,np.sin(angle/2),np.cos(angle/2)])
        np.testing.assert_allclose(rigid_from_hand(p,h,h@turn),p,atol=1e-12)
    def test_rotation_shape_is_strict(self):
        with self.assertRaises(ValueError):rotation([0,0,1])
    def test_out_of_range_slerp_rejected(self):
        with self.assertRaises(ValueError):slerp([0,0,0,1],[0,0,1,0],1.3)

if __name__=='__main__':unittest.main()
