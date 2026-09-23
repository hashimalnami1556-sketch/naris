from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class NarisHudContractTests(unittest.TestCase):
    def test_game_mode_uses_native_smoke_hud(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisGameMode.cpp"
        )
        self.assertIn('#include "NarisHUD.h"', source)
        self.assertIn("HUDClass = ANarisHUD::StaticClass()", source)

    def test_hud_exposes_core_combat_status(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
        )
        for token in (
            "Hero->Combat->Health",
            "Hero->Combat->Resonance",
            "Hero->Energy->Energy",
            "Boss->GetCurrentHealth()",
        ):
            self.assertIn(token, source)

    def test_hud_uses_interactable_prompt_contract(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
        )
        self.assertIn("FindNearestInteractable()", source)
        self.assertIn("INarisInteractable::Execute_GetInteractionPrompt", source)
        self.assertIn('GetActionKeyDisplayName(TEXT("Interact"))', source)
        self.assertIn('TEXT("[%s] %s")', source)

    def test_hud_exposes_progression_state(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
        )
        self.assertIn('IsCompanionUnlocked(TEXT("CelestialWolf"))', source)
        self.assertIn("IsDemoCompleted()", source)
        self.assertIn("W04 DEMO COMPLETE", source)

    def test_hud_is_localization_ready_at_source_level(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
        )
        self.assertIn("NSLOCTEXT", source)


if __name__ == "__main__":
    unittest.main()
