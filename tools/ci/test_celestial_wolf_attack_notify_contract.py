from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class CelestialWolfAttackNotifyContractTests(unittest.TestCase):
    def test_wolf_attack_requests_animation_before_damage(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/CelestialWolf.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/CelestialWolf.cpp"
        )
        for token in (
            "bImmediateSmokeAttackImpact",
            "OnAttackRequested",
            "CommitAttackImpact",
            "CancelAttack",
            "PendingAttackTarget",
        ):
            self.assertIn(token, header)

        self.assertIn("RequestAttack(Target)", source)
        self.assertIn("OnAttackRequested()", source)
        self.assertIn("PendingAttackTarget = Target", source)

    def test_damage_occurs_only_in_commit_path(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/CelestialWolf.cpp"
        )
        commit_index = source.index("bool ACelestialWolf::CommitAttackImpact()")
        damage_index = source.index("Target->ApplyDamageToEncounter(AttackDamage)")
        self.assertGreater(damage_index, commit_index)
        self.assertIn("CancelAttack()", source)

    def test_smoke_fallback_uses_same_commit_path(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/CelestialWolf.cpp"
        )
        self.assertIn("if (bImmediateSmokeAttackImpact)", source)
        self.assertIn("return CommitAttackImpact()", source)

    def test_native_anim_notify_commits_wolf_impact(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisWolfAttackImpactNotify.cpp"
        )
        self.assertIn("Wolf->CommitAttackImpact()", source)
        self.assertIn("FAnimNotifyEventReference", source)

    def test_pending_target_is_transient_object_reference(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/CelestialWolf.h"
        )
        self.assertIn("UPROPERTY(Transient)", header)
        self.assertIn("TObjectPtr<ABoneBeastBoss> PendingAttackTarget", header)


if __name__ == "__main__":
    unittest.main()
