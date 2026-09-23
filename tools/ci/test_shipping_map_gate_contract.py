from __future__ import annotations

from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]

def read(rel: str) -> str:
    return (ROOT/rel).read_text(encoding="utf-8")

class ShippingMapGateContractTests(unittest.TestCase):
    def test_validator_targets_ashen_forest_and_rejects_smoke_content(self):
        source=read("unreal/NARIS_W04/Content/Python/naris_validate_shipping_map.py")
        for token in (
            'PRODUCTION_MAP="/Game/NARIS/W04/Maps/W04_AshenForest"',
            '"NARIS_RuntimeSmokeDirector"',
            'FORBIDDEN_PREFIXES=("DEV_",)',
            '"NARIS_Waystone_0001"',
            '"NARIS_MemoryCrystal_0001"',
            '"NARIS_AshGate_0001"',
            '"NARIS_CelestialWolf_0001"',
            '"NARIS_BoneBeastBoss_0001"',
            '"NARIS_BossArenaController"',
            "naris_shipping_map_validation.json",
        ):
            self.assertIn(token,source)

    def test_release_candidate_runs_shipping_map_validator(self):
        source=read("tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1")
        self.assertIn("naris_validate_shipping_map.py",source)
        self.assertIn("[NARIS RC] Validating production Ashen Forest map",source)
        self.assertIn("shipping_map_validation_status",source)

    def test_release_candidate_cooks_production_map_not_smoke_map(self):
        source=read("tools/windows/Invoke-NarisWindowsReleaseCandidate.ps1")
        self.assertIn('"-map=W04_AshenForest"',source)
        self.assertNotIn('"-map=W04_Prototype"',source)

if __name__=="__main__":
    unittest.main()
