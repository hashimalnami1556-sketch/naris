"""Non-shipping real C++ Wolf attack-flow -> Boss HP network probe contract.

This verifies wiring only. An actual packaged 1+2 runtime test is required.
No production Montage/collision/quest/SaveGame approval is inferred.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2] / "unreal/NARIS_W04/Source/NARIS_W04/Private"
WOLF = (ROOT / "CelestialWolf.cpp").read_text(encoding="utf8")
BOSS = (ROOT / "BoneBeastBoss.cpp").read_text(encoding="utf8")


def method_body(source, name):
    found = re.search(r"::" + re.escape(name) + r"\s*\(", source)
    if not found:
        raise AssertionError("Method missing: " + name)
    start = source.find("{", found.end())
    depth = 0
    for i in range(start, len(source)):
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
            if depth == 0:
                return source[start:i+1]
    raise AssertionError("Unclosed method " + name)


class WolfBossAttackFlowProbe(unittest.TestCase):
    def test_server_only_qa_wolf_attack_initializes_real_attack_mode(self):
        src = method_body(WOLF, "BeginPlay")
        self.assertIn("#if !UE_BUILD_SHIPPING", src)
        self.assertIn("NarisWolfNetProbeCombatOnce", src)
        self.assertIn("ENarisWolfMode::Attack", src)
        self.assertIn("AttackAcquireRadius", src)
        self.assertIn("ForceNetUpdate();", src)

    def test_qa_runs_real_wolf_attack_decision_and_impact_functions(self):
        attack = method_body(WOLF, "TickAttack")
        impact = method_body(WOLF, "CommitAttackImpact")
        self.assertIn("RequestAttack(Target);", attack)
        self.assertIn("HasAuthority()", impact)
        self.assertIn("Target->ApplyDamageToEncounter(AttackDamage)", impact)
        self.assertIn("NarisWolfNetProbeCombatOnce", impact)
        self.assertIn("NARIS_WOLF_COMBAT_PROBE", impact)
        self.assertIn("SetMode(ENarisWolfMode::Guard)", impact)

    def test_boss_qa_skips_previous_scheduled_direct_hit_only_when_opted_in(self):
        tick = method_body(BOSS, "Tick")
        self.assertIn("#if !UE_BUILD_SHIPPING", tick)
        self.assertIn("NarisBossNetProbeNoDamage", tick)
        self.assertIn("ApplyDamageToEncounter(18.f)", tick)
        self.assertIn("HasAuthority()", tick)

    def test_real_wolf_request_still_checks_active_boss_and_authority(self):
        request = method_body(WOLF, "RequestAttack")
        self.assertIn("!HasAuthority()", request)
        self.assertIn("!Target->IsEncounterActive()", request)
        self.assertIn("Target->IsEncounterComplete()", request)
        self.assertIn("return CommitAttackImpact();", request)

    def test_boss_qa_is_active_not_completed_and_autosave_disabled(self):
        begin = method_body(BOSS, "BeginPlay")
        self.assertIn("NarisBossNetProbe", begin)
        self.assertIn("bEncounterActive = true", begin)
        self.assertIn("bEncounterComplete = false", begin)
        self.assertIn("bAutoAttack = false", begin)
        self.assertIn("ForceNetUpdate()", begin)


if __name__ == "__main__":
    unittest.main()
