#include "NarisWorldStateSubsystem.h"

#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "NarisDailyNPC.h"
#include "NarisRuntimeSubsystem.h"

void UNarisWorldStateSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    PullFromRuntime();
}

void UNarisWorldStateSubsystem::PullFromRuntime()
{
    UGameInstance* GI = GetGameInstance();
    UNarisRuntimeSubsystem* Runtime = GI ? GI->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;
    if (!Runtime)
    {
        return;
    }

    const FNarisSaveState State = Runtime->GetState();
    WorldHour = FMath::Fmod(FMath::Fmod(State.WorldHour, 24.f) + 24.f, 24.f);
    WorldDay = FMath::Max(1, State.WorldDay);
    WeatherState = State.WeatherState;
}

void UNarisWorldStateSubsystem::PushToRuntimeAndSave(bool bPersist)
{
    UGameInstance* GI = GetGameInstance();
    UNarisRuntimeSubsystem* Runtime = GI ? GI->GetSubsystem<UNarisRuntimeSubsystem>() : nullptr;
    if (!Runtime)
    {
        return;
    }

    Runtime->SetWorldStateSnapshot(WorldHour, WorldDay, WeatherState);
    if (bPersist)
    {
        Runtime->SaveState(Runtime->DefaultAutoSaveSlot);
    }
}

void UNarisWorldStateSubsystem::SetWorldHour(float InHour, bool bPersist)
{
    if (!FMath::IsFinite(InHour))
    {
        return;
    }

    WorldHour = FMath::Fmod(FMath::Fmod(InHour, 24.f) + 24.f, 24.f);
    PushToRuntimeAndSave(bPersist);
    BroadcastWorldStateToNPCs();
}

void UNarisWorldStateSubsystem::AdvanceGameHours(float DeltaHours, bool bPersist)
{
    if (!FMath::IsFinite(DeltaHours) || FMath::IsNearlyZero(DeltaHours))
    {
        return;
    }

    const float AbsoluteHours = WorldHour + DeltaHours;
    if (AbsoluteHours >= 24.f)
    {
        WorldDay += FMath::FloorToInt(AbsoluteHours / 24.f);
    }
    else if (AbsoluteHours < 0.f)
    {
        const int32 DaysBack = FMath::CeilToInt(-AbsoluteHours / 24.f);
        WorldDay = FMath::Max(1, WorldDay - DaysBack);
    }

    WorldHour = FMath::Fmod(FMath::Fmod(AbsoluteHours, 24.f) + 24.f, 24.f);
    PushToRuntimeAndSave(bPersist);
    BroadcastWorldStateToNPCs();
}

void UNarisWorldStateSubsystem::SetWeatherState(ENarisWeatherState NewState, bool bPersist)
{
    if (WeatherState == NewState)
    {
        return;
    }

    WeatherState = NewState;
    PushToRuntimeAndSave(bPersist);
    BroadcastWorldStateToNPCs();
}

bool UNarisWorldStateSubsystem::IsStormWeather() const
{
    switch (WeatherState)
    {
        case ENarisWeatherState::Thunderstorm:
        case ENarisWeatherState::Blizzard:
        case ENarisWeatherState::Sandstorm:
        case ENarisWeatherState::AshStorm:
        case ENarisWeatherState::VoidStorm:
            return true;
        default:
            return false;
    }
}

void UNarisWorldStateSubsystem::BroadcastWorldStateToNPCs()
{
    UWorld* World = GetWorld();
    if (!World)
    {
        return;
    }

    const bool bStorm = IsStormWeather();
    for (TActorIterator<ANarisDailyNPC> It(World); It; ++It)
    {
        ANarisDailyNPC* NPC = *It;
        if (!IsValid(NPC))
        {
            continue;
        }
        NPC->SetWorldHour(WorldHour);
        NPC->SetStormActive(bStorm);
    }
}
