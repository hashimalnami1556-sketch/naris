#include "NarisPlayerController.h"

#include "Components/InputComponent.h"
#include "Kismet/GameplayStatics.h"
#include "NarisGameUserSettings.h"

namespace
{
    constexpr int32 MainMenuCount = 2;
    constexpr int32 SettingsMenuCount = 17;

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
    if (bPauseMenuOpen)
    {
        return;
    }

    bPauseMenuOpen = true;
    PauseMenuPage = ENarisPauseMenuPage::Main;
    SelectedMenuIndex = 0;

    UGameplayStatics::SetGamePaused(this, true);

    bShowMouseCursor = true;
    FInputModeGameAndUI Mode;
    Mode.SetHideCursorDuringCapture(false);
    SetInputMode(Mode);
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

    UGameplayStatics::SetGamePaused(this, false);

    bShowMouseCursor = false;
    SetInputMode(FInputModeGameOnly());
}

int32 ANarisPlayerController::GetVisibleMenuItemCount() const
{
    return PauseMenuPage == ENarisPauseMenuPage::Main
        ? MainMenuCount
        : SettingsMenuCount;
}

FText ANarisPlayerController::GetMenuTitle() const
{
    return PauseMenuPage == ENarisPauseMenuPage::Main
        ? NSLOCTEXT("NARIS", "PauseMenuTitle", "CALL OF NARIS")
        : NSLOCTEXT("NARIS", "SettingsMenuTitle", "Settings");
}

FText ANarisPlayerController::GetMenuItemLabel(int32 Index) const
{
    if (PauseMenuPage == ENarisPauseMenuPage::Main)
    {
        switch (Index)
        {
            case 0:
                return NSLOCTEXT("NARIS", "PauseResume", "Resume");
            case 1:
                return NSLOCTEXT("NARIS", "PauseSettings", "Settings");
            default:
                return FText::GetEmpty();
        }
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
    if (!bPauseMenuOpen)
    {
        return;
    }

    const int32 Count = GetVisibleMenuItemCount();
    SelectedMenuIndex = (SelectedMenuIndex - 1 + Count) % Count;
}

void ANarisPlayerController::MenuDown()
{
    if (!bPauseMenuOpen)
    {
        return;
    }

    const int32 Count = GetVisibleMenuItemCount();
    SelectedMenuIndex = (SelectedMenuIndex + 1) % Count;
}

void ANarisPlayerController::MenuLeft()
{
    if (bPauseMenuOpen && PauseMenuPage == ENarisPauseMenuPage::Settings)
    {
        AdjustCurrentSetting(-1);
    }
}

void ANarisPlayerController::MenuRight()
{
    if (bPauseMenuOpen && PauseMenuPage == ENarisPauseMenuPage::Settings)
    {
        AdjustCurrentSetting(1);
    }
}

void ANarisPlayerController::MenuConfirm()
{
    if (!bPauseMenuOpen)
    {
        return;
    }

    if (PauseMenuPage == ENarisPauseMenuPage::Main)
    {
        if (SelectedMenuIndex == 0)
        {
            ClosePauseMenu();
        }
        else if (SelectedMenuIndex == 1)
        {
            PauseMenuPage = ENarisPauseMenuPage::Settings;
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
    if (!bPauseMenuOpen)
    {
        return;
    }

    if (PauseMenuPage == ENarisPauseMenuPage::Settings)
    {
        PauseMenuPage = ENarisPauseMenuPage::Main;
        SelectedMenuIndex = 0;
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
