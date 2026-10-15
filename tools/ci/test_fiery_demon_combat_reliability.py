"""W04 Fiery Demon combat regressions (source-level, NOT an Unreal runtime test).

These contracts block backsliding while UE5.7 compile/PIE remain gated to a Windows runner.
"""
import pathlib
import re
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[2]
NATIVE=ROOT/"unreal/NARIS_W04/Source/NARIS_W04"
BASE_H=(NATIVE/"Public/BoneBeastBoss.h").read_text(encoding="utf-8")
DEMON_H=(NATIVE/"Public/NarisFieryDemonBoss.h").read_text(encoding="utf-8")
DEMON_C=(NATIVE/"Private/NarisFieryDemonBoss.cpp").read_text(encoding="utf-8")
BASE_C=(NATIVE/"Private/BoneBeastBoss.cpp").read_text(encoding="utf-8")

class FieryDemonCombatReliability(unittest.TestCase):
    def test_boss_can_override_phase_attack_selection(self):
        self.assertRegex(BASE_H, r"virtual\s+bool\s+RequestPhaseAttack\s*\(")
        self.assertRegex(DEMON_H, r"bool\s+RequestPhaseAttack\s*\(\s*\)\s*override")

    def test_phase1_is_ground_smash_phase2_is_ember_nova(self):
        self.assertRegex(DEMON_C, r"ANarisFieryDemonBoss::RequestPhaseAttack\s*\(")
        self.assertIn('RequestAttack(TEXT("GroundSmash"), Phase1AttackDamage)', DEMON_C)
        self.assertIn('RequestAttack(TEXT("EmberNova"), Phase2AttackDamage)', DEMON_C)

    def test_demon_uses_at_most_two_combat_phases(self):
        self.assertIn("FallbackPhase2HealthPercent = 0.55f;", DEMON_C)
        self.assertIn("FallbackPhase3HealthPercent = 0.f;", DEMON_C)
        self.assertRegex(DEMON_C, r"GetPhase\(\)\s*==\s*ENarisBossPhase::Phase1")

    def test_delayed_attack_respects_line_of_sight(self):
        self.assertIn("LineTraceSingleByChannel", DEMON_C)
        self.assertIn("ECC_Visibility", DEMON_C)
        self.assertIn("Hit.GetActor()", DEMON_C)
        self.assertRegex(DEMON_C, r"CommitAttackImpact\(PlayerPawn\)")

    def test_no_impact_during_transition_and_on_death(self):
        self.assertRegex(DEMON_C, r"IsEncounterComplete\(\)\s*\|\|\s*bEnraging")
        self.assertIn("ClearTimer(ImpactTimer)",DEMON_C)
        self.assertIn("CancelAttack();",DEMON_C)

    def test_bone_beast_attack_ids_unchanged(self):
        self.assertIn('RequestAttack(TEXT("ClawSweep"), Phase1AttackDamage)',BASE_C)
        self.assertIn('RequestAttack(TEXT("BoneCharge"), Phase2AttackDamage)',BASE_C)

if __name__=="__main__":
    unittest.main()
