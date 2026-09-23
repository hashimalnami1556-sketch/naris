from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class PresentationProductionPassContractTests(unittest.TestCase):
    def test_wolf_exposes_five_modes_and_command_cycle(self) -> None:
        header = read("unreal/NARIS_W04/Source/NARIS_W04/Public/CelestialWolf.h")
        source = read("unreal/NARIS_W04/Source/NARIS_W04/Private/CelestialWolf.cpp")
        for token in ("Follow", "Guard", "Attack", "Track", "EchoLink"):
            self.assertIn(token, header)
        self.assertIn("void ACelestialWolf::CycleMode()", source)
        self.assertIn("GetModeDisplayName() const", source)

    def test_wolf_command_is_bound_for_keyboard_and_gamepad(self) -> None:
        ini = read("unreal/NARIS_W04/Config/DefaultInput.ini")
        hero = read("unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp")
        self.assertIn('ActionName="CompanionMode",Key=(KeyName="C")', ini)
        self.assertIn('ActionName="CompanionMode",Key=(KeyName="Gamepad_DPad_Up")', ini)
        self.assertIn('BindAction(TEXT("CompanionMode")', hero)
        self.assertIn("Wolf->CycleMode()", hero)

    def test_hud_exposes_localized_wolf_mode(self) -> None:
        hud = read("unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp")
        self.assertIn('"HUDWolfMode"', hud)
        self.assertIn("GetModeDisplayName()", hud)

    def test_bone_beast_requests_phase_specific_attacks(self) -> None:
        source = read("unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp")
        for token in ("ClawSweep", "BoneCharge", "AshRupture"):
            self.assertIn(token, source)
        self.assertIn("RequestPhaseAttack()", source)
        self.assertIn("Presentation->TriggerCue(", source)

    def test_bone_beast_impact_notify_commits_gameplay_damage(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "BoneBeastAttackImpactNotify.cpp"
        )
        self.assertIn("UGameplayStatics::GetPlayerPawn", source)
        self.assertIn("Boss->CommitAttackImpact(Target)", source)

    def test_presentation_component_owns_niagara_audio_and_camera_feedback(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisPresentationComponent.cpp"
        )
        for token in (
            "UNiagaraFunctionLibrary::SpawnSystemAtLocation",
            "UGameplayStatics::PlaySoundAtLocation",
            "UGameplayStatics::PlayWorldCameraShake",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
