from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class WindowsPackagePipelineContractTests(unittest.TestCase):
    def test_package_pipeline_builds_bootstraps_cooks_and_launches(self) -> None:
        source = read("tools/windows/Invoke-NarisWindowsPackage.ps1")
        ordered_tokens = (
            "NARIS_W04Editor",
            "Invoke-NarisW04AuthoringBootstrap.ps1",
            "W04_Prototype.umap",
            "DA_BoneBeast_Smoke.uasset",
            "BuildCookRun",
            "-platform=Win64",
            "-cook",
            "-stage",
            "-pak",
            "-package",
            "NARIS_W04.exe",
            "Start-Process",
            "-csvCaptureFrames=600",
            "-csvGpuStats",
            "-LLMCSV",
            "naris_windows_package_smoke.json",
        )
        cursor = -1
        for token in ordered_tokens:
            index = source.find(token)
            self.assertGreater(index, cursor, token)
            cursor = index

    def test_bootstrap_creates_expected_runtime_assets(self) -> None:
        source = read(
            "unreal/NARIS_W04/Content/Python/naris_bootstrap_w04_smoke.py"
        )
        self.assertIn(
            'MAP_PATH = "/Game/NARIS/W04/Maps/W04_Prototype"',
            source,
        )
        self.assertIn(
            'BOSS_DATA_PATH = DATA_DIR + "/DA_BoneBeast_Smoke"',
            source,
        )
        for actor in (
            "NarisWaystone",
            "NarisMemoryCrystal",
            "NarisAshGate",
            "CelestialWolf",
            "BoneBeastBoss",
        ):
            self.assertIn(actor, source)

    def test_default_map_matches_generated_map(self) -> None:
        engine = read("unreal/NARIS_W04/Config/DefaultEngine.ini")
        self.assertIn(
            "GameDefaultMap=/Game/NARIS/W04/Maps/W04_Prototype",
            engine,
        )

    def test_bone_beast_has_data_asset_fallback(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/BoneBeastBoss.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp"
        )
        for token in (
            "FallbackMaxHealth",
            "FallbackPhase2HealthPercent",
            "FallbackPhase3HealthPercent",
            "FallbackQuestCompletionId",
        ):
            self.assertIn(token, header)
        self.assertIn("GetConfiguredMaxHealth()", source)


if __name__ == "__main__":
    unittest.main()
