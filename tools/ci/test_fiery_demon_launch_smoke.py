"""Ensure Windows smoke test confirms Unreal really LOADS the Fiery Demon level.

The process command line alone contains the map path and must not count.
These are offline checks, not real Windows/UE execution.
"""
from pathlib import Path
import re
import unittest

SOURCE=(Path(__file__).resolve().parents[1] / "windows/Invoke-NarisFieryDemonBuild.ps1").read_text(encoding="utf-8")

class FieryDemonSmokeContracts(unittest.TestCase):
    def test_requires_loadmap_marker_not_any_mention(self):
        self.assertNotIn('if ($text -match "L_FieryDemon_QA")', SOURCE)
        self.assertIn("LogLoad:",SOURCE)
        self.assertIn("LoadMap:",SOURCE)

    def test_expected_map_regex_excludes_command_line_and_wrong_map(self):
        marker=re.search(r"\$expectedMapLogRegex\s*=\s*'([^']+)'",SOURCE)
        self.assertIsNotNone(marker,"Explicit LoadMap regex must be declared in build script")
        pattern=marker.group(1)
        genuine="[2026.10.15-09.00.00]LogLoad: LoadMap: /Game/NARIS/W04/Maps/L_FieryDemon_QA"
        argv="LogInit: Command Line: /Game/NARIS/W04/Maps/L_FieryDemon_QA -log -windowed"
        wrong="LogLoad: LoadMap: /Game/NARIS/W04/Maps/W04_Prototype"
        suffix="LogLoad: LoadMap: /Game/NARIS/W04/Maps/L_FieryDemon_QA_Old"
        self.assertRegex(genuine,pattern)
        for bad in (argv,wrong,suffix):
            self.assertNotRegex(bad,pattern)

    def test_smoke_leaves_shipping_unverified(self):
        self.assertIn('combat_playtested = $false',SOURCE)
        self.assertIn('shipping_approved = $false',SOURCE)

if __name__=="__main__":
    unittest.main()
