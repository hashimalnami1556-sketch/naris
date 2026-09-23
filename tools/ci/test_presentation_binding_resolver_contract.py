from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class PresentationBindingResolverContractTests(unittest.TestCase):
    def test_resolver_never_creates_missing_payloads(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/naris_resolve_presentation_bindings.py"
        )
        self.assertNotIn("create_asset(", source)
        self.assertNotIn("spawn", source.lower())
        self.assertIn("unreal.load_asset", source)
        self.assertIn("unreal.load_class", source)

    def test_resolver_validates_audio_and_vfx_types(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/naris_resolve_presentation_bindings.py"
        )
        self.assertIn("isinstance(loaded, unreal.SoundBase)", source)
        self.assertIn("isinstance(loaded, unreal.NiagaraSystem)", source)

    def test_resolver_only_populates_loadable_expected_path(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/naris_resolve_presentation_bindings.py"
        )
        self.assertIn('item["unreal_object_path"] = expected', source)
        self.assertIn('item["binding_source"] = "resolved_expected_path"', source)
        self.assertIn("if loaded is None:", source)
        self.assertIn("unresolved.append(asset_id)", source)

    def test_strict_mode_rejects_unresolved_payloads(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/naris_resolve_presentation_bindings.py"
        )
        self.assertIn("NARIS_PRESENTATION_STRICT", source)
        self.assertIn("if strict_mode() and unresolved:", source)

    def test_bootstrap_resolves_before_profile_authoring(self) -> None:
        source = read("tools/windows/Invoke-NarisW04AuthoringBootstrap.ps1")
        resolve_index = source.index(
            "[NARIS] Resolving real presentation payloads at deterministic paths"
        )
        profile_index = source.index(
            "[NARIS] Building/loading shared W04 presentation profile"
        )
        self.assertLess(resolve_index, profile_index)
        self.assertIn("naris_resolve_presentation_bindings.py", source)

    def test_development_package_archives_resolution_report(self) -> None:
        source = read("tools/windows/Invoke-NarisWindowsPackage.ps1")
        for token in (
            "naris_presentation_binding_resolution.json",
            "presentation_binding_resolution_status",
            "presentation_resolved_asset_ids",
            "presentation_already_bound_asset_ids",
            "presentation_unresolved_asset_ids",
        ):
            self.assertIn(token, source)


if __name__ == "__main__":
    unittest.main()
