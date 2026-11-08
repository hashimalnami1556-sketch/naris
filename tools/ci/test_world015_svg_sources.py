"""WORLD-015 six source-editable SVG icons, separate from approved screenshots."""
from pathlib import Path
import unittest
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[2]
ICONS = ROOT / "docs/ui/vector_sources/WORLD-015"
NAMES = {"health", "energy", "mana", "attack", "defense", "map"}
SVG = "{http://www.w3.org/2000/svg}"


class OriginalVectorHudIcons(unittest.TestCase):
    def test_exactly_six_source_svg_icons(self):
        self.assertEqual({f.stem for f in ICONS.glob("*.svg")}, NAMES)

    def test_valid_scalable_svg_and_actual_paths(self):
        for name in NAMES:
            with self.subTest(icon=name):
                root = ElementTree.parse(ICONS / (name + ".svg")).getroot()
                self.assertEqual(root.tag, SVG + "svg")
                self.assertEqual(root.attrib.get("viewBox"), "0 0 96 96")
                self.assertGreater(len(list(root.iter(SVG + "path"))), 1)

    def test_no_external_image_or_fonts(self):
        for name in NAMES:
            root = ElementTree.parse(ICONS / (name + ".svg")).getroot()
            self.assertFalse(list(root.iter(SVG + "image")))
            self.assertFalse(list(root.iter(SVG + "text")))
            text = (ICONS / (name + ".svg")).read_text("utf-8").lower()
            self.assertNotIn("http://", text.replace("http://www.w3.org/2000/svg", ""))
            self.assertNotIn("https://", text)


if __name__ == "__main__":
    unittest.main()
