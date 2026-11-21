"""ANIM-024: real Boss multiplayer authority and state replication source contracts.
A GREEN unittest is not a substitute for UE Game/Editor builds or real clients.
"""
import re
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[2] / "unreal/NARIS_W04/Source/NARIS_W04"
H = (BASE / "Public/BoneBeastBoss.h").read_text(encoding="utf8")
CPP = (BASE / "Private/BoneBeastBoss.cpp").read_text(encoding="utf8")


def body(classname: str, method: str) -> str:
    pattern = r"\b" + re.escape(classname) + "::" + re.escape(method) + r"\s*\("
    match = re.search(pattern, CPP)
    if not match:
        raise AssertionError(f"Missing {classname}::{method}")
    start = CPP.find("{", match.end())
    if start < 0:
        raise AssertionError(f"No body for {method}")
    depth = 0
    for i in range(start, len(CPP)):
        if CPP[i] == "{":
            depth += 1
        elif CPP[i] == "}":
            depth -= 1
            if depth == 0:
                return CPP[start:i + 1]
    raise AssertionError(f"No matching brace for {method}")


class BossNetworkAuthority(unittest.TestCase):
    def test_health_and_phase_replicated_with_client_notifications(self):
        self.assertRegex(H, r"UPROPERTY\(ReplicatedUsing=OnRep_CurrentHealth[^)]*\)\s*float\s+CurrentHealth")
        self.assertRegex(H, r"UPROPERTY\(ReplicatedUsing=OnRep_CurrentPhase[^)]*\)\s*ENarisBossPhase\s+CurrentPhase")
        self.assertIn("GetLifetimeReplicatedProps", H)
        for member in ("CurrentHealth", "CurrentPhase", "bEncounterActive", "bEncounterComplete"):
            with self.subTest(member=member):
                self.assertIn("DOREPLIFETIME(ABoneBeastBoss, " + member + ");", CPP)
        self.assertIn("void ABoneBeastBoss::OnRep_CurrentHealth()", CPP)
        self.assertIn("void ABoneBeastBoss::OnRep_CurrentPhase()", CPP)

    def test_boss_encounter_state_fields_replicated(self):
        self.assertRegex(H, r"UPROPERTY\(Replicated[^)]*\)\s*bool\s+bEncounterActive")
        self.assertRegex(H, r"UPROPERTY\(Replicated[^)]*\)\s*bool\s+bEncounterComplete")

    def test_all_boss_damage_and_quest_mutations_are_server_only(self):
        for method in ("BeginPlay", "Tick", "StartEncounter", "ResetEncounter", "ApplyDamageToEncounter",
                       "CompleteEncounter", "RequestAttack", "CommitAttackImpact", "TryStartEncounter", "CancelAttack"):
            with self.subTest(method=method):
                self.assertIn("HasAuthority()", body("ABoneBeastBoss", method))

    def test_boss_client_does_not_read_local_defeat_save_in_beginplay(self):
        src = body("ABoneBeastBoss", "BeginPlay")
        self.assertLess(src.index("if (!HasAuthority())"), src.index("IsBossDefeated("))

    def test_boss_damage_mutation_happens_only_after_authority_check(self):
        src = body("ABoneBeastBoss", "ApplyDamageToEncounter")
        self.assertLess(src.index("if (!HasAuthority())"), src.index("CurrentHealth = FMath::Max("))

    def test_nonshipping_qa_hp_probe_tracks_real_server_and_client_snapshots(self):
        init = body("ABoneBeastBoss", "BeginPlay")
        tick = body("ABoneBeastBoss", "Tick")
        self.assertIn("#if !UE_BUILD_SHIPPING", init)
        self.assertIn("NarisBossNetProbe", init)
        self.assertIn("NarisBossNetProbe", tick)
        self.assertIn("NARIS_BOSS_NET_PROBE", tick)
        self.assertIn("ApplyDamageToEncounter(", tick)
        self.assertIn("OnRep_CurrentHealth", CPP)
        self.assertIn("NARIS_BOSS_NET_PROBE", body("ABoneBeastBoss", "OnRep_CurrentHealth"))

    def test_qa_combat_does_not_mark_boss_defeated_or_autosave(self):
        init = body("ABoneBeastBoss", "BeginPlay")
        self.assertIn("NarisBossNetProbe", init)
        self.assertIn("return;", init)
        tick = body("ABoneBeastBoss", "Tick")
        self.assertIn("ApplyDamageToEncounter(", tick)
        self.assertIn("bBossNetProbeApplied", H)


if __name__ == "__main__":
    unittest.main()
