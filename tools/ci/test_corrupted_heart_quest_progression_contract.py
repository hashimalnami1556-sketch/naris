from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class CorruptedHeartQuestProgressionContractTests(unittest.TestCase):
    def test_save_state_persists_active_quest_and_steps(self) -> None:
        types = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisGameplayTypes.h"
        )
        self.assertIn("TArray<FString> ActiveQuests", types)
        self.assertIn("TMap<FString, int32> QuestSteps", types)
        self.assertIn("TArray<FString> CompletedQuests", types)

    def test_runtime_exposes_start_step_active_and_complete_apis(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisRuntimeSubsystem.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisRuntimeSubsystem.cpp"
        )
        for token in (
            "StartQuest",
            "SetQuestStep",
            "IsQuestActive",
            "GetQuestStep",
            "CompleteQuest",
            "IsQuestCompleted",
        ):
            self.assertIn(token, header)
            self.assertIn(token, source)
        self.assertIn("State.ActiveQuests.Remove(QuestId)", source)

    def test_corrupted_heart_advances_across_w04_beats(self) -> None:
        memory_h = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisMemoryCrystal.h"
        )
        memory_cpp = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisMemoryCrystal.cpp"
        )
        gate_h = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisAshGate.h"
        )
        gate_cpp = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisAshGate.cpp"
        )
        wolf_h = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/CelestialWolf.h"
        )
        wolf_cpp = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/CelestialWolf.cpp"
        )
        boss_h = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/BoneBeastBoss.h"
        )
        boss_cpp = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp"
        )

        for header, step in ((memory_h, 1), (gate_h, 2), (wolf_h, 3)):
            self.assertIn('QuestId = TEXT("Quest.W04.CorruptedHeart")', header)
            self.assertIn(f"QuestStep = {step}", header)

        self.assertIn("Runtime->StartQuest(QuestId, QuestStep)", memory_cpp)
        self.assertIn("Runtime->SetQuestStep(QuestId, QuestStep)", gate_cpp)
        self.assertIn("Runtime->SetQuestStep(QuestId, QuestStep)", wolf_cpp)
        self.assertIn(
            'FallbackQuestCompletionId = TEXT("Quest.W04.CorruptedHeart")',
            boss_h,
        )
        self.assertIn(
            "Runtime->SetQuestStep(QuestCompletionId.ToString(), 4)",
            boss_cpp,
        )
        self.assertIn(
            "Runtime->CompleteQuest(QuestCompletionId.ToString())",
            boss_cpp,
        )

    def test_runtime_smoke_verifies_all_four_steps_and_round_trip(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisRuntimeSmokeDirector.cpp"
        )
        for token in (
            "quest_step_1_memory",
            "quest_step_2_gate",
            "quest_step_3_wolf",
            "quest_step_4_complete",
            "QuestSteps.FindRef",
            "ActiveQuests.IsEmpty()",
            "save_load_round_trip",
        ):
            self.assertIn(token, source)

    def test_hud_displays_localized_corrupted_heart_objective(self) -> None:
        hud = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
        )
        for token in (
            "HUDQuestCorruptedHeart",
            "HUDQuestCorruptedHeartStep1",
            "HUDQuestCorruptedHeartStep2",
            "HUDQuestCorruptedHeartStep3",
            "HUDQuestCorruptedHeartComplete",
            "Runtime->GetQuestStep(QuestId)",
        ):
            self.assertIn(token, hud)

        en = read(
            "unreal/NARIS_W04/Content/Localization/NARIS_Game/en/NARIS_Game.po"
        )
        ar = read(
            "unreal/NARIS_W04/Content/Localization/NARIS_Game/ar/NARIS_Game.po"
        )
        for key in (
            "HUDQuestCorruptedHeart",
            "HUDQuestCorruptedHeartStep1",
            "HUDQuestCorruptedHeartStep2",
            "HUDQuestCorruptedHeartStep3",
            "HUDQuestCorruptedHeartComplete",
        ):
            self.assertIn(f'msgctxt "NARIS,{key}"', en)
            self.assertIn(f'msgctxt "NARIS,{key}"', ar)


if __name__ == "__main__":
    unittest.main()
