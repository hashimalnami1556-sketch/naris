from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class MemoryCrystalNarrativeContractTests(unittest.TestCase):
    def test_save_state_persists_narrative_ids(self) -> None:
        types = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisGameplayTypes.h"
        )
        self.assertIn("TArray<FString> TriggeredNarratives", types)

    def test_runtime_unlocks_lore_and_tracks_first_whisper(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisRuntimeSubsystem.cpp"
        )
        self.assertIn("State.UnlockedLore.AddUnique(LoreId)", source)
        self.assertIn("State.TriggeredNarratives.AddUnique(NarrativeId)", source)
        self.assertIn("State.TriggeredNarratives.Contains(NarrativeId)", source)

    def test_memory_crystal_triggers_narrative_and_autosave(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisMemoryCrystal.cpp"
        )
        self.assertIn("Runtime->UnlockLore(LoreId)", source)
        self.assertIn("Runtime->TriggerNarrative(NarrativeId)", source)
        self.assertIn("Runtime->HasNarrativeTriggered(NarrativeId)", source)
        self.assertIn("Runtime->SaveState(AutoSaveSlot)", source)

    def test_memory_crystal_and_first_whisper_are_registered(self) -> None:
        registry = json.loads(
            read("data/MASTER_ASSET_REGISTRY.json")
        )
        by_id = {
            item["id"]: item
            for item in registry.get("assets", [])
            if isinstance(item, dict) and "id" in item
        }

        memory_id = "NARIS-W04-PRP-MEMORYCRYSTAL-0001"
        whisper_id = "NARIS-W04-QST-FIRSTWHISPER-0001"
        self.assertIn(memory_id, by_id)
        self.assertIn(whisper_id, by_id)
        self.assertEqual(by_id[memory_id]["world"], "W04")
        self.assertEqual(by_id[whisper_id]["world"], "W04")

    def test_gameplay_tags_cover_interactable_and_narrative(self) -> None:
        tags = read("unreal/NARIS_W04/Config/DefaultGameplayTags.ini")
        for tag in (
            "Interactable.MemoryCrystal",
            "Narrative.W04.FirstWhisper",
            "Quest.W04.MemoryCrystal",
        ):
            self.assertIn(tag, tags)


if __name__ == "__main__":
    unittest.main()
