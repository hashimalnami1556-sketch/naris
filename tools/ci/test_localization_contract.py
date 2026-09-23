from __future__ import annotations

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "unreal" / "NARIS_W04" / "Source" / "NARIS_W04"
EN_PO = ROOT / "unreal" / "NARIS_W04" / "Content" / "Localization" / "NARIS_Game" / "en" / "NARIS_Game.po"
AR_PO = ROOT / "unreal" / "NARIS_W04" / "Content" / "Localization" / "NARIS_Game" / "ar" / "NARIS_Game.po"
LOC_CONFIG = ROOT / "unreal" / "NARIS_W04" / "Config" / "Localization" / "NARIS_Game.ini"


def parse_po(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    entries: dict[str, str] = {}
    blocks = re.split(r"\n\s*\n", text)
    for block in blocks:
        context = re.search(r'^msgctxt "NARIS,([^"]+)"', block, re.M)
        target = re.search(r'^msgstr "(.*)"$', block, re.M)
        if context and target:
            entries[context.group(1)] = target.group(1)
    return entries


class LocalizationContractTests(unittest.TestCase):
    def test_all_naris_source_keys_have_en_and_ar_translations(self) -> None:
        keys: set[str] = set()
        pattern = re.compile(
            r'NSLOCTEXT\(\s*"NARIS"\s*,\s*"([^"]+)"\s*,',
            re.S,
        )
        for path in list(SOURCE.rglob("*.cpp")) + list(SOURCE.rglob("*.h")):
            keys.update(pattern.findall(path.read_text(encoding="utf-8")))

        self.assertGreater(len(keys), 0)
        en = parse_po(EN_PO)
        ar = parse_po(AR_PO)

        for key in sorted(keys):
            self.assertIn(key, en, f"missing EN localization key: {key}")
            self.assertIn(key, ar, f"missing AR localization key: {key}")
            self.assertTrue(en[key].strip(), f"empty EN translation: {key}")
            self.assertTrue(ar[key].strip(), f"empty AR translation: {key}")

    def test_localization_config_generates_en_and_ar(self) -> None:
        config = LOC_CONFIG.read_text(encoding="utf-8")
        self.assertIn("NativeCulture=en", config)
        self.assertIn("CulturesToGenerate=en", config)
        self.assertIn("CulturesToGenerate=ar", config)
        self.assertIn("GenerateTextLocalizationResource", config)

    def test_windows_package_runs_localization_before_cook(self) -> None:
        source = (ROOT / "tools" / "windows" / "Invoke-NarisWindowsPackage.ps1").read_text(
            encoding="utf-8"
        )
        loc_index = source.index("Invoke-NarisLocalization.ps1")
        cook_index = source.index("BuildCookRun")
        self.assertLess(loc_index, cook_index)


if __name__ == "__main__":
    unittest.main()
