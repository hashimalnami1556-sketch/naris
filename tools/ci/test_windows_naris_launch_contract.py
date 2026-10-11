"""Source-only launcher regression contract; Unreal runtime acceptance is separate."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class NarisWindowsLaunchContractTests(unittest.TestCase):
    def test_launch_script_finds_both_engine_project_names(self):
        source = read("tools/windows/Start-NarisGame.ps1")
        for token in ("NARIS.exe", "NARIS_W04.exe", "NARSIC.exe", "-Recurse", "LastWriteTimeUtc", "if ($ListOnly)", "[switch]$ListOnly"):
            self.assertIn(token, source)
        self.assertIn("[string]$Executable", source)
        self.assertNotIn("Stop-Process", source)

    def test_launch_script_requires_actual_process_and_fresh_log(self):
        source = read("tools/windows/Start-NarisGame.ps1")
        for token in ("-PassThru", ".HasExited", ".ExitCode", "LastWriteTimeUtc", "Fatal error:", "[DateTime]::UtcNow"):
            self.assertIn(token, source)

    def test_apply_patch_does_not_force_close_editors_or_overwrite_build(self):
        source = read("NARIS_MASTER/14_UI_UX/releases/UI4_1/Tools/Apply-UI4_1.ps1")
        self.assertNotIn("Stop-Process", source)
        self.assertIn("Get-Process UnrealEditor", source)
        self.assertIn("already exists", source)
        self.assertIn("-package", source)
        self.assertIn("Get-ChildItem -LiteralPath $out -Filter 'NARIS.exe' -File -Recurse", source)
        self.assertIn("-LaunchedAtUtc $launchUtc", source)
        self.assertLess(source.index("$ubt = Join-Path"), source.index("$backup = Join-Path"))
        self.assertLess(source.index("HUD marker missing"), source.index("$backup = Join-Path"))

    def test_validator_does_not_rely_on_stale_archived_log(self):
        source = read("NARIS_MASTER/14_UI_UX/releases/UI4_1/Tools/Validate-UI4_1.ps1")
        for token in ("LaunchedAtUtc", "LastWriteTimeUtc", "Get-ChildItem", "NARIS_FRONTEND READY", "NARIS_RUNTIME_READY", "WaitSeconds"):
            self.assertIn(token, source)
        self.assertIn("[NARIS] Validated fresh log", source)

    def test_release_readme_does_not_equate_markers_with_visual_acceptance(self):
        source = read("NARIS_MASTER/14_UI_UX/releases/UI4_1/README.md")
        self.assertIn("does **not** prove menu visibility", source)


if __name__ == "__main__":
    unittest.main()
