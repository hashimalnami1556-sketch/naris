from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class RuntimeSmokeDirectorContractTests(unittest.TestCase):
    def test_module_has_json_dependency(self) -> None:
        build = read("unreal/NARIS_W04/Source/NARIS_W04/NARIS_W04.Build.cs")
        self.assertIn('"Json"', build)

    def test_bootstrap_spawns_runtime_smoke_director(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/naris_bootstrap_w04_smoke.py"
        )
        self.assertIn("NARIS_RuntimeSmokeDirector", source)
        self.assertIn('require_unreal_class("NarisRuntimeSmokeDirector")', source)

    def test_runtime_smoke_drives_real_progression_actors(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisRuntimeSmokeDirector.cpp"
        )
        for token in (
            "Waystone->ActivateWaystone(this)",
            "MemoryCrystal->ActivateMemory(this)",
            "AshGate->TryUnlockGate(this)",
            "Wolf->BondWithPlayer(this)",
            "BoneBeast->TryStartEncounter(this)",
            "BoneBeast->ApplyDamageToEncounter",
        ):
            self.assertIn(token, source)

    def test_runtime_smoke_checks_complete_progression_and_round_trip(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisRuntimeSmokeDirector.cpp"
        )
        for token in (
            'CheckpointId == TEXT("W04_Waystone_0001")',
            'UnlockedLore.Contains(TEXT("W04_Lore_MemoryCrystal_0001"))',
            'TriggeredNarratives.Contains(TEXT("W04_FirstWhisper"))',
            'UnlockedGates.Contains(TEXT("W04_AshGate"))',
            'UnlockedCompanions.Contains(TEXT("CelestialWolf"))',
            'CompletedQuests.Contains(TEXT("Quest.W04.CorruptedHeart"))',
            'DefeatedBosses.Contains(TEXT("BoneBeast"))',
            "bDemoCompleted",
            "Runtime->LoadState(RuntimeSmokeSlot)",
            "save_load_round_trip",
        ):
            self.assertIn(token, source)

    def test_runtime_smoke_uses_isolated_save_slot_and_json_report(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisRuntimeSmokeDirector.cpp"
        )
        self.assertIn('TEXT("NARIS_RuntimeSmoke")', source)
        self.assertIn("UGameplayStatics::DeleteGameInSlot", source)
        self.assertIn("naris.w04.runtime-smoke.v1", source)
        self.assertIn("FJsonSerializer::Serialize", source)
        self.assertIn("NarisSmokeReport=", source)

    def test_windows_package_requires_runtime_smoke_pass(self) -> None:
        source = read("tools/windows/Invoke-NarisWindowsPackage.ps1")
        for token in (
            "Runtime progression + save/load smoke",
            "-NarisRuntimeSmoke",
            "naris_runtime_smoke.json",
            "ConvertFrom-Json",
            '$RuntimeSmokeData.status -ne "pass"',
            "Runtime progression smoke PASSED",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
