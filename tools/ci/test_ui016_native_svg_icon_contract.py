"""UI-016 contract: six vector glyphs become REAL native UMG brush images.

Test first (red), then implement actual C++ and editor importer.
UE5.7 Editor runtime visual tests remain mandatory before merging.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
WIDGET_C = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisSystemMenuWidget.cpp"
WIDGET_H = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisSystemMenuWidget.h"
IMPORTER = ROOT / "tools/ui/import_naris_ui016_icons.py"
ASSETS = {"health", "energy", "mana", "attack", "defense", "map"}


class NativeIconBindingsContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cpp = WIDGET_C.read_text(encoding="utf-8")
        cls.header = WIDGET_H.read_text(encoding="utf-8")
        cls.importer = IMPORTER.read_text(encoding="utf-8")

    def test_image_widgets_are_in_native_widget_tree(self):
        self.assertIn("#include \"Components/Image.h\"", self.cpp)
        self.assertIn("ConstructWidget<UImage>", self.cpp)
        self.assertIn("IconImages.Add(", self.cpp)
        self.assertIn("TArray<TObjectPtr<UImage>> IconImages", self.header)

    def test_images_get_actual_texture_brushes(self):
        self.assertIn("SetBrushFromTexture(", self.cpp)
        self.assertIn("SetColorAndOpacity(", self.cpp)

    def test_glyph_fallback_exists_if_texture_is_missing(self):
        self.assertIn("if (IconTexture)", self.cpp)
        self.assertIn("ResolveIcon(Index)", self.cpp)
        self.assertIn("IconTexts[Index]->SetVisibility(", self.cpp)

    def test_input_activation_and_hover_are_preserved(self):
        self.assertIn("Controller->ActivateMenuIndex(MenuIndex);", self.cpp)
        self.assertIn("Controller->SelectMenuIndex(MenuIndex);", self.cpp)

    def test_uses_stable_unreal_texture_path(self):
        self.assertIn("/Game/NARIS/UI/Icons/", self.cpp)
        self.assertIn("/Game/NARIS/UI/Icons", self.importer)
        self.assertIn("NARIS_UI016_ICON_ROOT", self.importer)

    def test_icon_names_are_whitelisted(self):
        for name in ASSETS:
            self.assertIn(f"TEXT(\"{name}\")", self.cpp)
            self.assertIn(f'"{name}"', self.importer)

    def test_no_asset_overwrite_without_opt_in(self):
        self.assertIn("does_directory_exist", self.importer)
        self.assertIn("replace_existing", self.importer)
        self.assertIn("False", self.importer)

    def test_source_assets_are_verified_before_import(self):
        self.assertIn("sha256", self.importer)
        self.assertIn("manifest.json", self.importer)
        self.assertIn("UI/IconsPng", self.importer)

    def test_no_flattening_of_original_approved_screens(self):
        self.assertNotIn("UI_MainMenu_Approved.png", self.cpp)
        self.assertNotIn("UI_Character_Approved.png", self.cpp)
        self.assertNotIn("UI_Combat_Approved.png", self.cpp)


if __name__ == "__main__":
    unittest.main()
