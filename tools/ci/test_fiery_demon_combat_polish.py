"""Regression tests for Fiery Demon phase animation and boss HUD naming.

Offline source assertions: these are not Unreal Editor/PIE tests.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisFieryDemonBoss.h"
PRIVATE = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisFieryDemonBoss.cpp"
HUD = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
IMPORTER = ROOT / "tools/unreal/import_fiery_demon_runtime.py"

class DemonCombatPolishContracts(unittest.TestCase):
    def test_fiery_demon_hud_name_is_not_bone_beast(self):
        hud=HUD.read_text(encoding="utf-8")
        self.assertIn('BossProgressId == TEXT("FieryDemon")',hud)
        self.assertIn('NSLOCTEXT("NARIS", "HUDFieryDemon", "Fiery Demon")',hud)

    def test_enrage_blocks_attacks_during_transition(self):
        boss=PRIVATE.read_text(encoding="utf-8")
        for part in ("bAutoAttack = false;", "bEnraging = true;",
                     "GetWorldTimerManager().ClearTimer(ImpactTimer)",
                     "EndEnrage()", "bAutoAttack = true;"):
            self.assertIn(part,boss)
        header=PUBLIC.read_text(encoding="utf-8")
        self.assertIn("bool bEnraging = false;",header)

    def test_boss_death_plays_fallback_animation(self):
        header=PUBLIC.read_text(encoding="utf-8")
        boss=PRIVATE.read_text(encoding="utf-8")
        importer=IMPORTER.read_text(encoding="utf-8")
        self.assertIn("DeathAnimation",header)
        self.assertIn("Skel->PlayAnimation(DeathAnimation",boss)
        self.assertIn('"death_animation"',importer)

    def test_enrage_interrupt_does_not_land_old_impact(self):
        source=PRIVATE.read_text(encoding="utf-8")
        self.assertIn("CancelAttack();",source)
        self.assertIn("ClearTimer(ImpactTimer)",source)

if __name__=="__main__":
    unittest.main()
