#pragma once
#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NarisUserSettingsSubsystem.generated.h"
USTRUCT(BlueprintType)
struct FNarisAccessibilitySettings
{
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite) bool bSubtitles=true;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) bool bHighContrastHUD=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) bool bReducedCameraMotion=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) bool bHoldToBlock=true;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float UIScale=1.f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float AimAssistStrength=.35f;
};
UCLASS()
class NARISCORE_API UNarisUserSettingsSubsystem : public UGameInstanceSubsystem
{
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable) void ApplyQualityPreset(int32 Preset);
 UFUNCTION(BlueprintCallable) void SetMasterVolume(float Value);
 UFUNCTION(BlueprintCallable) void SetMusicVolume(float Value);
 UFUNCTION(BlueprintCallable) void SetSFXVolume(float Value);
 UFUNCTION(BlueprintCallable) void SetAccessibility(const FNarisAccessibilitySettings& InSettings);
 UFUNCTION(BlueprintPure) FNarisAccessibilitySettings GetAccessibility() const{return Accessibility;}
 UFUNCTION(BlueprintPure) float GetMasterVolume() const{return MasterVolume;}
private:
 UPROPERTY() FNarisAccessibilitySettings Accessibility;
 float MasterVolume=1.f,MusicVolume=.8f,SFXVolume=1.f;
};