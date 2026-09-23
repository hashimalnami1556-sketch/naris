from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class PresentationProfileAuthoringContractTests(unittest.TestCase):
    def test_runtime_component_supports_shared_profile_and_wildcards(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisPresentationComponent.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPresentationComponent.cpp"
        )
        self.assertIn("class NARIS_W04_API UNarisPresentationProfile", header)
        self.assertIn("TObjectPtr<UNarisPresentationProfile> Profile", header)
        self.assertIn("FSoftObjectPath DefaultProfilePath", header)
        self.assertIn("bAutoLoadDefaultProfile", header)
        self.assertIn("DA_W04_Presentation.DA_W04_Presentation", source)
        self.assertIn("DefaultProfilePath.TryLoad()", source)
        self.assertIn("Profile->Cues.FindByPredicate", source)
        self.assertIn('PatternString.EndsWith(TEXT(".*"))', source)
        self.assertIn("Actual.ToString().StartsWith(Prefix)", source)

    def test_unreal_python_authoring_is_manifest_and_binding_driven(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/naris_build_presentation_profile.py"
        )
        for token in (
            "W04_PresentationCueManifest.json",
            "W04_PresentationAssetBindings.json",
            "NarisPresentationProfile",
            "NarisPresentationCue",
            "dynamic_cues",
            "runtime_cue",
            "NARIS_PRESENTATION_STRICT",
            "naris_presentation_authoring.json",
            "bound_asset_ids",
            "unbound_asset_ids",
            "unbound_expected_paths",
        ):
            self.assertIn(token, source)

    def test_authoring_does_not_fabricate_unbound_assets(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/naris_build_presentation_profile.py"
        )
        self.assertIn("if not object_path:", source)
        self.assertIn("return None", source)
        self.assertIn("unbound.append(asset_id)", source)
        self.assertIn("if strict_mode() and unbound:", source)
        self.assertIn("expected_unreal_object_path", source)

    def test_windows_bootstrap_runs_presentation_authoring(self) -> None:
        source = read("tools/windows/Invoke-NarisW04AuthoringBootstrap.ps1")
        self.assertIn("naris_build_presentation_profile.py", source)
        self.assertIn(
            "[NARIS] Building/loading shared W04 presentation profile",
            source,
        )
        self.assertIn("& $UnrealCmd $UProject", source)

    def test_windows_package_requires_profile_and_report(self) -> None:
        source = read("tools/windows/Invoke-NarisWindowsPackage.ps1")
        for token in (
            "DA_W04_Presentation.uasset",
            "naris_presentation_authoring.json",
            "$PresentationAuthoringData.status -ne",
            "presentation_bound_asset_ids",
            "presentation_unbound_asset_ids",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
