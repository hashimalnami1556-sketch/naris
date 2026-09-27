#include "NarisUserSettingsSubsystem.h"
#include "GameFramework/GameUserSettings.h"
#include "Misc/ConfigCacheIni.h"

namespace
{
const TCHAR* SettingsSection = TEXT("NARIS.UserSettings");
}

void UNarisUserSettingsSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
 Super::Initialize(Collection);
 LoadPersistentSettings();
}

void UNarisUserSettingsSubsystem::Deinitialize()
{
 SavePersistentSettings();
 Super::Deinitialize();
}

void UNarisUserSettingsSubsystem::LoadPersistentSettings()
{
 if (!GConfig) return;
 GConfig->GetFloat(SettingsSection,TEXT("MasterVolume"),MasterVolume,GGameUserSettingsIni);
 GConfig->GetFloat(SettingsSection,TEXT("MusicVolume"),MusicVolume,GGameUserSettingsIni);
 GConfig->GetFloat(SettingsSection,TEXT("SFXVolume"),SFXVolume,GGameUserSettingsIni);
 GConfig->GetBool(SettingsSection,TEXT("Subtitles"),Accessibility.bSubtitles,GGameUserSettingsIni);
 GConfig->GetBool(SettingsSection,TEXT("HighContrastHUD"),Accessibility.bHighContrastHUD,GGameUserSettingsIni);
 GConfig->GetBool(SettingsSection,TEXT("ReducedCameraMotion"),Accessibility.bReducedCameraMotion,GGameUserSettingsIni);
 GConfig->GetBool(SettingsSection,TEXT("HoldToBlock"),Accessibility.bHoldToBlock,GGameUserSettingsIni);
 GConfig->GetFloat(SettingsSection,TEXT("UIScale"),Accessibility.UIScale,GGameUserSettingsIni);
 GConfig->GetFloat(SettingsSection,TEXT("AimAssistStrength"),Accessibility.AimAssistStrength,GGameUserSettingsIni);
 MasterVolume=FMath::Clamp(MasterVolume,0.f,1.f);
 MusicVolume=FMath::Clamp(MusicVolume,0.f,1.f);
 SFXVolume=FMath::Clamp(SFXVolume,0.f,1.f);
 Accessibility.UIScale=FMath::Clamp(Accessibility.UIScale,.75f,1.5f);
 Accessibility.AimAssistStrength=FMath::Clamp(Accessibility.AimAssistStrength,0.f,1.f);
}

void UNarisUserSettingsSubsystem::SavePersistentSettings() const
{
 if (!GConfig) return;
 GConfig->SetFloat(SettingsSection,TEXT("MasterVolume"),MasterVolume,GGameUserSettingsIni);
 GConfig->SetFloat(SettingsSection,TEXT("MusicVolume"),MusicVolume,GGameUserSettingsIni);
 GConfig->SetFloat(SettingsSection,TEXT("SFXVolume"),SFXVolume,GGameUserSettingsIni);
 GConfig->SetBool(SettingsSection,TEXT("Subtitles"),Accessibility.bSubtitles,GGameUserSettingsIni);
 GConfig->SetBool(SettingsSection,TEXT("HighContrastHUD"),Accessibility.bHighContrastHUD,GGameUserSettingsIni);
 GConfig->SetBool(SettingsSection,TEXT("ReducedCameraMotion"),Accessibility.bReducedCameraMotion,GGameUserSettingsIni);
 GConfig->SetBool(SettingsSection,TEXT("HoldToBlock"),Accessibility.bHoldToBlock,GGameUserSettingsIni);
 GConfig->SetFloat(SettingsSection,TEXT("UIScale"),Accessibility.UIScale,GGameUserSettingsIni);
 GConfig->SetFloat(SettingsSection,TEXT("AimAssistStrength"),Accessibility.AimAssistStrength,GGameUserSettingsIni);
 GConfig->Flush(false,GGameUserSettingsIni);
}

void UNarisUserSettingsSubsystem::ApplyQualityPreset(int32 Preset)
{
 if (UGameUserSettings* Settings=UGameUserSettings::GetGameUserSettings())
 {
  Settings->SetOverallScalabilityLevel(FMath::Clamp(Preset,0,4));
  Settings->ApplySettings(false);
  Settings->SaveSettings();
 }
}
void UNarisUserSettingsSubsystem::SetMasterVolume(float Value)
{
 MasterVolume=FMath::Clamp(Value,0.f,1.f);
 SavePersistentSettings();
}

void UNarisUserSettingsSubsystem::SetMusicVolume(float Value)
{
 MusicVolume=FMath::Clamp(Value,0.f,1.f);
 SavePersistentSettings();
}

void UNarisUserSettingsSubsystem::SetSFXVolume(float Value)
{
 SFXVolume=FMath::Clamp(Value,0.f,1.f);
 SavePersistentSettings();
}

void UNarisUserSettingsSubsystem::SetAccessibility(const FNarisAccessibilitySettings& InSettings)
{
 Accessibility=InSettings;
 Accessibility.UIScale=FMath::Clamp(Accessibility.UIScale,.75f,1.5f);
 Accessibility.AimAssistStrength=FMath::Clamp(Accessibility.AimAssistStrength,0.f,1.f);
 SavePersistentSettings();
}