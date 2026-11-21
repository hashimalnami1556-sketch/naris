"""ANIM-024 regression for the existing Wolf V9 AnimBlueprint native parent.

The real UE 5.7.4 editor log showed ABP_CelestialWolf_C failed to load
because /Script/NARIS_W04.NarisWolfAnimInstance did not exist. After an
isolated class-only compatibility probe, it showed missing SmoothedSpeed
in the locomotion BlendSpace. These source checks do NOT replace UE tests.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PUBLIC = ROOT / "unreal" / "NARIS_W04" / "Source" / "NARIS_W04" / "Public"
PRIVATE = ROOT / "unreal" / "NARIS_W04" / "Source" / "NARIS_W04" / "Private"


class WolfAnimationNativeContract(unittest.TestCase):
    def test_existing_blueprint_parent_has_correct_reflected_name(self):
        path = PUBLIC / "NarisWolfAnimInstance.h"
        self.assertTrue(path.is_file(), "Native parent referenced by ABP_CelestialWolf is missing")
        text = path.read_text(encoding="utf-8")
        self.assertIn('#include "Animation/AnimInstance.h"', text)
        self.assertIn("UCLASS(Blueprintable, BlueprintType)", text)
        self.assertIn("class NARIS_W04_API UNarisWolfAnimInstance : public UAnimInstance", text)
        self.assertIn("GENERATED_BODY()", text)

    def test_existing_blendspace_speed_field_is_reflected(self):
        text = (PUBLIC / "NarisWolfAnimInstance.h").read_text(encoding="utf-8")
        self.assertRegex(text, r"UPROPERTY\([^\n]*BlueprintReadOnly[^\n]*\)[\s\S]*?float SmoothedSpeed")
        self.assertRegex(text, r"float SpeedInterpolationRate")

    def test_anim_speed_is_updated_from_real_pawn_velocity(self):
        text = (PRIVATE / "NarisWolfAnimInstance.cpp").read_text(encoding="utf-8")
        for required in ("NativeUpdateAnimation", "Super::NativeUpdateAnimation",
                         "TryGetPawnOwner", "GetVelocity", "Size2D", "FMath::FInterpTo",
                         "SmoothedSpeed", "SpeedInterpolationRate"):
            self.assertIn(required, text)
        self.assertRegex(text, r"FMath::Max\(0\.f,\s*DeltaSeconds\)")

    def test_no_temporary_diagnostic_only_class_shipped(self):
        text = (PUBLIC / "NarisWolfAnimInstance.h").read_text(encoding="utf-8")
        self.assertNotIn("THIS IS NOT PRODUCTION APPROVAL", text)
        self.assertNotIn("class identity only", text.lower())


if __name__ == "__main__":
    unittest.main()
