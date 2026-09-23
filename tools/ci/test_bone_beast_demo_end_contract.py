from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class BoneBeastDemoEndContractTests(unittest.TestCase):
    def test_legacy_bone_beast_path_is_removed(self) -> None:
        for rel in (
            "unreal/NARIS_W04/Source/NARIS_W04/Public/BoneBeast.h",
            "unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeast.cpp",
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisBossPhaseComponent.h",
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisBossPhaseComponent.cpp",
        ):
            self.assertFalse((ROOT / rel).exists(), rel)

    def test_save_state_persists_boss_and_demo_completion(self) -> None:
        types = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisGameplayTypes.h"
        )
        self.assertIn("TArray<FString> DefeatedBosses", types)
        self.assertIn("bool bDemoCompleted = false", types)

    def test_runtime_tracks_quest_boss_and_demo_state(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisRuntimeSubsystem.cpp"
        )
        for token in (
            "State.CompletedQuests.AddUnique(QuestId)",
            "State.DefeatedBosses.AddUnique(BossId)",
            "State.DefeatedBosses.Contains(BossId)",
            "State.bDemoCompleted = true",
        ):
            self.assertIn(token, source)

    def test_boss_requires_celestial_wolf(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/BoneBeastBoss.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp"
        )
        self.assertIn(
            'RequiredCompanionId = TEXT("CelestialWolf")',
            header,
        )
        self.assertIn(
            "Runtime->IsCompanionUnlocked(RequiredCompanionId)",
            source,
        )
        self.assertIn('EmitBossEvent(TEXT("EncounterLocked"))', source)

    def test_death_completes_encounter_and_demo(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp"
        )
        self.assertIn("CompleteEncounter();", source)
        self.assertIn("Runtime->MarkBossDefeated(BossProgressId)", source)
        self.assertIn("Runtime->CompleteQuest", source)
        self.assertIn("Runtime->CompleteDemo()", source)
        self.assertIn('EmitBossEvent(TEXT("EncounterComplete"))', source)
        self.assertIn('EmitBossEvent(TEXT("DemoEnd"))', source)

    def test_autosave_failure_does_not_revert_completion(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp"
        )
        complete_index = source.index("bEncounterComplete = true")
        save_index = source.rindex("Runtime->SaveState(AutoSaveSlot)")
        self.assertLess(complete_index, save_index)

    def test_manifest_registry_and_tags_cover_demo_end(self) -> None:
        registry = json.loads(read("data/MASTER_ASSET_REGISTRY.json"))
        ids = {
            item["id"]
            for item in registry.get("assets", [])
            if isinstance(item, dict) and "id" in item
        }
        self.assertIn("NARIS-W04-ENM-BONEBEAST-0001", ids)
        self.assertIn("NARIS-W04-QST-DEMOEND-0001", ids)

        manifest = json.loads(
            read(
                "unreal/NARIS_W04/Content/NARIS/W04/Data/"
                "W04_VerticalSliceManifest.json"
            )
        )
        for beat in ("BoneBeastEncounter", "BoneBeastDefeat", "DemoEnd"):
            self.assertIn(beat, manifest.get("progression_beats", []))
        self.assertEqual(
            manifest["runtime_contracts"]["bone_beast_actor"],
            "ABoneBeastBoss",
        )
        self.assertEqual(
            manifest["runtime_contracts"]["bone_beast_requirement"],
            "CelestialWolf",
        )
        self.assertFalse(manifest["release"]["public_demo_allowed"])

        tags = read("unreal/NARIS_W04/Config/DefaultGameplayTags.ini")
        self.assertIn("Progression.W04.BoneBeastDefeated", tags)
        self.assertIn("Progression.W04.DemoCompleted", tags)
        self.assertIn("Quest.W04.DemoEnd", tags)


if __name__ == "__main__":
    unittest.main()
