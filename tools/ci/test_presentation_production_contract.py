from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class PresentationProductionContractTests(unittest.TestCase):
    def test_module_enables_niagara(self) -> None:
        build = read("unreal/NARIS_W04/Source/NARIS_W04/NARIS_W04.Build.cs")
        self.assertIn('"Niagara"', build)

    def test_presentation_bus_supports_vfx_audio_camera_and_blueprint_cues(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisPresentationComponent.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPresentationComponent.cpp"
        )
        for token in (
            "UNiagaraSystem",
            "USoundBase",
            "UCameraShakeBase",
            "OnCueTriggered",
            "TriggerCueAtLocation",
        ):
            self.assertIn(token, header)
        self.assertIn("UNiagaraFunctionLibrary::SpawnSystemAtLocation", source)
        self.assertIn("UGameplayStatics::PlaySoundAtLocation", source)
        self.assertIn("UGameplayStatics::PlayWorldCameraShake", source)

    def test_hero_emits_combat_feedback_cues(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        for cue in (
            "Hero.Evade",
            "Hero.ParrySuccess",
            "Hero.HitReact",
            "Hero.AttackHit.Light",
            "Hero.AttackHit.Heavy",
            "Hero.Dodge",
            "Hero.ParryWindow",
            "Hero.ResonanceBurst",
            "Hero.EssenceSwitch",
        ):
            self.assertIn(cue, source)

    def test_wolf_implements_all_five_modes(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/CelestialWolf.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/CelestialWolf.cpp"
        )
        for mode in ("Follow", "Guard", "Attack", "Track", "EchoLink"):
            self.assertIn(mode, header)
        for token in (
            "TickFollow()",
            "TickGuard()",
            "TickAttack()",
            "TickTrack()",
            "TickEchoLink()",
            "Target->ApplyDamageToEncounter(AttackDamage)",
            "Wolf.AttackImpact",
            "Wolf.EchoLink.Pulse",
        ):
            self.assertIn(token, source)

    def test_bone_beast_has_attack_phase_and_presentation_hooks(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/BoneBeastBoss.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp"
        )
        for token in (
            "CombatPresentation",
            "PhasePresentation",
            "Presentation",
            "RequestAttack",
            "CommitAttackImpact",
            "CancelAttack",
        ):
            self.assertIn(token, header)
        self.assertIn("CombatPresentation->StartAttack(AttackId)", source)
        self.assertIn("UGameplayStatics::ApplyDamage", source)
        self.assertIn("PhasePresentation->SetAuthoritativePhase", source)
        self.assertIn('TEXT("Boss.%s")', source)

    def test_bone_beast_delegate_name_does_not_collide_with_general_combat(self) -> None:
        boss_header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/BoneBeastCombatComponent.h"
        )
        hero_header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisCombatComponent.h"
        )
        self.assertIn("FNarisBoneBeastCombatEvent", boss_header)
        self.assertIn("FNarisCombatEvent", hero_header)
        self.assertNotIn(
            "DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FNarisCombatEvent",
            boss_header,
        )

    def test_arena_closes_and_opens_from_boss_events(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisBossArenaController.cpp"
        )
        self.assertIn('EventName == TEXT("EncounterStarted")', source)
        self.assertIn("SetArenaClosed(true)", source)
        self.assertIn('EventName == TEXT("EncounterComplete")', source)
        self.assertIn("SetArenaClosed(false)", source)
        for cue in (
            "Arena.Lock",
            "Arena.Unlock",
            "Arena.PhaseTransition",
            "Arena.BossDeath",
            "Arena.DemoEnd",
        ):
            self.assertIn(cue, source)

    def test_bootstrap_spawns_and_binds_arena_controller(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/naris_bootstrap_w04_smoke.py"
        )
        self.assertIn("NARIS_BossArenaController", source)
        self.assertIn('require_unreal_class("NarisBossArenaController")', source)
        self.assertIn('arena_controller.set_editor_property("boss", bone_beast)', source)

    def test_runtime_smoke_checks_arena_lock_cycle(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisRuntimeSmokeDirector.cpp"
        )
        self.assertIn("arena_closed_on_encounter", source)
        self.assertIn("arena_open_after_completion", source)


if __name__ == "__main__":
    unittest.main()
