from __future__ import annotations

import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
BINDINGS = (
    ROOT
    / "unreal"
    / "NARIS_W04"
    / "Content"
    / "NARIS"
    / "W04"
    / "Presentation"
    / "W04_PresentationAssetBindings.json"
)


class NativeCameraShakeContractTests(unittest.TestCase):
    def test_gameplay_cameras_module_and_plugin_are_enabled(self) -> None:
        build = (
            ROOT
            / "unreal"
            / "NARIS_W04"
            / "Source"
            / "NARIS_W04"
            / "NARIS_W04.Build.cs"
        ).read_text(encoding="utf-8")
        self.assertIn('"GameplayCameras"', build)

        project = json.loads(
            (ROOT / "unreal" / "NARIS_W04" / "NARIS_W04.uproject").read_text(
                encoding="utf-8"
            )
        )
        enabled = {
            item.get("Name")
            for item in project.get("Plugins", [])
            if isinstance(item, dict) and item.get("Enabled") is True
        }
        self.assertIn("GameplayCameras", enabled)

    def test_native_camera_shake_classes_exist(self) -> None:
        header = (
            ROOT
            / "unreal"
            / "NARIS_W04"
            / "Source"
            / "NARIS_W04"
            / "Public"
            / "NarisCameraShakes.h"
        ).read_text(encoding="utf-8")
        source = (
            ROOT
            / "unreal"
            / "NARIS_W04"
            / "Source"
            / "NARIS_W04"
            / "Private"
            / "NarisCameraShakes.cpp"
        ).read_text(encoding="utf-8")

        for class_name in (
            "UNarisHitCameraShake",
            "UNarisHeavyCameraShake",
            "UNarisParryCameraShake",
            "UNarisPhaseCameraShake",
            "UNarisDeathCameraShake",
        ):
            self.assertIn(class_name, header)
            self.assertIn(f"{class_name}::{class_name}", source)

        for token in (
            "UDefaultCameraShakeBase",
            "UPerlinNoiseCameraShakePattern",
            "ChangeRootShakePattern<UPerlinNoiseCameraShakePattern>()",
            "Pattern->Duration",
            "Pattern->BlendInTime",
            "Pattern->BlendOutTime",
            "LocationAmplitudeMultiplier",
            "RotationAmplitudeMultiplier",
            "Pattern->Pitch.Amplitude",
            "Pattern->Yaw.Amplitude",
            "Pattern->Roll.Amplitude",
            "Pattern->FOV.Amplitude",
        ):
            self.assertTrue(token in header or token in source, token)

    def test_all_five_camera_payloads_are_native_and_bound(self) -> None:
        bindings = json.loads(BINDINGS.read_text(encoding="utf-8"))
        cameras = [
            item
            for item in bindings.get("assets", [])
            if item.get("kind") == "camera"
        ]

        self.assertEqual(len(cameras), 5)
        for item in cameras:
            path = item.get("unreal_object_path")
            self.assertTrue(path)
            self.assertTrue(path.startswith("/Script/NARIS_W04."))
            self.assertTrue(path.endswith("CameraShake"))
            self.assertEqual(item.get("expected_unreal_object_path"), path)
            self.assertEqual(item.get("binding_source"), "native_cpp")

    def test_binding_counts_drop_to_thirty_unbound(self) -> None:
        bindings = json.loads(BINDINGS.read_text(encoding="utf-8"))
        assets = bindings.get("assets", [])
        bound = [item for item in assets if item.get("unreal_object_path")]
        unbound = [item for item in assets if not item.get("unreal_object_path")]
        self.assertEqual(len(assets), 35)
        self.assertEqual(len(bound), 5)
        self.assertEqual(len(unbound), 30)


if __name__ == "__main__":
    unittest.main()
