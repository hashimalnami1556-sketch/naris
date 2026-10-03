#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "NarisGameplayTypes.h"
#include "NarisWorldStateSubsystem.generated.h"

UCLASS()
class NARIS_W04_API UNarisWorldStateSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    virtual void Initialize(FSubsystemCollectionBase& Collection) override;

    UFUNCTION(BlueprintPure, Category="NARIS|World")
    float GetWorldHour() const { return WorldHour; }

    UFUNCTION(BlueprintPure, Category="NARIS|World")
    int32 GetWorldDay() const { return WorldDay; }

    UFUNCTION(BlueprintPure, Category="NARIS|World")
    ENarisWeatherState GetWeatherState() const { return WeatherState; }

    UFUNCTION(BlueprintCallable, Category="NARIS|World")
    void SetWorldHour(float InHour, bool bPersist = true);

    UFUNCTION(BlueprintCallable, Category="NARIS|World")
    void AdvanceGameHours(float DeltaHours, bool bPersist = true);

    UFUNCTION(BlueprintCallable, Category="NARIS|World")
    void SetWeatherState(ENarisWeatherState NewState, bool bPersist = true);

    UFUNCTION(BlueprintPure, Category="NARIS|World")
    bool IsStormWeather() const;

    UFUNCTION(BlueprintCallable, Category="NARIS|World")
    void BroadcastWorldStateToNPCs();

private:
    void PullFromRuntime();
    void PushToRuntimeAndSave(bool bPersist);

    float WorldHour = 8.f;
    int32 WorldDay = 1;
    ENarisWeatherState WeatherState = ENarisWeatherState::Clear;
};
