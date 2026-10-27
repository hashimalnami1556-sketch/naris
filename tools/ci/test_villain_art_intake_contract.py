"""Source-only gate for optional NARIS villain skinning and animation intake.

No mesh or engine is fabricated by this test. Unreal Windows execution is required.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "unreal/NARIS_W04/Source/NARIS_W04"
UE_SCRIPT = ROOT / "unreal/NARIS_W04/Content/Python/naris_import_villain_fbx.py"
WINDOWS = ROOT / "tools/windows/Invoke-NarisW04VillainArtIntake.ps1"


class VillainArtIntakeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h = (SRC / "Public/NarisVillainCharacter.h").read_text(encoding="utf-8")
        cls.cpp = (SRC / "Private/NarisVillainCharacter.cpp").read_text(encoding="utf-8")
        cls.py = UE_SCRIPT.read_text(encoding="utf-8")
        cls.ps = WINDOWS.read_text(encoding="utf-8")

    def test_explicit_art_and_not_auto_approved(self):
        self.assertIn("TObjectPtr<USkeletalMesh> VisualMesh", self.h)
        self.assertIn("if (VisualMesh && GetMesh())", self.cpp)
        self.assertIn("SetSkeletalMeshAsset(VisualMesh)", self.cpp)
        self.assertIn("DevelopmentVisual->SetVisibility", self.cpp)
        self.assertIn("DEVELOPMENT_ONLY", self.py)

    def test_all_character_state_animation_hooks(self):
        for prop in ("IdleAnimation", "WalkAnimation", "LightAttackAnimation",
                     "HeavyAttackAnimation", "StaggerAnimation", "DeathAnimation"):
            self.assertIn(prop, self.h)
        for token in ("PlayStateAnimation", "GetSkeleton()", "PlayAnimation(",
                      "ENarisVillainState::Patrol", "ENarisVillainState::Dead"):
            self.assertIn(token, self.cpp)

    def test_importer_fails_missing_mesh_and_clips(self):
        for token in ("SK_", ".fbx", "FBXIT_SKELETAL_MESH", "SkeletalMesh",
                      "AnimSequence", "idle_animation", "walk_animation",
                      "light_attack_animation", "heavy_attack_animation",
                      "stagger_animation", "death_animation", "raise RuntimeError"):
            self.assertIn(token, self.py)
        self.assertIn("naris_villain_fbx_intake.json", self.py)

    def test_windows_launcher_integrates_blender_and_unreal_without_shipping(self):
        for token in ("Expand-Archive", "BlenderExecutable", "NARIS_VILLAIN_FBX_DIR",
                      "convert_glb_to_fbx_blender.py", "Invoke-NarisW04VillainIntegration.ps1",
                      "naris_import_villain_fbx.py", "Development"):
            self.assertIn(token.lower(), self.ps.lower())


if __name__ == "__main__":
    unittest.main()
