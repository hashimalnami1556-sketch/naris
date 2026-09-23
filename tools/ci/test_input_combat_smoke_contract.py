from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class InputCombatSmokeContractTests(unittest.TestCase):
    def test_keyboard_and_gamepad_actions_share_input_names(self) -> None:
        cfg = read("unreal/NARIS_W04/Config/DefaultInput.ini")
        required = (
            'ActionName="LightAttack",Key=(KeyName="LeftMouseButton")',
            'ActionName="LightAttack",Key=(KeyName="Gamepad_RightShoulder")',
            'ActionName="HeavyAttack",Key=(KeyName="Gamepad_RightTrigger")',
            'ActionName="Dodge",Key=(KeyName="Gamepad_FaceButton_Bottom")',
            'ActionName="Parry",Key=(KeyName="Gamepad_LeftShoulder")',
            'ActionName="ResonanceBurst",Key=(KeyName="Gamepad_FaceButton_Top")',
            'ActionName="Interact",Key=(KeyName="Gamepad_FaceButton_Left")',
            'ActionName="LockOn",Key=(KeyName="Gamepad_RightThumbstick")',
            'ActionName="Sprint",Key=(KeyName="Gamepad_LeftThumbstick")',
            'AxisName="MoveForward",Key=(KeyName="Gamepad_LeftY")',
            'AxisName="MoveRight",Key=(KeyName="Gamepad_LeftX")',
            'AxisName="LookYaw",Key=(KeyName="Gamepad_RightX")',
            'AxisName="LookPitch",Key=(KeyName="Gamepad_RightY")',
        )
        for token in required:
            self.assertIn(token, cfg)

    def test_hero_binds_sprint_lockon_and_interaction(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        for token in (
            'BindAction(TEXT("Sprint")',
            'BindAction(TEXT("LockOn")',
            'BindAction(TEXT("Interact")',
            "ToggleLockOn",
            "StartSprinting",
            "StopSprinting",
        ):
            self.assertIn(token, source)

    def test_lockon_can_target_active_bone_beast(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisLockOnComponent.cpp"
        )
        self.assertIn("Cast<ABoneBeastBoss>", source)
        self.assertIn("Boss->IsEncounterActive()", source)
        self.assertIn("Boss->GetCurrentHealth() > 0.f", source)

    def test_melee_attacks_apply_real_target_damage(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHeroCharacter.cpp"
        )
        self.assertIn("ApplyAttackToLockedTarget", source)
        self.assertIn("Boss->ApplyDamageToEncounter(Damage)", source)
        self.assertIn("TargetCombat->ResolveHit", source)
        self.assertIn("MeleeRange", read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisHeroCharacter.h"
        ))

    def test_bone_beast_starts_through_interaction_contract(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/BoneBeastBoss.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/BoneBeastBoss.cpp"
        )
        self.assertIn("public INarisInteractable", header)
        self.assertIn("TryStartEncounter", header)
        self.assertIn("Interact_Implementation", source)
        self.assertIn("StartEncounter()", source)
        self.assertIn("return bEncounterActive", source)


if __name__ == "__main__":
    unittest.main()
