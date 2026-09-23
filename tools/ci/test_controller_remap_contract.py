from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


class ControllerRemapContractTests(unittest.TestCase):
    def test_inputcore_is_a_direct_runtime_dependency(self) -> None:
        build = read("unreal/NARIS_W04/Source/NARIS_W04/NARIS_W04.Build.cs")
        self.assertIn('"InputCore"', build)

    def test_pause_controller_exposes_controls_page_and_capture_state(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisPlayerController.h"
        )
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        self.assertIn("Controls", header)
        self.assertIn("virtual bool InputKey(const FInputKeyParams& Params)", header)
        self.assertIn("IsWaitingForGamepadRemap", header)
        self.assertIn("bWaitingForGamepadRemap", header)
        self.assertIn("PendingRemapAction", header)
        self.assertIn("constexpr int32 ControlActionCount = 11", source)
        self.assertIn("constexpr int32 ControlsMenuCount = ControlActionCount + 2", source)

    def test_eleven_core_gameplay_actions_are_remappable(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        for action in (
            "LightAttack",
            "HeavyAttack",
            "Dodge",
            "Parry",
            "ResonanceBurst",
            "LockOn",
            "Interact",
            "Sprint",
            "EssenceNext",
            "EssencePrevious",
            "CompanionMode",
        ):
            self.assertIn(f'TEXT("{action}")', source)

    def test_capture_accepts_gamepad_press_and_consumes_it(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        self.assertIn("Params.Event == IE_Pressed", source)
        self.assertIn("Params.IsGamepad()", source)
        self.assertIn("ApplyGamepadActionRemap(PendingRemapAction, Params.Key, true)", source)
        self.assertIn("return true;", source)

    def test_start_and_back_buttons_remain_reserved_for_menu_recovery(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        self.assertIn("EKeys::Gamepad_Special_Right", source)
        self.assertIn("EKeys::Gamepad_FaceButton_Right", source)
        self.assertIn("IsReservedGamepadMenuKey(NewKey)", source)

    def test_remap_rejects_conflict_with_other_gameplay_action(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        self.assertIn("Mapping.Key != NewKey", source)
        self.assertIn("Mapping.ActionName == ActionName", source)
        self.assertIn("bOtherGameplayAction", source)

    def test_remap_replaces_only_gamepad_mapping_and_persists(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        for token in (
            "UInputSettings::GetInputSettings()",
            "GetActionMappingByName",
            "Mapping.Key.IsGamepadKey()",
            "RemoveActionMapping(Mapping, false)",
            "AddActionMapping(",
            "SaveKeyMappings()",
            "ForceRebuildKeymaps()",
        ):
            self.assertIn(token, source)

    def test_reset_restores_all_default_gamepad_mappings(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        self.assertIn("void ANarisPlayerController::ResetGamepadActionRemaps()", source)
        for key in (
            "Gamepad_RightShoulder",
            "Gamepad_RightTrigger",
            "Gamepad_FaceButton_Bottom",
            "Gamepad_LeftShoulder",
            "Gamepad_FaceButton_Top",
            "Gamepad_RightThumbstick",
            "Gamepad_FaceButton_Left",
            "Gamepad_LeftThumbstick",
            "Gamepad_DPad_Right",
            "Gamepad_DPad_Left",
            "Gamepad_DPad_Up",
        ):
            self.assertIn(key, source)

    def test_controls_page_is_localized_in_en_and_ar(self) -> None:
        en = read(
            "unreal/NARIS_W04/Content/Localization/NARIS_Game/en/NARIS_Game.po"
        )
        ar = read(
            "unreal/NARIS_W04/Content/Localization/NARIS_Game/ar/NARIS_Game.po"
        )
        for key in (
            "PauseControls",
            "ControlsMenuTitle",
            "ControlLightAttack",
            "ControlHeavyAttack",
            "ControlDodge",
            "ControlParry",
            "ControlInteract",
            "ControlCompanionMode",
            "ControlsResetDefaults",
            "ControlsPressButton",
            "ControlsCaptureHint",
            "ControlsMenuHint",
        ):
            marker = f'msgctxt "NARIS,{key}"'
            self.assertIn(marker, en)
            self.assertIn(marker, ar)

    def test_hud_has_capture_and_controls_page_guidance(self) -> None:
        source = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
        )
        self.assertIn("ENarisPauseMenuPage::Controls", source)
        self.assertIn("Controller->IsWaitingForGamepadRemap()", source)
        self.assertIn("ControlsCaptureHint", source)
        self.assertIn("ControlsMenuHint", source)

    def test_interaction_prompt_tracks_live_device_and_remapped_key(self) -> None:
        header = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Public/NarisPlayerController.h"
        )
        controller = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisPlayerController.cpp"
        )
        hud = read(
            "unreal/NARIS_W04/Source/NARIS_W04/Private/NarisHUD.cpp"
        )
        self.assertIn("bLastInputWasGamepad", header)
        self.assertIn("GetActionKeyDisplayName", header)
        self.assertIn("bLastInputWasGamepad = Params.IsGamepad()", controller)
        self.assertIn("GetCurrentGamepadKey(ActionName)", controller)
        self.assertIn("!Mapping.Key.IsGamepadKey()", controller)
        self.assertIn(
            'GetActionKeyDisplayName(TEXT("Interact"))',
            hud,
        )
        self.assertNotIn('TEXT("[E] %s")', hud)


if __name__ == "__main__":
    unittest.main()
