"""UI-017 one-command native UE5.7 asset audit launch safety contract."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PS1 = ROOT / "tools/windows/Invoke-NarisUI017.ps1"


class UI017EditorGate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.content = PS1.read_text(encoding="utf-8")

    def test_editor_is_explicit_opt_in(self):
        self.assertIn("[switch]$RunEditor", self.content)
        self.assertIn("if (-not $RunEditor)", self.content)

    def test_uses_canonical_unreal_and_audit(self):
        self.assertIn("NARIS_W04.uproject", self.content)
        self.assertIn("verify_ui017_hud_assets.py", self.content)
        self.assertIn("UnrealEditor-Cmd.exe", self.content)

    def test_does_not_overwrite_existing_evidence(self):
        self.assertIn("Test-Path -LiteralPath $report", self.content)
        self.assertIn("throw", self.content)

    def test_propagates_editor_failure(self):
        self.assertIn("$LASTEXITCODE -ne 0", self.content)
        self.assertIn("NARIS_UI017_AUDIT_REPORT", self.content)

    def test_no_default_level_change(self):
        self.assertNotIn("GameDefaultMap=", self.content)
        self.assertNotIn("SaveCurrentLevel", self.content)


if __name__ == "__main__":
    unittest.main()
