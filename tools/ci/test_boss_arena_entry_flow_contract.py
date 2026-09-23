from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class BossArenaEntryFlowContractTests(unittest.TestCase):
    def test_arena_exposes_player_overlap_trigger(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisBossArenaController.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisBossArenaController.cpp"
        )
        self.assertIn("EncounterTrigger", header)
        self.assertIn("HandleEncounterOverlap", header)
        self.assertIn(
            'CreateDefaultSubobject<UBoxComponent>(TEXT("EncounterTrigger"))',
            source,
        )
        self.assertIn("ECR_Overlap", source)
        self.assertIn("OnComponentBeginOverlap.AddDynamic", source)

    def test_only_local_player_can_auto_start_boss(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisBossArenaController.cpp"
        )
        self.assertIn("UGameplayStatics::GetPlayerPawn(this, 0)", source)
        self.assertIn("OtherActor != PlayerPawn", source)
        self.assertIn("Boss->TryStartEncounter(OtherActor)", source)

    def test_trigger_stops_after_start_or_completed_encounter(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisBossArenaController.cpp"
        )
        self.assertIn("Boss->IsEncounterActive()", source)
        self.assertIn("Boss->IsEncounterComplete()", source)
        self.assertIn(
            "EncounterTrigger->SetCollisionEnabled(ECollisionEnabled::NoCollision)",
            source,
        )

    def test_arena_entry_emits_presentation_cue(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisBossArenaController.cpp"
        )
        self.assertIn('OnArenaEvent.Broadcast(TEXT("Arena.Enter"))', source)
        self.assertIn('Presentation->TriggerCue(TEXT("Arena.Enter"))', source)

        manifest = json.loads(
            read(
                "unreal/NARIS_W04/Content/NARIS/W04/Presentation/"
                "W04_PresentationCueManifest.json"
            )
        )
        cue_ids = {item["cue"] for item in manifest.get("cues", [])}
        self.assertIn("Arena.Enter", cue_ids)


if __name__ == "__main__":
    unittest.main()
