#include "NarisWeatherEnvironmentSubsystem.h"

#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "NarisGameplayTypes.h"
#include "NarisWorldStateSubsystem.h"
#include "TimerManager.h"

void UNarisWeatherEnvironmentSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);

    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().SetTimer(
            UpdateTimer,
            this,
            &UNarisWeatherEnvironmentSubsystem::UpdateEnvironmentState,
            FMath::Clamp(UpdateIntervalSeconds, 0.25f, 10.f),
            true
        );
    }

    UpdateEnvironmentState();
}

void UNarisWeatherEnvironmentSubsystem::Deinitialize()
{
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(UpdateTimer);
    }
    Super::Deinitialize();
}

void UNarisWeatherEnvironmentSubsystem::UpdateEnvironmentState()
{
    UGameInstance* GI = GetGameInstance();
    UNarisWorldStateSubsystem* WorldState =
        GI ? GI->GetSubsystem<UNarisWorldStateSubsystem>() : nullptr;
    if (!WorldState)
    {
        return;
    }

    const ENarisWeatherState Weather = WorldState->GetWeatherState();
    const float Dt = FMath::Clamp(UpdateIntervalSeconds, 0.25f, 10.f);

    const bool bSnowing =
        Weather == ENarisWeatherState::Snow ||
        Weather == ENarisWeatherState::Blizzard;

    const bool bRaining =
        Weather == ENarisWeatherState::Rain ||
        Weather == ENarisWeatherState::HeavyRain ||
        Weather == ENarisWeatherState::Thunderstorm;

    const float SnowTarget = bSnowing ? 1.f : 0.f;
    const float WetTarget = bRaining ? 1.f : 0.f;
    const float MudTarget = bRaining ? 1.f : 0.f;

    SnowLevel = FMath::FInterpTo(
        SnowLevel,
        SnowTarget,
        Dt,
        bSnowing ? SnowBuildPerSecond : SnowMeltPerSecond
    );
    Wetness = FMath::FInterpTo(
        Wetness,
        WetTarget,
        Dt,
        bRaining ? WetBuildPerSecond : WetDryPerSecond
    );
    Mud = FMath::FInterpTo(
        Mud,
        MudTarget,
        Dt,
        bRaining ? MudBuildPerSecond : MudDryPerSecond
    );

    switch (Weather)
    {
        case ENarisWeatherState::Thunderstorm:
            WindStrength = 20.f;
            break;
        case ENarisWeatherState::Blizzard:
            WindStrength = 25.f;
            break;
        case ENarisWeatherState::Sandstorm:
            WindStrength = 22.f;
            break;
        case ENarisWeatherState::AshStorm:
            WindStrength = 18.f;
            break;
        case ENarisWeatherState::VoidStorm:
            WindStrength = 26.f;
            break;
        case ENarisWeatherState::HeavyRain:
            WindStrength = 12.f;
            break;
        case ENarisWeatherState::Snow:
            WindStrength = 7.f;
            break;
        default:
            WindStrength = 2.f;
            break;
    }

    SnowLevel = FMath::Clamp(SnowLevel, 0.f, 1.f);
    Wetness = FMath::Clamp(Wetness, 0.f, 1.f);
    Mud = FMath::Clamp(Mud, 0.f, 1.f);
}
