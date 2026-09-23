from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class CelestialWolfCompanionContractTests(unittest.TestCase):
    def test_save_state_persists_unlocked_companions(self) -> None:
        types = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisGameplayTypes.h"
        )
        self.assertIn("TArray<FString> UnlockedCompanions", types)

    def test_runtime_unlocks_and_restores_companion(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisRuntimeSubsystem.cpp"
        )
        self.assertIn("State.UnlockedCompanions.AddUnique(CompanionId)", source)
        self.assertIn("State.UnlockedCompanions.Contains(CompanionId)", source)

    def test_wolf_requires_ash_gate_before_bond(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/CelestialWolf.cpp"
        )
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/CelestialWolf.h"
        )
        self.assertIn('RequiredGateId = TEXT("W04_AshGate")', header)
        self.assertIn("Runtime->IsGateUnlocked(RequiredGateId)", source)
        self.assertIn("Runtime->UnlockCompanion(CompanionId)", source)

    def test_wolf_follow_and_echo_link_require_bond(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/CelestialWolf.cpp"
        )
        self.assertIn("if (!bBonded)", source)
        self.assertIn("if (bBonded)", source)
        self.assertIn("Mode = ENarisWolfMode::EchoLink", source)
        self.assertIn(
            "if (!bBonded || Mode != ENarisWolfMode::Follow)",
            source,
        )

    def test_wolf_bond_autosaves_and_restores_on_begin_play(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/CelestialWolf.cpp"
        )
        self.assertIn("Runtime->IsCompanionUnlocked(CompanionId)", source)
        self.assertIn("Runtime->SaveState(AutoSaveSlot)", source)
        self.assertIn("OnBonded.Broadcast()", source)

    def test_manifest_records_companion_contract(self) -> None:
        manifest = json.loads(
            read(
                "unreal/NARIS_W04/Content/NARIS/W04/Data/"
                "W04_VerticalSliceManifest.json"
            )
        )
        self.assertIn("CelestialWolfBond", manifest.get("progression_beats", []))
        self.assertEqual(
            manifest["runtime_contracts"]["celestial_wolf_actor"],
            "ACelestialWolf",
        )
        self.assertEqual(
            manifest["runtime_contracts"]["celestial_wolf_requirement"],
            "W04_AshGate",
        )

    def test_gameplay_tags_cover_companion_and_echo_link(self) -> None:
        tags = read("unreal/NARIS_W04/Config/DefaultGameplayTags.ini")
        self.assertIn("Companion.CelestialWolf", tags)
        self.assertIn("Progression.W04.CelestialWolfBonded", tags)
        self.assertIn("Ability.CelestialWolf.EchoLink", tags)


if __name__ == "__main__":
    unittest.main()
