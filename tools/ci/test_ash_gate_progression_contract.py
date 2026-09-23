from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class AshGateProgressionContractTests(unittest.TestCase):
    def test_save_state_persists_unlocked_gates(self) -> None:
        types = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisGameplayTypes.h"
        )
        self.assertIn("TArray<FString> UnlockedGates", types)

    def test_runtime_can_unlock_and_restore_gate(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisRuntimeSubsystem.cpp"
        )
        self.assertIn("State.UnlockedGates.AddUnique(GateId)", source)
        self.assertIn("State.UnlockedGates.Contains(GateId)", source)

    def test_ash_gate_requires_first_whisper(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisAshGate.cpp"
        )
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisAshGate.h"
        )
        self.assertIn('RequiredNarrativeId = TEXT("W04_FirstWhisper")', header)
        self.assertIn(
            "Runtime->HasNarrativeTriggered(RequiredNarrativeId)",
            source,
        )
        self.assertIn("OnGateLocked.Broadcast()", source)

    def test_ash_gate_autosaves_and_disables_blocker(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisAshGate.cpp"
        )
        self.assertIn("Runtime->SaveState(AutoSaveSlot)", source)
        self.assertIn(
            "Blocker->SetCollisionEnabled(ECollisionEnabled::NoCollision)",
            source,
        )
        self.assertIn("Runtime->IsGateUnlocked(GateId)", source)

    def test_registry_and_manifest_include_ash_gate(self) -> None:
        registry = json.loads(read("data/MASTER_ASSET_REGISTRY.json"))
        ids = {
            item["id"]
            for item in registry.get("assets", [])
            if isinstance(item, dict) and "id" in item
        }
        self.assertIn("NARIS-W04-PRP-ASHGATE-0001", ids)

        manifest = json.loads(
            read(
                "unreal/NARIS_W04/Content/NARIS/W04/Data/"
                "W04_VerticalSliceManifest.json"
            )
        )
        self.assertIn("AshGate", manifest.get("interactables", []))
        self.assertEqual(
            manifest["runtime_contracts"]["ash_gate_requirement"],
            "W04_FirstWhisper",
        )

    def test_gameplay_tags_cover_gate_progression(self) -> None:
        tags = read("unreal/NARIS_W04/Config/DefaultGameplayTags.ini")
        self.assertIn("Interactable.AshGate", tags)
        self.assertIn("Progression.W04.AshGateUnlocked", tags)


if __name__ == "__main__":
    unittest.main()
