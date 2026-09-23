from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PLAN = (
    ROOT
    / "unreal"
    / "NARIS_W04"
    / "Content"
    / "NARIS"
    / "W04"
    / "Presentation"
    / "W04_PresentationSourcePlan.json"
)


class PresentationSFXGenerationPlanContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = json.loads(PLAN.read_text(encoding="utf-8"))
        cls.audio = [
            item
            for item in cls.plan.get("assets", [])
            if item.get("kind") == "audio"
        ]

    def test_all_sixteen_audio_payloads_have_generation_contracts(self) -> None:
        self.assertEqual(len(self.audio), 16)
        for item in self.audio:
            contract = item.get("generation_contract")
            self.assertIsInstance(contract, dict, item["asset_id"])
            self.assertEqual(
                contract.get("provider_model"),
                "sfx/elevenlabs-sound-v2",
            )
            self.assertTrue(contract.get("prompt"))
            self.assertLessEqual(len(contract["prompt"]), 450)
            self.assertFalse(contract.get("loop"))
            self.assertEqual(contract.get("output_format"), "pcm_48000")
            self.assertGreater(contract.get("prompt_influence", 0), 0)
            self.assertLessEqual(contract.get("prompt_influence", 0), 1)

    def test_generation_duration_matches_audio_source_contract(self) -> None:
        for item in self.audio:
            self.assertEqual(
                item["generation_contract"]["duration_seconds"],
                item["source_contract"]["target_duration_seconds"],
                item["asset_id"],
            )

    def test_generation_plan_does_not_claim_sources_exist(self) -> None:
        for item in self.audio:
            self.assertEqual(item.get("status"), "required")
            self.assertIsNone(item.get("unreal_object_path"))
            self.assertIn(
                "Generation spends external credits",
                item["generation_contract"]["note"],
            )


if __name__ == "__main__":
    unittest.main()
