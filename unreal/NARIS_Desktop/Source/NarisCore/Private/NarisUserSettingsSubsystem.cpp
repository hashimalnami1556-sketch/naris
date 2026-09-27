#include "NarisUserSettingsSubsystem.h"
#include "GameFramework/GameUserSettings.h"
void UNarisUserSettingsSubsystem::ApplyQualityPreset(int32 P){if(UGameUserSettings* S=UGameUserSettings::GetGameUserSettings()){S->SetOverallScalabilityLevel(FMath::Clamp(P,0,4));S->ApplySettings(false);}}
void UNarisUserSettingsSubsystem::SetMasterVolume(float V){MasterVolume=FMath::Clamp(V,0.f,1.f);}
void UNarisUserSettingsSubsystem::SetMusicVolume(float V){MusicVolume=FMath::Clamp(V,0.f,1.f);}
void UNarisUserSettingsSubsystem::SetSFXVolume(float V){SFXVolume=FMath::Clamp(V,0.f,1.f);}
void UNarisUserSettingsSubsystem::SetAccessibility(const FNarisAccessibilitySettings& S){Accessibility=S;Accessibility.UIScale=FMath::Clamp(Accessibility.UIScale,.75f,1.5f);Accessibility.AimAssistStrength=FMath::Clamp(Accessibility.AimAssistStrength,0.f,1.f);}
