"""UI-017 imported texture audit: require genuine 256px Unreal Texture2D icons."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / "ui/verify_ui017_hud_assets.py"
spec = importlib.util.spec_from_file_location("verify_ui017_hud_assets", PATH)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)


class Texture:
    def __init__(self, w=256, h=256, is_texture=True):
        self.w, self.h, self.is_texture = w, h, is_texture

    def is_a(self, expected):
        return self.is_texture

    def blueprint_get_size_x(self):
        return self.w

    def blueprint_get_size_y(self):
        return self.h


class UI017TextureAudit(unittest.TestCase):
    def test_six_valid_native_textures_can_be_found(self):
        lookup = {audit.asset_path(x): Texture() for x in audit.ICONS}
        result = audit.audit_texture_assets(lookup.get, object)
        self.assertEqual(result["status"], "IMPORT_ASSETS_PRESENT")
        self.assertEqual(len(result["icons"]), 6)
        self.assertEqual(result["gameplay_rendered_in_pie"], False)

    def test_missing_asset_fails(self):
        lookup = {audit.asset_path(x): Texture() for x in audit.ICONS if x != "defense"}
        result = audit.audit_texture_assets(lookup.get, object)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertTrue(any("defense" in error for error in result["errors"]))

    def test_wrong_texture_class_fails(self):
        lookup = {audit.asset_path(x): Texture() for x in audit.ICONS}
        lookup[audit.asset_path("mana")] = Texture(is_texture=False)
        self.assertEqual(audit.audit_texture_assets(lookup.get, object)["status"], "BLOCKED")

    def test_wrong_source_dimensions_fail(self):
        lookup = {audit.asset_path(x): Texture() for x in audit.ICONS}
        lookup[audit.asset_path("energy")] = Texture(w=512)
        self.assertEqual(audit.audit_texture_assets(lookup.get, object)["status"], "BLOCKED")

    def test_preflight_does_not_produce_runtime_success_claims(self):
        lookup = {audit.asset_path(x): Texture() for x in audit.ICONS}
        report = audit.audit_texture_assets(lookup.get, object)
        self.assertFalse(report["gameplay_rendered_in_pie"])
        self.assertFalse(report["full_unreal_build_tested"])
        self.assertFalse(report["release_approved"])


if __name__ == "__main__":
    unittest.main()
