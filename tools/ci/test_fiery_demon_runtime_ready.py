"""Runtime readiness smoke marker contract; real packaged execution still required."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
CPP=(ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Private/NarisFieryDemonBoss.cpp").read_text(encoding="utf-8")
PS=(ROOT/"tools/windows/Invoke-NarisFieryDemonBuild.ps1").read_text(encoding="utf-8")

class FieryDemonRuntimeReadyContract(unittest.TestCase):
    def test_only_emit_runtime_ready_when_character_asset_present(self):
        self.assertIn("GetSkeletalMeshAsset()",CPP)
        self.assertIn("SmashAnimation",CPP)
        self.assertIn("NovaAnimation",CPP)
        self.assertIn("IdleAnimation",CPP)
        self.assertIn("NARIS_FIERY_DEMON_RUNTIME_READY",CPP)
        self.assertIn("NARIS_FIERY_DEMON_ASSET_BINDING_FAILED",CPP)

    def test_packaged_smoke_requires_boss_runtime_ready_marker(self):
        self.assertIn("$expectedBossLogRegex",PS)
        self.assertIn("$bossReadyFound",PS)
        self.assertIn("NARIS_FIERY_DEMON_RUNTIME_READY",PS)
        self.assertRegex(PS,r"(?s)if\s*\(-not\s*\$bossReadyFound\).*?throw")

    def test_regex_matches_real_ue_display_log_not_cli_string(self):
        marker=re.search(r"\$expectedBossLogRegex\s*=\s*'([^']+)'",PS)
        self.assertIsNotNone(marker)
        pattern=marker.group(1)
        self.assertRegex("LogTemp: Display: NARIS_FIERY_DEMON_RUNTIME_READY",pattern)
        self.assertNotRegex("LogInit: Command Line: -NARIS_FIERY_DEMON_RUNTIME_READY",pattern)
        self.assertNotRegex("LogTemp: Display: NARIS_FIERY_DEMON_RUNTIME_READY_BOGUS",pattern)

if __name__=="__main__":
    unittest.main()
