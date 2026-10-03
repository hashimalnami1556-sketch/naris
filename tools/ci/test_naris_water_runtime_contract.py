from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SWIM_H = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisSwimmingComponent.h"
SWIM_CPP = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisSwimmingComponent.cpp"
VOL_H = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisWaterVolume.h"
VOL_CPP = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisWaterVolume.cpp"
HERO = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisHeroCharacter.h"
HUD = ROOT / "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"

class NarisWaterRuntimeContract(unittest.TestCase):
    def test_swimming_component_exposes_breath_and_state(self):
        h=SWIM_H.read_text(encoding="utf-8")
        for token in ("UNarisSwimmingComponent","GetBreathPercent","IsSwimming","IsUnderwater","EnterWater","ExitWater","SetVerticalSwimInput"):
            self.assertIn(token,h)

    def test_water_volume_owns_overlap_and_current(self):
        h=VOL_H.read_text(encoding="utf-8")
        cpp=VOL_CPP.read_text(encoding="utf-8")
        for token in ("ANarisWaterVolume","UBoxComponent","SurfaceOffset","CurrentStrength","CurrentDirection"):
            self.assertIn(token,h)
        for token in ("OnComponentBeginOverlap","OnComponentEndOverlap","EnterWater","ExitWater"):
            self.assertIn(token,cpp)

    def test_swimming_handles_breath_and_drowning(self):
        cpp=SWIM_CPP.read_text(encoding="utf-8")
        for token in ("BreathRemaining","DrowningDamagePerSecond","Combat->Health","MOVE_Swimming","MOVE_Walking","ActiveWaterVolume"):
            self.assertIn(token,cpp)

    def test_hero_owns_swimming_component(self):
        h=HERO.read_text(encoding="utf-8")
        self.assertIn("UNarisSwimmingComponent",h)
        self.assertIn("Swimming",h)

    def test_hud_draws_breath_only_when_underwater(self):
        hud=HUD.read_text(encoding="utf-8")
        for token in ("Hero->Swimming","IsUnderwater()","GetBreathPercent()","HUDBreath"):
            self.assertIn(token,hud)

if __name__=="__main__":
    unittest.main()
