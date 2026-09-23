from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class BossAutonomousAttackContractTests(unittest.TestCase):
    def test_boss_ticks_only_when_encounter_is_attackable(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp"
        )
        self.assertIn("PrimaryActorTick.bCanEverTick = true", source)
        self.assertIn("void ABoneBeastBoss::Tick(float DeltaSeconds)", source)
        self.assertIn("!bEncounterActive", source)
        self.assertIn("bEncounterComplete", source)
        self.assertIn("!PendingAttackId.IsNone()", source)

    def test_boss_requires_player_in_range_and_cadence(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp"
        )
        self.assertIn("UGameplayStatics::GetPlayerPawn(this, 0)", source)
        self.assertIn("FMath::Square(FMath::Max(AttackRange, 1.f))", source)
        self.assertIn("AttackIntervalSeconds", source)
        self.assertIn("RequestPhaseAttack()", source)

    def test_phase_attack_ids_remain_authoritative(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp"
        )
        for token in ("ClawSweep", "BoneCharge", "AshRupture"):
            self.assertIn(token, source)

    def test_smoke_impact_reuses_damage_pipeline(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/BoneBeastBoss.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp"
        )
        self.assertIn("bImmediateSmokeAttackImpact", header)
        self.assertIn("CommitAttackImpact(PlayerPawn)", source)
        self.assertIn("UGameplayStatics::ApplyDamage", source)

    def test_production_impact_notify_uses_same_commit_path(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "BoneBeastAttackImpactNotify.cpp"
        )
        self.assertIn("Boss->CommitAttackImpact(Target)", source)


if __name__ == "__main__":
    unittest.main()
