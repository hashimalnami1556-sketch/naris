from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[2]
CPP=(ROOT/"unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp").read_text(encoding="utf-8")

class Stage29MenuMapIntegration(unittest.TestCase):
    def test_new_game_targets_production_map(self):
        self.assertIn('/Game/NARIS/W04/Maps/W04_AshenForest', CPP)
        self.assertIn('FPackageName::DoesPackageExist', CPP)
        self.assertIn('FName(TEXT("W04_AshenForest"))', CPP)

    def test_prototype_fallback_is_explicit_only(self):
        self.assertIn('NarisAllowPrototypeFallback', CPP)
        self.assertIn('New Game blocked: production map', CPP)

if __name__=="__main__":
    unittest.main()
