from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class AttackAnimationWindowContractTests(unittest.TestCase):
    def test_attack_kind_enum_supports_light_and_heavy(self) -> None:
        types = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisGameplayTypes.h"
        )
        self.assertIn("enum class ENarisAttackKind", types)
        self.assertIn("Light", types)
        self.assertIn("Heavy", types)

    def test_hero_exposes_animation_window_hooks_and_smoke_fallback(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisHeroCharacter.h"
        )
        for token in (
            "bImmediateSmokeAttackHit",
            "OpenAttackHitWindow",
            "CloseAttackHitWindow",
            "CommitPendingAttackHit",
            "CancelPendingAttack",
            "OnAttackRequested",
            "PendingAttack",
            "bAttackHitConsumed",
        ):
            self.assertIn(token, header)

    def test_attack_input_queues_kind_instead_of_direct_damage(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        self.assertIn(
            "QueueAttack(ENarisAttackKind::Light)",
            source,
        )
        self.assertIn(
            "QueueAttack(ENarisAttackKind::Heavy)",
            source,
        )
        self.assertIn("OnAttackRequested(AttackKind)", source)

    def test_smoke_fallback_runs_same_window_and_impact_path(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        fallback = (
            "if (bImmediateSmokeAttackHit)\n"
            "    {\n"
            "        OpenAttackHitWindow();\n"
            "        CommitPendingAttackHit();\n"
            "        CloseAttackHitWindow();"
        )
        self.assertIn(fallback, source)

    def test_impact_is_single_consume_inside_open_window(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        for token in (
            "!bAttackHitWindowOpen",
            "bAttackHitConsumed",
            "bAttackHitConsumed = true",
            "ApplyAttackToLockedTarget(Damage, PoiseDamage)",
            "Combat->AddResonance(ResonanceReward)",
        ):
            self.assertIn(token, source)

    def test_notify_state_opens_and_closes_window(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisAttackWindowNotifyState.cpp"
        )
        self.assertIn("Hero->OpenAttackHitWindow()", source)
        self.assertIn("Hero->CloseAttackHitWindow()", source)
        self.assertIn("FAnimNotifyEventReference", source)

    def test_impact_notify_commits_pending_attack(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisAttackImpactNotify.cpp"
        )
        self.assertIn("Hero->CommitPendingAttackHit()", source)
        self.assertIn("FAnimNotifyEventReference", source)


if __name__ == "__main__":
    unittest.main()
