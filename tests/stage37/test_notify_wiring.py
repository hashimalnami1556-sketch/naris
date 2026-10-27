from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[2]
H=(ROOT/'unreal/NARIS_W04/Source/NARIS_W04/Public/NarisCombatHitWindowNotifyState.h').read_text()
C=(ROOT/'unreal/NARIS_W04/Source/NARIS_W04/Private/NarisCombatHitWindowNotifyState.cpp').read_text()
A=(ROOT/'unreal/NARIS_W04/Content/Python/naris_stage37_animation_link_audit.py').read_text()
class TestWiring(unittest.TestCase):
 def test_native_notify(self):self.assertIn('UAnimNotifyState',H)
 def test_begin(self):self.assertIn('Combat->BeginHitWindow()',C)
 def test_end(self):self.assertIn('Combat->EndHitWindow()',C)
 def test_actor_guard(self):self.assertIn('IsValid(MeshComp->GetOwner())',C)
 def test_component_lookup(self):self.assertIn('FindComponentByClass<UNarisStage32CombatComponent>',C)
 def test_skeleton_link_audit(self):self.assertIn('animation_without_matching_mesh_skeleton',A)
if __name__=='__main__':unittest.main()
