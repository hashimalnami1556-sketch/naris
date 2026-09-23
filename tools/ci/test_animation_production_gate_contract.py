from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "data" / "MASTER_ASSET_REGISTRY.json"
BINDINGS = (
    ROOT
    / "unreal"
    / "NARIS_W04"
    / "Content"
    / "NARIS"
    / "W04"
    / "Animation"
    / "W04_AnimationBindings.json"
)


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class AnimationProductionGateContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.bindings = json.loads(BINDINGS.read_text(encoding="utf-8"))

    def test_manifest_registers_ten_required_w04_montages(self) -> None:
        assets = self.bindings.get("assets", [])
        self.assertEqual(
            self.bindings.get("schema"),
            "naris.w04.animation-bindings.v1",
        )
        self.assertEqual(len(assets), 10)

        registry_ids = {
            item.get("id")
            for item in self.registry.get("assets", [])
            if isinstance(item, dict)
        }
        for item in assets:
            self.assertIn(item["asset_id"], registry_ids)
            self.assertEqual(item["expected_class"], "AnimMontage")
            self.assertTrue(
                item["expected_unreal_object_path"].startswith(
                    "/Game/NARIS/W04/"
                )
            )

    def test_attack_montages_require_native_gameplay_notifies(self) -> None:
        by_role = {
            item["role"]: item
            for item in self.bindings.get("assets", [])
        }

        for role in ("hero_light_attack", "hero_heavy_attack"):
            required = set(by_role[role]["required_notify_classes"])
            self.assertEqual(
                required,
                {"NarisAttackWindowNotifyState", "NarisAttackImpactNotify"},
            )
            self.assertEqual(
                by_role[role]["require_positive_state_duration"],
                ["NarisAttackWindowNotifyState"],
            )

        self.assertEqual(
            by_role["celestial_wolf_attack"]["required_notify_classes"],
            ["NarisWolfAttackImpactNotify"],
        )

        for role in (
            "bone_beast_claw_sweep",
            "bone_beast_bone_charge",
            "bone_beast_ash_rupture",
        ):
            self.assertEqual(
                by_role[role]["required_notify_classes"],
                ["BoneBeastAttackImpactNotify"],
            )

    def test_unreal_validator_checks_montage_type_notifies_and_state_duration(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/"
            "naris_validate_animation_bindings.py"
        )
        for token in (
            "unreal.AnimMontage",
            "unreal.AnimationLibrary.get_animation_notify_events",
            "event.get_editor_property(\"notify\")",
            "event.get_editor_property(\"notify_state_class\")",
            "unreal.AnimationLibrary.get_anim_notify_event_duration",
            "missing required notifies",
            "notify states require positive duration",
            "NARIS_ANIMATION_STRICT",
            "naris_animation_validation.json",
        ):
            self.assertIn(token, source)

    def test_bootstrap_runs_animation_validation_before_presentation_intake(self) -> None:
        source = read("tools/windows/Invoke-NarisW04AuthoringBootstrap.ps1")
        validation_index = source.index(
            "[NARIS] Validating production animation bindings and notifies"
        )
        audio_index = source.index(
            "[NARIS] Importing validated presentation WAV sources"
        )
        self.assertLess(validation_index, audio_index)
        self.assertIn("naris_validate_animation_bindings.py", source)

    def test_development_package_archives_animation_report(self) -> None:
        source = read("tools/windows/Invoke-NarisWindowsPackage.ps1")
        for token in (
            "naris_animation_validation.json",
            "animation_validation_status",
            "animation_validated_asset_ids",
            "animation_unresolved_asset_ids",
        ):
            self.assertIn(token, source)

    def test_shipping_rc_requires_strict_zero_unresolved_animations(self) -> None:
        source = read("tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1")
        for token in (
            'NARIS_ANIMATION_STRICT = "1"',
            "Strict animation validation did not pass",
            "Release candidate has unresolved production animations",
            "Release candidate animation validation contains errors",
            "animation_unresolved_count",
            "animation_error_count",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
