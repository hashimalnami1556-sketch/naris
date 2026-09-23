from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class WaystoneInteractionContractTests(unittest.TestCase):
    def test_interaction_interface_is_required_before_dispatch(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisInteractionComponent.cpp"
        )
        self.assertIn(
            "ImplementsInterface(UNarisInteractable::StaticClass())",
            source,
        )
        self.assertIn(
            "INarisInteractable::Execute_Interact",
            source,
        )

    def test_waystone_updates_runtime_and_autosaves(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisWaystone.cpp"
        )
        self.assertIn("Runtime->ActivateWaystone", source)
        self.assertIn("Runtime->SaveState(AutoSaveSlot)", source)
        self.assertIn("OnActivated.Broadcast()", source)

    def test_runtime_records_checkpoint_and_unlock(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisRuntimeSubsystem.cpp"
        )
        self.assertIn("State.CheckpointId = CheckpointId", source)
        self.assertIn("State.MapId = MapId", source)
        self.assertIn("State.UnlockedWaystones.AddUnique(WaystoneId)", source)

    def test_hero_input_chain_reaches_interaction_component(self) -> None:
        hero = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        input_ini = read("unreal/NARIS_W04/Config/DefaultInput.ini")

        self.assertIn('BindAction(TEXT("Interact")', hero)
        self.assertIn("Interaction->Interact()", hero)
        self.assertIn(
            '+ActionMappings=(ActionName="Interact",Key=(KeyName="E"))',
            input_ini,
        )

    def test_waystone_uses_registered_asset_identity(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisWaystone.h"
        )
        self.assertIn("NARIS-W04-PRP-WAYSTONE-0001", header)
        self.assertIn("W04_Waystone_0001", header)


if __name__ == "__main__":
    unittest.main()
