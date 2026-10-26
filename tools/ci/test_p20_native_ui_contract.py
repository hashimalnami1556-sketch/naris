"""Static guards for the P20 native W04 HUD and cinematic title layout.

These tests verify source contracts only. They never assert a Windows build,
Unreal Editor run, gameplay playtest, or approved user-facing visual quality.
"""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
CPP = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
MENU_CPP = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisSystemMenuWidget.cpp"
MENU_H = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisSystemMenuWidget.h"


class TestP20NativeIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.hud = CPP.read_text(encoding="utf-8")
        cls.menu = MENU_CPP.read_text(encoding="utf-8")
        cls.menu_header = MENU_H.read_text(encoding="utf-8")

    def test_live_player_data_not_browser_simulation(self):
        for source in ("Combat->Health", "Combat->MaxHealth",
                       "Combat->Resonance", "Combat->MaxResonance",
                       "Energy->Energy", "Energy->MaxEnergy"):
            self.assertIn(source, self.hud)

    def test_boss_real_actor_phase_and_active_encounter(self):
        for source in ("ABoneBeastBoss", "Boss->IsEncounterActive()",
                       "Boss->GetCurrentHealth()", "Boss->GetConfiguredMaxHealth()",
                       "ENarisBossPhase::Phase2", "ENarisBossPhase::Phase3"):
            self.assertIn(source, self.hud)

    def test_live_input_bindings_not_browser_demo_keys(self):
        for action in ("LightAttack", "Dodge", "Parry"):
            self.assertIn(f'GetActionKeyDisplayName(TEXT("{action}"))', self.hud)
        self.assertNotIn("document.getElementById", self.hud)

    def test_hidden_menu_does_not_intercept_gameplay_input(self):
        # A Collapsed root could stop Tick and prevent the menu reopening.
        # Opacity zero alone allows invisible child buttons to consume clicks.
        self.assertIn("ESlateVisibility::HitTestInvisible", self.menu)
        self.assertIn("ESlateVisibility::SelfHitTestInvisible", self.menu)
        self.assertIn("SetRenderOpacity(bOpen ? 1.f : 0.f)", self.menu)
        self.assertIn("SetVisibility(bOpen", self.menu)

    def test_cinematic_front_end_and_opaque_submenus(self):
        self.assertIn("bFrontEndLayout", self.menu)
        self.assertIn("BackdropPanel->SetBrushColor", self.menu)
        self.assertIn("NarsicUMG::Obsidian", self.menu)
        self.assertIn("StatusPanelRef->SetVisibility", self.menu)
        for name in ("BackdropPanel", "MenuPanelRef", "StatusPanelRef"):
            self.assertIn(name, self.menu_header)


if __name__ == "__main__":
    unittest.main()
