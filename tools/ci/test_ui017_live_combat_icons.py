"""UI-017 regression contract for real game HUD SVG->Texture2D rendering.

These checks operate on C++ source and do not substitute for UE5.7 PIE visual QA.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
HEADER = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisHUD.h"
SOURCE = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
ICON_DIR = ROOT / "docs/ui/vector_sources/WORLD-015"


class LiveCombatHUDIcons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h = HEADER.read_text(encoding="utf-8")
        cls.s = SOURCE.read_text(encoding="utf-8")

    def function(self, name, next_name):
        return self.s.split(name, 1)[1].split(next_name, 1)[0]

    def test_six_original_icon_sources_exist(self):
        self.assertEqual(
            {p.stem for p in ICON_DIR.glob("*.svg")},
            {"health", "energy", "mana", "attack", "defense", "map"}
        )

    def test_gameplay_icons_have_gc_safe_storage(self):
        self.assertIn("UPROPERTY(Transient)", self.h)
        self.assertIn("TMap<FName, TObjectPtr<UTexture2D>> GameplayIconTextures", self.h)

    def test_runtime_icons_loaded_once_at_beginplay(self):
        begin = self.function("void ANarisHUD::BeginPlay()", "void ANarisHUD::DrawPauseMenu()")
        self.assertIn('LoadObject<UTexture2D>', begin)
        self.assertIn("/Game/NARIS/UI/Icons/", begin)
        self.assertNotIn("LoadObject<UTexture2D>", self.s.split("void ANarisHUD::DrawHUD()",1)[1])

    def test_draw_helper_uses_real_texture_with_null_fallback(self):
        self.assertIn("void ANarisHUD::DrawGameIcon(", self.s)
        helper = self.function("void ANarisHUD::DrawGameIcon(", "void ANarisHUD::DrawPlayerVitals(")
        self.assertIn("if (!Canvas || !IconTexture)", helper)
        self.assertIn("DrawTexture(", helper)

    def test_live_health_resonance_and_energy_icons(self):
        body = self.function("void ANarisHUD::DrawPlayerVitals(", "void ANarisHUD::DrawBreath(")
        for name in ("health", "mana", "energy"):
            self.assertIn(f'DrawGameIcon(TEXT("{name}")', body)
        self.assertIn("Hero->Combat->Health", body)
        self.assertIn("Hero->Combat->Resonance", body)
        self.assertIn("Hero->Energy->Energy", body)

    def test_attack_and_defense_preserve_live_key_mapping(self):
        body = self.function("void ANarisHUD::DrawPlayerVitals(", "void ANarisHUD::DrawBreath(")
        self.assertIn('DrawGameIcon(TEXT("attack")', body)
        self.assertIn('DrawGameIcon(TEXT("defense")', body)
        for action in ("LightAttack", "Dodge", "Parry"):
            self.assertIn(f'GetActionKeyDisplayName(TEXT("{action}"))', body)

    def test_map_icon_uses_actual_quest_state(self):
        body = self.function("void ANarisHUD::DrawObjectiveCard(", "void ANarisHUD::DrawInteractionPrompt(")
        self.assertIn('DrawGameIcon(TEXT("map")', body)
        self.assertIn("Runtime->IsQuestActive", body)

    def test_original_approved_ui_images_are_not_faked(self):
        for name in ("UI_Character_Approved.png", "UI_Combat_Approved.png", "UI_MainMenu_Approved.png"):
            self.assertNotIn(name, self.s)

    def test_no_gameplay_values_are_fabricated(self):
        self.assertNotIn("DrawBar(TEXT(\"Health\"), 100", self.s)
        self.assertNotIn("DrawBar(TEXT(\"Energy\"), 100", self.s)


if __name__ == "__main__":
    unittest.main()
