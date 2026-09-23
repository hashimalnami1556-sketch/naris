from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = (
    ROOT
    / "unreal"
    / "NARIS_W04"
    / "Content"
    / "NARIS"
    / "W04"
    / "Presentation"
    / "W04_PresentationCueManifest.json"
)
PLAN = MANIFEST.with_name("W04_PresentationSourcePlan.json")


class HeroDeathPresentationContractTests(unittest.TestCase):
    def test_hero_emits_death_and_respawn_cues(self) -> None:
        source = (
            ROOT
            / "unreal"
            / "NARIS_W04"
            / "Source"
            / "NARIS_W04"
            / "Private"
            / "NarisHeroCharacter.cpp"
        ).read_text(encoding="utf-8")
        self.assertIn('Presentation->TriggerCue(TEXT("Hero.Death"))', source)
        self.assertIn('Presentation->TriggerCue(TEXT("Hero.Respawn"))', source)

        death_index = source.index('Presentation->TriggerCue(TEXT("Hero.Death"))')
        timer_index = source.index("GetWorldTimerManager().SetTimer")
        self.assertLess(death_index, timer_index)

        respawn_index = source.index('Presentation->TriggerCue(TEXT("Hero.Respawn"))')
        enable_index = source.index("EnableInput(PlayerController)")
        self.assertGreater(respawn_index, enable_index)

    def test_death_reuses_registered_native_death_shake(self) -> None:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        by_cue = {item["cue"]: item for item in manifest.get("cues", [])}
        self.assertEqual(
            by_cue["Hero.Death"]["camera"],
            "NARIS-W04-CINE-SHAKEDEATH-0001",
        )
        self.assertIn("Hero.Respawn", by_cue)
        self.assertEqual(
            set(by_cue["Hero.Respawn"].keys()),
            {"cue"},
        )

    def test_source_plan_tracks_shared_death_camera_usage(self) -> None:
        plan = json.loads(PLAN.read_text(encoding="utf-8"))
        item = next(
            asset
            for asset in plan["assets"]
            if asset["asset_id"] == "NARIS-W04-CINE-SHAKEDEATH-0001"
        )
        self.assertEqual(item["status"], "bound")
        self.assertIn("Boss.Death", item["used_by_cues"])
        self.assertIn("Hero.Death", item["used_by_cues"])


if __name__ == "__main__":
    unittest.main()
