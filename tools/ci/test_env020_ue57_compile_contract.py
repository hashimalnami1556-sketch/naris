"""ENV-020: regression for compiler failures reproduced on real UE 5.7.4."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/"unreal/NARIS_W04/Source/NARIS_W04"

class UE57CompileRegression(unittest.TestCase):
    def test_hero_movement_statements_are_physical_lines(self):
        text=(SOURCE/"Private/NarisHeroCharacter.cpp").read_text(encoding="utf-8")
        for line in text.splitlines():
            if "GetCharacterMovement()->" in line:
                self.assertNotIn(r"\n",line)
        self.assertIn("GetCharacterMovement()->JumpZVelocity = 600.f;",text)
        self.assertIn("GetCharacterMovement()->AirControl = 0.8f;",text)
        self.assertIn("GetCharacterMovement()->GravityScale = 1.5f;",text)

    def test_input_bindings_are_physical_lines(self):
        text=(SOURCE/"Private/NarisHeroCharacter.cpp").read_text(encoding="utf-8")
        body=text.split("void ANarisHeroCharacter::SetupPlayerInputComponent(",1)[1].split("void ANarisHeroCharacter::MoveForward(",1)[0]
        self.assertNotIn(r"\n",body)
        self.assertIn('Input->BindAction(TEXT("Jump"), IE_Pressed, this, &ACharacter::Jump);',body)
        self.assertIn('Input->BindAction(TEXT("Jump"), IE_Released, this, &ACharacter::StopJumping);',body)
        self.assertIn('Input->BindAction(TEXT("LightAttack"), IE_Pressed, this, &ANarisHeroCharacter::LightAttack);',body)

    def test_makepanel_parameter_does_not_shadow_userwidget_padding(self):
        header=(SOURCE/"Public/NarisSystemMenuWidget.h").read_text(encoding="utf-8")
        cpp=(SOURCE/"Private/NarisSystemMenuWidget.cpp").read_text(encoding="utf-8")
        self.assertNotRegex(header,r"MakePanel\([^;]*FMargin&\s+Padding\b")
        body=cpp.split("UBorder* UNarisSystemMenuWidget::MakePanel(",1)[1].split("void UNarisSystemMenuWidget::BuildInterface(",1)[0]
        self.assertIn("const FMargin& InPadding",body)
        self.assertIn("Panel->SetPadding(InPadding);",body)

if __name__=="__main__":
    unittest.main()
