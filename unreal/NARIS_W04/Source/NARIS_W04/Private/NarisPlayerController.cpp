#include "NarisPlayerController.h"

#include "Components/InputComponent.h"
#include "GameFramework/InputSettings.h"
#include "GameFramework/PlayerInput.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "NarisRuntimeSubsystem.h"
#include "Misc/Parse.h"
#include "Misc/CommandLine.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"
#include "NarisGameUserSettings.h"

namespace
{
    constexpr int32 PauseMainMenuCount = 3;
    constexpr int32 FrontEndMainMenuCount = 5;
    constexpr int32 SettingsMenuCount = 17;
    constexpr int32 ControlActionCount = 11;
    constexpr int32 ControlsMenuCount = ControlActionCount + 2;

    enum ENarisSettingsRow : int32
    {
        Quality = 0,
        VSync,
        FrameRate,
        MasterVolume,
        MusicVolume,
        SFXVolume,
        VoiceVolume,
        CameraShake,
        ReduceCameraShake,
        Subtitles,
        SubtitleScale,
        HighContrast,
        ColorVision,
        ColorVisionSeverity,
        ApplySave,
        ResetDefaults,
        Back
    };


    FName ControlActionName(int32 Index)
    {
        static const TArray<FName> Actions = {
            TEXT("LightAttack"),
            TEXT("HeavyAttack"),
            TEXT("Dodge"),
            TEXT("Parry"),
            TEXT("ResonanceBurst"),
            TEXT("LockOn"),
            TEXT("Interact"),
            TEXT("Sprint"),
            TEXT("EssenceNext"),
            TEXT("EssencePrevious"),
            TEXT("CompanionMode")
        };

        return Actions.IsValidIndex(Index)
            ? Actions[Index]
            : NAME_None;
    }

    FKey DefaultGamepadKey(FName ActionName)
    {
        if (ActionName == TEXT("LightAttack"))
        {
            return EKeys::Gamepad_RightShoulder;
        }
        if (ActionName == TEXT("HeavyAttack"))
        {
            return EKeys::Gamepad_RightTrigger;
        }
        if (ActionName == TEXT("Dodge"))
        {
            return EKeys::Gamepad_FaceButton_Bottom;
        }
        if (ActionName == TEXT("Parry"))
        {
            return EKeys::Gamepad_LeftShoulder;
        }
        if (ActionName == TEXT("ResonanceBurst"))
        {
            return EKeys::Gamepad_FaceButton_Top;
        }
        if (ActionName == TEXT("LockOn"))
        {
            return EKeys::Gamepad_RightThumbstick;
        }
        if (ActionName == TEXT("Interact"))
        {
            return EKeys::Gamepad_FaceButton_Left;
        }
        if (ActionName == TEXT("Sprint"))
        {
            return EKeys::Gamepad_LeftThumbstick;
        }
        if (ActionName == TEXT("EssenceNext"))
        {
            return EKeys::Gamepad_DPad_Right;
        }
        if (ActionName == TEXT("EssencePrevious"))
        {
            return EKeys::Gamepad_DPad_Left;
        }
        if (ActionName == TEXT("CompanionMode"))
        {
            return EKeys::Gamepad_DPad_Up;
        }

        return EKeys::Invalid;
    }

    FText ControlActionLabel(FName ActionName)
    {
        if (ActionName == TEXT("LightAttack"))
        {
            return NSLOCTEXT("NARIS", "ControlLightAttack", "Light Attack");
        }
        if (ActionName == TEXT("HeavyAttack"))
        {
            return NSLOCTEXT("NARIS", "ControlHeavyAttack", "Heavy Attack");
        }
        if (ActionName == TEXT("Dodge"))
        {
            return NSLOCTEXT("NARIS", "ControlDodge", "Dodge");
        }
        if (ActionName == TEXT("Parry"))
        {
            return NSLOCTEXT("NARIS", "ControlParry", "Parry");
        }
        if (ActionName == TEXT("ResonanceBurst"))
        {
            return NSLOCTEXT("NARIS", "ControlResonanceBurst", "Resonance Burst");
        }
        if (ActionName == TEXT("LockOn"))
        {
            return NSLOCTEXT("NARIS", "ControlLockOn", "Lock On");
        }
        if (ActionName == TEXT("Interact"))
        {
            return NSLOCTEXT("NARIS", "ControlInteract", "Interact");
        }
        if (ActionName == TEXT("Sprint"))
        {
            return NSLOCTEXT("NARIS", "ControlSprint", "Sprint");
        }
        if (ActionName == TEXT("EssenceNext"))
        {
            return NSLOCTEXT("NARIS", "ControlEssenceNext", "Next Essence");
        }
        if (ActionName == TEXT("EssencePrevious"))
        {
            return NSLOCTEXT("NARIS", "ControlEssencePrevious", "Previous Essence");
        }
        if (ActionName == TEXT("CompanionMode"))
        {
            return NSLOCTEXT("NARIS", "ControlCompanionMode", "Companion Mode");
        }

        return FText::GetEmpty();
    }

    bool IsReservedGamepadMenuKey(const FKey& Key)
    {
        return Key == EKeys::Gamepad_Special_Right
            || Key == EKeys::Gamepad_FaceButton_Right;
    }

    float StepFrameRate(float Current, int32 Direction)
    {
        static const TArray<float> Limits = {
            30.f, 60.f, 90.f, 120.f, 144.f, 165.f, 240.f, 0.f
        };

        int32 BestIndex = 0;
        float BestDistance = TNumericLimits<float>::Max();
        for (int32 Index = 0; Index < Limits.Num(); ++Index)
        {
            const float Candidate = Limits[Index];
            const float Distance = FMath::Abs(Current - Candidate);
            if (Distance < BestDistance)
            {
                BestDistance = Distance;
                BestIndex = Index;
            }
        }

        const int32 Count = Limits.Num();
        BestIndex = (BestIndex + Direction + Count) % Count;
        return Limits[BestIndex];
    }

    FText BoolText(bool bEnabled)
    {
        return bEnabled
            ? NSLOCTEXT("NARIS", "SettingsOn", "On")
            : NSLOCTEXT("NARIS", "SettingsOff", "Off");
    }

    FText PercentText(float Value)
    {
        const int32 Percent = FMath::RoundToInt(
            FMath::Clamp(Value, 0.f, 2.f) * 100.f
        );
        return FText::Format(
            NSLOCTEXT("NARIS", "SettingsPercentFormat", "{0}%"),
            FText::AsNumber(Percent)
        );
    }
}

ANarisPlayerController::ANarisPlayerController()
{
    bShowMouseCursor = false;
}

void ANarisPlayerController::BeginPlay()
{
    Super::BeginPlay();

    const bool bRuntimeSmoke =
        FParse::Param(FCommandLine::Get(), TEXT("NarisRuntimeSmoke"));
    const bool bSkipFrontEnd =
        FParse::Param(FCommandLine::Get(), TEXT("NarisSkipFrontEnd"));

    bool bBypassOnce = false;
    if (GetWorld())
    {
        if (UGameInstance* GameInstance = GetWorld()->GetGameInstance())
        {
            if (UNarisRuntimeSubsystem* Runtime =
                    GameInstance->GetSubsystem<UNarisRuntimeSubsystem>())
            {
                bBypassOnce = Runtime->ConsumeFrontEndBypassOnce();
            }
        }
    }

    if (!bRuntimeSmoke && !bSkipFrontEnd && !bBypassOnce)
    {
        OpenFrontEndMenu();
    }
}

void ANarisPlayerController::SetupInputComponent()
{
    Super::SetupInputComponent();

    if (!InputComponent)
    {
        return;
    }

    auto BindPausedAction = [this](
        const FName ActionName,
        void (ANarisPlayerController::*Function)()
    )
    {
        FInputActionBinding& Binding = InputComponent->BindAction(
            ActionName,
            IE_Pressed,
            this,
            Function
        );
        Binding.bExecuteWhenPaused = true;
    };

    BindPausedAction(TEXT("MenuUp"), &ANarisPlayerController::MenuUp);
    BindPausedAction(TEXT("MenuDown"), &ANarisPlayerController::MenuDown);
    BindPausedAction(TEXT("MenuLeft"), &ANarisPlayerController::MenuLeft);
    BindPausedAction(TEXT("MenuRight"), &ANarisPlayerController::MenuRight);
    BindPausedAction(TEXT("MenuConfirm"), &ANarisPlayerController::MenuConfirm);
    BindPausedAction(TEXT("MenuBack"), &ANarisPlayerController::MenuBack);
}

bool ANarisPlayerController::InputKey(const FInputKeyParams& Params)
{
    if (Params.Event == IE_Pressed || Params.Event == IE_Repeat)
    {
        bLastInputWasGamepad = Params.IsGamepad();
    }

    if (IsSystemMenuOpen()
        && PauseMenuPage == ENarisPauseMenuPage::Controls
        && bWaitingForGamepadRemap
        && Params.Event == IE_Pressed
        && Params.IsGamepad())
    {
        if (IsReservedGamepadMenuKey(Params.Key))
        {
            CancelGamepadRemap();
            return true;
        }

        if (ApplyGamepadActionRemap(PendingRemapAction, Params.Key, true))
        {
            CancelGamepadRemap();
        }
        return true;
    }

    return Super::InputKey(Params);
}

void ANarisPlayerController::OpenFrontEndMenu()
{
    bFrontEndMenuOpen = true;
    bPauseMenuOpen = false;
    MenuContext = ENarisMenuContext::FrontEnd;
    PauseMenuPage = ENarisPauseMenuPage::Main;
    SelectedMenuIndex = 0;
    CancelGamepadRemap();

    UGameplayStatics::SetGamePaused(this, true);
    ApplyMenuInputMode(true);
}

void ANarisPlayerController::CloseFrontEndMenu()
{
    if (!bFrontEndMenuOpen)
    {
        return;
    }

    bFrontEndMenuOpen = false;
    PauseMenuPage = ENarisPauseMenuPage::Main;
    SelectedMenuIndex = 0;
    CancelGamepadRemap();

    UGameplayStatics::SetGamePaused(this, false);
    ApplyMenuInputMode(false);
}

void ANarisPlayerController::ApplyMenuInputMode(bool bOpen)
{
    bShowMouseCursor = bOpen;

    if (bOpen)
    {
        FInputModeGameAndUI Mode;
        Mode.SetHideCursorDuringCapture(false);
        SetInputMode(Mode);
    }
    else
    {
        SetInputMode(FInputModeGameOnly());
    }
}

void ANarisPlayerController::TogglePauseMenu()
{
    if (bPauseMenuOpen)
    {
        ClosePauseMenu();
    }
    else
    {
        OpenPauseMenu();
    }
}

void ANarisPlayerController::OpenPauseMenu()
{
    if (bPauseMenuOpen || bFrontEndMenuOpen)
    {
        return;
    }

    bPauseMenuOpen = true;
    MenuContext = ENarisMenuContext::Pause;
    PauseMenuPage = ENarisPauseMenuPage::Main;
    SelectedMenuIndex = 0;
    CancelGamepadRemap();

    UGameplayStatics::SetGamePaused(this, true);
    ApplyMenuInputMode(true);
}

void ANarisPlayerController::ClosePauseMenu()
{
    if (!bPauseMenuOpen)
    {
        return;
    }

    bPauseMenuOpen = false;
    PauseMenuPage = ENarisPauseMenuPage::Main;
    SelectedMenuIndex = 0;
    CancelGamepadRemap();

    UGameplayStatics::SetGamePaused(this, false);
    ApplyMenuInputMode(false);
}

bool ANarisPlayerController::CanContinueGame() const
{
    if (!GetWorld())
    {
        return false;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    const UNarisRuntimeSubsystem* Runtime =
        GameInstance
            ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>()
            : nullptr;

    return Runtime
        && !Runtime->DefaultAutoSaveSlot.IsEmpty()
        && UGameplayStatics::DoesSaveGameExist(
            Runtime->DefaultAutoSaveSlot,
            0
        );
}

int32 ANarisPlayerController::GetVisibleMenuItemCount() const
{
    switch (PauseMenuPage)
    {
        case ENarisPauseMenuPage::Main:
            return MenuContext == ENarisMenuContext::FrontEnd
                ? FrontEndMainMenuCount
                : PauseMainMenuCount;
        case ENarisPauseMenuPage::Settings:
            return SettingsMenuCount;
        case ENarisPauseMenuPage::Controls:
            return ControlsMenuCount;
        default:
            return 0;
    }
}

FText ANarisPlayerController::GetMenuTitle() const
{
    switch (PauseMenuPage)
    {
        case ENarisPauseMenuPage::Main:
            return NSLOCTEXT("NARIS", "PauseMenuTitle", "CALL OF NARIS");
        case ENarisPauseMenuPage::Settings:
            return NSLOCTEXT("NARIS", "SettingsMenuTitle", "Settings");
        case ENarisPauseMenuPage::Controls:
            return NSLOCTEXT("NARIS", "ControlsMenuTitle", "Controller Remap");
        default:
            return FText::GetEmpty();
    }
}

FText ANarisPlayerController::GetMenuItemLabel(int32 Index) const
{
    if (PauseMenuPage == ENarisPauseMenuPage::Main)
    {
        if (MenuContext == ENarisMenuContext::FrontEnd)
        {
            switch (Index)
            {
                case 0:
                    return NSLOCTEXT("NARIS", "FrontEndNewGame", "New Game");
                case 1:
                    return NSLOCTEXT("NARIS", "FrontEndContinue", "Continue");
                case 2:
                    return NSLOCTEXT("NARIS", "PauseSettings", "Settings");
                case 3:
                    return NSLOCTEXT("NARIS", "PauseControls", "Controller Remap");
                case 4:
                    return NSLOCTEXT("NARIS", "FrontEndQuit", "Quit");
                default:
                    return FText::GetEmpty();
            }
        }

        switch (Index)
        {
            case 0:
                return NSLOCTEXT("NARIS", "PauseResume", "Resume");
            case 1:
                return NSLOCTEXT("NARIS", "PauseSettings", "Settings");
            case 2:
                return NSLOCTEXT("NARIS", "PauseControls", "Controller Remap");
            default:
                return FText::GetEmpty();
        }
    }

    if (PauseMenuPage == ENarisPauseMenuPage::Controls)
    {
        if (Index >= 0 && Index < ControlActionCount)
        {
            return ControlActionLabel(ControlActionName(Index));
        }

        if (Index == ControlActionCount)
        {
            return NSLOCTEXT(
                "NARIS",
                "ControlsResetDefaults",
                "Reset Controller Defaults"
            );
        }

        if (Index == ControlActionCount + 1)
        {
            return NSLOCTEXT("NARIS", "SettingsBack", "Back");
        }

        return FText::GetEmpty();
    }

    switch (Index)
    {
        case Quality:
            return NSLOCTEXT("NARIS", "SettingsQuality", "Quality Preset");
        case VSync:
            return NSLOCTEXT("NARIS", "SettingsVSync", "VSync");
        case FrameRate:
            return NSLOCTEXT("NARIS", "SettingsFrameRate", "Frame Rate Limit");
        case MasterVolume:
            return NSLOCTEXT("NARIS", "SettingsMasterVolume", "Master Volume");
        case MusicVolume:
            return NSLOCTEXT("NARIS", "SettingsMusicVolume", "Music Volume");
        case SFXVolume:
            return NSLOCTEXT("NARIS", "SettingsSFXVolume", "SFX Volume");
        case VoiceVolume:
            return NSLOCTEXT("NARIS", "SettingsVoiceVolume", "Voice Volume");
        case CameraShake:
            return NSLOCTEXT("NARIS", "SettingsCameraShake", "Camera Shake");
        case ReduceCameraShake:
            return NSLOCTEXT("NARIS", "SettingsReduceCameraShake", "Reduce Camera Shake");
        case Subtitles:
            return NSLOCTEXT("NARIS", "SettingsSubtitles", "Subtitles");
        case SubtitleScale:
            return NSLOCTEXT("NARIS", "SettingsSubtitleScale", "Subtitle Scale");
        case HighContrast:
            return NSLOCTEXT("NARIS", "SettingsHighContrast", "High Contrast Interactions");
        case ColorVision:
            return NSLOCTEXT("NARIS", "SettingsColorVision", "Color Vision Mode");
        case ColorVisionSeverity:
            return NSLOCTEXT("NARIS", "SettingsColorVisionSeverity", "Color Vision Severity");
        case ApplySave:
            return NSLOCTEXT("NARIS", "SettingsApplySave", "Apply & Save");
        case ResetDefaults:
            return NSLOCTEXT("NARIS", "SettingsResetDefaults", "Reset Defaults");
        case Back:
            return NSLOCTEXT("NARIS", "SettingsBack", "Back");
        default:
            return FText::GetEmpty();
    }
}

FText ANarisPlayerController::GetMenuItemValue(int32 Index) const
{
    if (PauseMenuPage == ENarisPauseMenuPage::Main)
    {
        if (MenuContext == ENarisMenuContext::FrontEnd
            && Index == 1
            && !CanContinueGame())
        {
            return NSLOCTEXT("NARIS", "FrontEndNoSave", "No Save Data");
        }

        return FText::GetEmpty();
    }

    if (PauseMenuPage == ENarisPauseMenuPage::Controls)
    {
        if (Index >= 0 && Index < ControlActionCount)
        {
            const FName ActionName = ControlActionName(Index);
            if (bWaitingForGamepadRemap
                && PendingRemapAction == ActionName
                && SelectedMenuIndex == Index)
            {
                return NSLOCTEXT(
                    "NARIS",
                    "ControlsPressButton",
                    "Press a gamepad button..."
                );
            }

            const FKey Key = GetCurrentGamepadKey(ActionName);
            return Key.IsValid()
                ? Key.GetDisplayName()
                : NSLOCTEXT("NARIS", "ControlsUnbound", "Unbound");
        }

        return FText::GetEmpty();
    }

    const UNarisGameUserSettings* Settings =
        UNarisGameUserSettings::GetNarisGameUserSettings();
    if (!Settings)
    {
        return FText::GetEmpty();
    }

    switch (Index)
    {
        case Quality:
        {
            switch (Settings->GetOverallScalabilityLevel())
            {
                case 0:
                    return NSLOCTEXT("NARIS", "QualityLow", "Low");
                case 1:
                    return NSLOCTEXT("NARIS", "QualityMedium", "Medium");
                case 2:
                    return NSLOCTEXT("NARIS", "QualityHigh", "High");
                case 3:
                    return NSLOCTEXT("NARIS", "QualityEpic", "Epic");
                case 4:
                    return NSLOCTEXT("NARIS", "QualityCinematic", "Cinematic");
                default:
                    return NSLOCTEXT("NARIS", "QualityCustom", "Custom");
            }
        }
        case VSync:
            return BoolText(Settings->IsVSyncEnabled());
        case FrameRate:
        {
            const float Limit = Settings->GetFrameRateLimit();
            if (Limit <= 0.f)
            {
                return NSLOCTEXT("NARIS", "FrameRateUnlimited", "Unlimited");
            }
            return FText::Format(
                NSLOCTEXT("NARIS", "FrameRateFormat", "{0} FPS"),
                FText::AsNumber(FMath::RoundToInt(Limit))
            );
        }
        case MasterVolume:
            return PercentText(Settings->MasterVolume);
        case MusicVolume:
            return PercentText(Settings->MusicVolume);
        case SFXVolume:
            return PercentText(Settings->SFXVolume);
        case VoiceVolume:
            return PercentText(Settings->VoiceVolume);
        case CameraShake:
            return PercentText(Settings->CameraShakeIntensity);
        case ReduceCameraShake:
            return BoolText(Settings->bReduceCameraShake);
        case Subtitles:
            return BoolText(Settings->bSubtitlesEnabled);
        case SubtitleScale:
            return PercentText(Settings->SubtitleScale);
        case HighContrast:
            return BoolText(Settings->bHighContrastInteractions);
        case ColorVision:
            switch (Settings->ColorVisionMode)
            {
                case ENarisColorVisionMode::Deuteranopia:
                    return NSLOCTEXT("NARIS", "ColorVisionDeuteranopia", "Deuteranopia");
                case ENarisColorVisionMode::Protanopia:
                    return NSLOCTEXT("NARIS", "ColorVisionProtanopia", "Protanopia");
                case ENarisColorVisionMode::Tritanopia:
                    return NSLOCTEXT("NARIS", "ColorVisionTritanopia", "Tritanopia");
                case ENarisColorVisionMode::Normal:
                default:
                    return NSLOCTEXT("NARIS", "ColorVisionNormal", "Normal");
            }
        case ColorVisionSeverity:
            return PercentText(Settings->ColorVisionSeverity);
        default:
            return FText::GetEmpty();
    }
}

void ANarisPlayerController::MenuUp()
{
    if (bWaitingForGamepadRemap)
    {
        return;
    }

    if (!IsSystemMenuOpen())
    {
        return;
    }

    const int32 Count = GetVisibleMenuItemCount();
    SelectedMenuIndex = (SelectedMenuIndex - 1 + Count) % Count;
}

void ANarisPlayerController::MenuDown()
{
    if (bWaitingForGamepadRemap)
    {
        return;
    }

    if (!IsSystemMenuOpen())
    {
        return;
    }

    const int32 Count = GetVisibleMenuItemCount();
    SelectedMenuIndex = (SelectedMenuIndex + 1) % Count;
}

void ANarisPlayerController::MenuLeft()
{
    if (!bWaitingForGamepadRemap
        && IsSystemMenuOpen()
        && PauseMenuPage == ENarisPauseMenuPage::Settings)
    {
        AdjustCurrentSetting(-1);
    }
}

void ANarisPlayerController::MenuRight()
{
    if (!bWaitingForGamepadRemap
        && IsSystemMenuOpen()
        && PauseMenuPage == ENarisPauseMenuPage::Settings)
    {
        AdjustCurrentSetting(1);
    }
}

void ANarisPlayerController::MenuConfirm()
{
    if (!IsSystemMenuOpen())
    {
        return;
    }

    if (PauseMenuPage == ENarisPauseMenuPage::Main)
    {
        if (MenuContext == ENarisMenuContext::FrontEnd)
        {
            switch (SelectedMenuIndex)
            {
                case 0:
                    StartNewGameFromMenu();
                    break;
                case 1:
                    ContinueGameFromMenu();
                    break;
                case 2:
                    PauseMenuPage = ENarisPauseMenuPage::Settings;
                    SelectedMenuIndex = 0;
                    break;
                case 3:
                    PauseMenuPage = ENarisPauseMenuPage::Controls;
                    SelectedMenuIndex = 0;
                    break;
                case 4:
                    QuitGameFromMenu();
                    break;
                default:
                    break;
            }
            return;
        }

        if (SelectedMenuIndex == 0)
        {
            ClosePauseMenu();
        }
        else if (SelectedMenuIndex == 1)
        {
            PauseMenuPage = ENarisPauseMenuPage::Settings;
            SelectedMenuIndex = 0;
        }
        else if (SelectedMenuIndex == 2)
        {
            PauseMenuPage = ENarisPauseMenuPage::Controls;
            SelectedMenuIndex = 0;
        }
        return;
    }

    if (PauseMenuPage == ENarisPauseMenuPage::Controls)
    {
        if (bWaitingForGamepadRemap)
        {
            return;
        }

        if (SelectedMenuIndex >= 0
            && SelectedMenuIndex < ControlActionCount)
        {
            BeginGamepadRemap(ControlActionName(SelectedMenuIndex));
        }
        else if (SelectedMenuIndex == ControlActionCount)
        {
            ResetGamepadActionRemaps();
        }
        else if (SelectedMenuIndex == ControlActionCount + 1)
        {
            PauseMenuPage = ENarisPauseMenuPage::Main;
            SelectedMenuIndex = 0;
        }
        return;
    }

    switch (SelectedMenuIndex)
    {
        case VSync:
        case ReduceCameraShake:
        case Subtitles:
        case HighContrast:
            AdjustCurrentSetting(1);
            break;
        case ApplySave:
            ApplyCurrentSettings();
            break;
        case ResetDefaults:
            ResetCurrentSettings();
            break;
        case Back:
            PauseMenuPage = ENarisPauseMenuPage::Main;
            SelectedMenuIndex = 0;
            break;
        default:
            break;
    }
}

void ANarisPlayerController::MenuBack()
{
    if (!IsSystemMenuOpen())
    {
        return;
    }

    if (bWaitingForGamepadRemap)
    {
        CancelGamepadRemap();
        return;
    }

    if (PauseMenuPage == ENarisPauseMenuPage::Settings
        || PauseMenuPage == ENarisPauseMenuPage::Controls)
    {
        PauseMenuPage = ENarisPauseMenuPage::Main;
        SelectedMenuIndex = 0;
        return;
    }

    if (MenuContext == ENarisMenuContext::FrontEnd)
    {
        return;
    }

    ClosePauseMenu();
}

void ANarisPlayerController::AdjustCurrentSetting(int32 Direction)
{
    UNarisGameUserSettings* Settings =
        UNarisGameUserSettings::GetNarisGameUserSettings();
    if (!Settings || Direction == 0)
    {
        return;
    }

    const float FloatStep = 0.1f;

    switch (SelectedMenuIndex)
    {
        case Quality:
        {
            int32 Level = Settings->GetOverallScalabilityLevel();
            if (Level < 0)
            {
                Level = 3;
            }
            Level = (Level + Direction + 5) % 5;
            Settings->SetQualityPreset(Level);
            break;
        }
        case VSync:
            Settings->SetVSyncEnabled(!Settings->IsVSyncEnabled());
            break;
        case FrameRate:
            Settings->SetFrameRateLimit(
                StepFrameRate(Settings->GetFrameRateLimit(), Direction)
            );
            break;
        case MasterVolume:
            Settings->SetMasterVolume(Settings->MasterVolume + FloatStep * Direction);
            break;
        case MusicVolume:
            Settings->SetMusicVolume(Settings->MusicVolume + FloatStep * Direction);
            break;
        case SFXVolume:
            Settings->SetSFXVolume(Settings->SFXVolume + FloatStep * Direction);
            break;
        case VoiceVolume:
            Settings->SetVoiceVolume(Settings->VoiceVolume + FloatStep * Direction);
            break;
        case CameraShake:
            Settings->SetCameraShakeIntensity(
                Settings->CameraShakeIntensity + FloatStep * Direction
            );
            break;
        case ReduceCameraShake:
            Settings->SetReduceCameraShake(!Settings->bReduceCameraShake);
            break;
        case Subtitles:
            Settings->SetSubtitlesEnabled(!Settings->bSubtitlesEnabled);
            break;
        case SubtitleScale:
            Settings->SetSubtitleScale(
                Settings->SubtitleScale + FloatStep * Direction
            );
            break;
        case HighContrast:
            Settings->SetHighContrastInteractions(
                !Settings->bHighContrastInteractions
            );
            break;
        case ColorVision:
        {
            const int32 Count = 4;
            int32 Mode = static_cast<int32>(Settings->ColorVisionMode);
            Mode = (Mode + Direction + Count) % Count;
            Settings->SetColorVisionMode(
                static_cast<ENarisColorVisionMode>(Mode),
                Settings->ColorVisionSeverity,
                Settings->bCorrectColorVisionDeficiency
            );
            break;
        }
        case ColorVisionSeverity:
            Settings->SetColorVisionMode(
                Settings->ColorVisionMode,
                Settings->ColorVisionSeverity + FloatStep * Direction,
                Settings->bCorrectColorVisionDeficiency
            );
            break;
        default:
            break;
    }

    Settings->ApplyNonResolutionSettings();
}

void ANarisPlayerController::ApplyCurrentSettings()
{
    if (UNarisGameUserSettings* Settings =
            UNarisGameUserSettings::GetNarisGameUserSettings())
    {
        Settings->ApplyAndSave(true);
    }
}

void ANarisPlayerController::ResetCurrentSettings()
{
    if (UNarisGameUserSettings* Settings =
            UNarisGameUserSettings::GetNarisGameUserSettings())
    {
        Settings->SetToDefaults();
        Settings->ApplyAndSave(true);
    }
}


FText ANarisPlayerController::GetActionKeyDisplayName(
    FName ActionName
) const
{
    if (ActionName.IsNone())
    {
        return FText::GetEmpty();
    }

    if (bLastInputWasGamepad)
    {
        const FKey GamepadKey = GetCurrentGamepadKey(ActionName);
        return GamepadKey.IsValid()
            ? GamepadKey.GetDisplayName()
            : FText::FromName(ActionName);
    }

    const UInputSettings* InputSettings = UInputSettings::GetInputSettings();
    if (InputSettings)
    {
        TArray<FInputActionKeyMapping> Mappings;
        InputSettings->GetActionMappingByName(ActionName, Mappings);

        for (const FInputActionKeyMapping& Mapping : Mappings)
        {
            if (Mapping.Key.IsValid() && !Mapping.Key.IsGamepadKey())
            {
                return Mapping.Key.GetDisplayName();
            }
        }
    }

    return FText::FromName(ActionName);
}

FKey ANarisPlayerController::GetCurrentGamepadKey(FName ActionName) const
{
    if (ActionName.IsNone())
    {
        return EKeys::Invalid;
    }

    const UInputSettings* InputSettings = UInputSettings::GetInputSettings();
    if (!InputSettings)
    {
        return DefaultGamepadKey(ActionName);
    }

    TArray<FInputActionKeyMapping> Mappings;
    InputSettings->GetActionMappingByName(ActionName, Mappings);

    for (const FInputActionKeyMapping& Mapping : Mappings)
    {
        if (Mapping.Key.IsGamepadKey())
        {
            return Mapping.Key;
        }
    }

    return DefaultGamepadKey(ActionName);
}

void ANarisPlayerController::BeginGamepadRemap(FName ActionName)
{
    if (ActionName.IsNone())
    {
        return;
    }

    bWaitingForGamepadRemap = true;
    PendingRemapAction = ActionName;
}

void ANarisPlayerController::CancelGamepadRemap()
{
    bWaitingForGamepadRemap = false;
    PendingRemapAction = NAME_None;
}

bool ANarisPlayerController::ApplyGamepadActionRemap(
    FName ActionName,
    FKey NewKey,
    bool bPersist
)
{
    if (ActionName.IsNone()
        || !NewKey.IsValid()
        || !NewKey.IsGamepadKey()
        || IsReservedGamepadMenuKey(NewKey))
    {
        return false;
    }

    UInputSettings* InputSettings = UInputSettings::GetInputSettings();
    if (!InputSettings)
    {
        return false;
    }

    const TArray<FInputActionKeyMapping>& AllMappings =
        InputSettings->GetActionMappings();

    for (const FInputActionKeyMapping& Mapping : AllMappings)
    {
        if (Mapping.Key != NewKey
            || Mapping.ActionName == ActionName
            || !Mapping.Key.IsGamepadKey())
        {
            continue;
        }

        bool bOtherGameplayAction = false;
        for (int32 Index = 0; Index < ControlActionCount; ++Index)
        {
            if (ControlActionName(Index) == Mapping.ActionName)
            {
                bOtherGameplayAction = true;
                break;
            }
        }

        if (bOtherGameplayAction)
        {
            return false;
        }
    }

    TArray<FInputActionKeyMapping> CurrentMappings;
    InputSettings->GetActionMappingByName(ActionName, CurrentMappings);

    for (const FInputActionKeyMapping& Mapping : CurrentMappings)
    {
        if (Mapping.Key.IsGamepadKey())
        {
            InputSettings->RemoveActionMapping(Mapping, false);
        }
    }

    InputSettings->AddActionMapping(
        FInputActionKeyMapping(
            ActionName,
            NewKey,
            false,
            false,
            false,
            false
        ),
        false
    );

    if (bPersist)
    {
        InputSettings->SaveKeyMappings();
        InputSettings->ForceRebuildKeymaps();
    }

    return true;
}

void ANarisPlayerController::ResetGamepadActionRemaps()
{
    UInputSettings* InputSettings = UInputSettings::GetInputSettings();
    if (!InputSettings)
    {
        return;
    }

    for (int32 Index = 0; Index < ControlActionCount; ++Index)
    {
        const FName ActionName = ControlActionName(Index);

        TArray<FInputActionKeyMapping> CurrentMappings;
        InputSettings->GetActionMappingByName(ActionName, CurrentMappings);
        for (const FInputActionKeyMapping& Mapping : CurrentMappings)
        {
            if (Mapping.Key.IsGamepadKey())
            {
                InputSettings->RemoveActionMapping(Mapping, false);
            }
        }
    }

    for (int32 Index = 0; Index < ControlActionCount; ++Index)
    {
        const FName ActionName = ControlActionName(Index);
        const FKey DefaultKey = DefaultGamepadKey(ActionName);
        if (!ActionName.IsNone() && DefaultKey.IsValid())
        {
            InputSettings->AddActionMapping(
                FInputActionKeyMapping(
                    ActionName,
                    DefaultKey,
                    false,
                    false,
                    false,
                    false
                ),
                false
            );
        }
    }

    InputSettings->SaveKeyMappings();
    InputSettings->ForceRebuildKeymaps();
    CancelGamepadRemap();
}


void ANarisPlayerController::StartNewGameFromMenu()
{
    if (!GetWorld())
    {
        return;
    }

    UGameInstance* GameInstance = GetWorld()->GetGameInstance();
    UNarisRuntimeSubsystem* Runtime =
        GameInstance
            ? GameInstance->GetSubsystem<UNarisRuntimeSubsystem>()
            : nullptr;

    if (!Runtime)
    {
        return;
    }

    Runtime->BeginNewGame();
    if (!Runtime->SaveState(Runtime->DefaultAutoSaveSlot))
    {
        return;
    }

    Runtime->RequestFrontEndBypassOnce();

    const FString CurrentLevel =
        UGameplayStatics::GetCurrentLevelName(this, true);
    if (CurrentLevel.IsEmpty())
    {
        return;
    }

    UGameplayStatics::OpenLevel(this, FName(*CurrentLevel));
}

void ANarisPlayerController::ContinueGameFromMenu()
{
    if (!CanContinueGame())
    {
        return;
    }

    CloseFrontEndMenu();
}

void ANarisPlayerController::QuitGameFromMenu()
{
    UKismetSystemLibrary::QuitGame(
        this,
        this,
        EQuitPreference::Quit,
        false
    );
}
