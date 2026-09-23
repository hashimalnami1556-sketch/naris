from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class RuntimeSaveRecoveryContractTests(unittest.TestCase):
    def test_runtime_subsystem_autoloads_default_slot(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisRuntimeSubsystem.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisRuntimeSubsystem.cpp"
        )
        self.assertIn('DefaultAutoSaveSlot = TEXT("NARIS_Auto")', header)
        self.assertIn(
            "virtual void Initialize(FSubsystemCollectionBase& Collection) override",
            header,
        )
        self.assertIn("Super::Initialize(Collection)", source)
        self.assertIn("LoadState(DefaultAutoSaveSlot)", source)
        self.assertIn("BeginNewGame()", source)

    def test_progression_actors_use_same_autosave_slot(self) -> None:
        files = [
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisWaystone.h",
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisMemoryCrystal.h",
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisAshGate.h",
            "unreal/NARIS_W04/Source/NARIS_W04/Public/CelestialWolf.h",
            "unreal/NARIS_W04/Source/NARIS_W04/Public/BoneBeastBoss.h",
        ]
        for rel in files:
            self.assertIn('TEXT("NARIS_Auto")', read(rel), rel)


if __name__ == "__main__":
    unittest.main()
