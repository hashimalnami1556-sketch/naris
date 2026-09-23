from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class ReleaseCandidateGateContractTests(unittest.TestCase):
    def test_release_candidate_requires_strict_presentation_bindings(self) -> None:
        source = read("tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1")
        for token in (
            'NARIS_PRESENTATION_STRICT = "1"',
            "unbound_asset_ids",
            "errors",
            'clientconfig=Shipping',
            "BuildCookRun",
            "naris_release_candidate.json",
        ):
            self.assertIn(token, source)

    def test_release_candidate_fails_on_unbound_assets(self) -> None:
        source = read("tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1")
        self.assertIn(
            '@($Presentation.unbound_asset_ids).Count -ne 0',
            source,
        )
        self.assertIn(
            'throw "Release candidate has unbound presentation assets"',
            source,
        )

    def test_manual_workflow_exposes_development_and_release_modes(self) -> None:
        workflow = read(".github/workflows/naris-ci.yml")
        for token in (
            "package_mode:",
            "- development",
            "- release_candidate",
            "Invoke-NarisWindowsPackage.ps1",
            "Invoke-NarisWindowsReleaseCandidate.ps1",
            "NARIS_W04-Windows-Development",
            "NARIS_W04-Windows-Shipping-RC",
        ):
            self.assertIn(token, workflow)

    def test_release_candidate_is_manual_only(self) -> None:
        workflow = read(".github/workflows/naris-ci.yml")
        self.assertIn(
            "if: ${{ github.event_name == 'workflow_dispatch' }}",
            workflow,
        )
        self.assertIn(
            "if: ${{ inputs.package_mode == 'release_candidate' }}",
            workflow,
        )


if __name__ == "__main__":
    unittest.main()
