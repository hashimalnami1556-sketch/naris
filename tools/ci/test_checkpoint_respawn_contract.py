from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class CheckpointRespawnContractTests(unittest.TestCase):
    def test_save_state_persists_checkpoint_location(self) -> None:
        types = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisGameplayTypes.h"
        )
        self.assertIn("FVector CheckpointLocation", types)
        self.assertIn("bool bHasCheckpointLocation = false", types)

    def test_waystone_stores_world_location_before_autosave(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisWaystone.cpp"
        )
        activate_index = source.index("Runtime->ActivateWaystone")
        location_index = source.index("Runtime->SetCheckpointLocation(GetActorLocation())")
        save_index = source.index("Runtime->SaveState(AutoSaveSlot)")
        self.assertLess(activate_index, location_index)
        self.assertLess(location_index, save_index)

    def test_runtime_validates_and_stores_checkpoint_location(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisRuntimeSubsystem.cpp"
        )
        self.assertIn("WorldLocation.ContainsNaN()", source)
        self.assertIn("State.CheckpointLocation = WorldLocation", source)
        self.assertIn("State.bHasCheckpointLocation = true", source)

    def test_hero_death_schedules_checkpoint_respawn(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisHeroCharacter.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        for token in (
            "RespawnDelaySeconds",
            "CheckpointRespawnZOffset",
            "RespawnAtCheckpoint",
            "HandleDeath",
            "bDeathHandled",
        ):
            self.assertIn(token, header)
        self.assertIn("GetWorldTimerManager().SetTimer", source)
        self.assertIn("&ANarisHeroCharacter::RespawnAtCheckpoint", source)

    def test_respawn_restores_location_stats_movement_and_input(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        for token in (
            "State.bHasCheckpointLocation",
            "State.CheckpointLocation",
            "CheckpointRespawnZOffset",
            "Combat->Health = Combat->MaxHealth",
            "Combat->Poise = Combat->MaxPoise",
            "Combat->ClearDefenseWindows()",
            "Energy->Energy = Energy->MaxEnergy",
            "SetMovementMode(MOVE_Walking)",
            "EnableInput(PlayerController)",
        ):
            self.assertIn(token, source)

    def test_runtime_smoke_verifies_checkpoint_round_trip(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/"
            "NarisRuntimeSmokeDirector.cpp"
        )
        self.assertIn("checkpoint_location_saved", source)
        self.assertIn("CheckpointLocation.Equals", source)
        self.assertIn("!Cleared.bHasCheckpointLocation", source)


if __name__ == "__main__":
    unittest.main()
