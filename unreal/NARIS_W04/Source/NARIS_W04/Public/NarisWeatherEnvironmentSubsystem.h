#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NarisWeatherEnvironmentSubsystem.generated.h"

UCLASS()
class NARIS_W04_API UNarisWeatherEnvironmentSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;
    virtual void Deinitialize() override;

    UFUNCTION(BlueprintPure, Category="NARIS|Weather")
    float GetSnowLevel() const { return SnowLevel; }

    UFUNCTION(BlueprintPure, Category="NARIS|Weather")
    float GetWetness() const { return Wetness; }

    UFUNCTION(BlueprintPure, Category="NARIS|Weather")
    float GetMud() const { return Mud; }

    UFUNCTION(BlueprintPure, Category="NARIS|Weather")
    float GetWindStrength() const { return WindStrength; }

    UFUNCTION(BlueprintCallable, Category="NARIS|Weather")
    void UpdateEnvironmentState();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Weather")
    float UpdateIntervalSeconds = 1.f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Weather")
    float SnowBuildPerSecond = 0.04f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Weather")
    float SnowMeltPerSecond = 0.015f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Weather")
    float WetBuildPerSecond = 0.15f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Weather")
    float WetDryPerSecond = 0.05f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Weather")
    float MudBuildPerSecond = 0.08f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="NARIS|Weather")
    float MudDryPerSecond = 0.025f;

private:
    FTimerHandle UpdateTimer;
    float SnowLevel = 0.f;
    float Wetness = 0.f;
    float Mud = 0.f;
    float WindStrength = 0.f;
};
