#include "NarisWeatherGameplayComponent.h"

#include "Engine/GameInstance.h"
#include "Engine/World.h"
#include "NarisCombatComponent.h"
#include "NarisHeroCharacter.h"
#include "NarisWorldStateSubsystem.h"
#include "TimerManager.h"

UNarisWeatherGameplayComponent::UNarisWeatherGameplayComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
}

void UNarisWeatherGameplayComponent::BeginPlay()
{
    Super::BeginPlay();

    HeroOwner = Cast<ANarisHeroCharacter>(GetOwner());
    if (ANarisHeroCharacter* Hero = HeroOwner.Get())
    {
        Combat = Hero->Combat;
    }

    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().SetTimer(
            WeatherTimer,
            this,
            &UNarisWeatherGameplayComponent::RefreshWeatherProfile,
            UpdateIntervalSeconds,
            true
        );
    }

    RefreshWeatherProfile();
}

void UNarisWeatherGameplayComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(WeatherTimer);
    }
    Super::EndPlay(EndPlayReason);
}

void UNarisWeatherGameplayComponent::RefreshWeatherProfile()
{
    UGameInstance* GI = GetWorld() ? GetWorld()->GetGameInstance() : nullptr;
    UNarisWorldStateSubsystem* WorldState =
        GI ? GI->GetSubsystem<UNarisWorldStateSubsystem>() : nullptr;
    if (!WorldState)
    {
        return;
    }

    MoveSpeedMultiplier = 1.f;
    VisibilityMultiplier = 1.f;
    HealthDrainPerSecond = 0.f;

    switch (WorldState->GetWeatherState())
    {
        case ENarisWeatherState::HeavyRain:
            MoveSpeedMultiplier = 0.92f;
            VisibilityMultiplier = 0.82f;
            break;
        case ENarisWeatherState::Thunderstorm:
            MoveSpeedMultiplier = 0.88f;
            VisibilityMultiplier = 0.68f;
            break;
        case ENarisWeatherState::Snow:
            MoveSpeedMultiplier = 0.90f;
            VisibilityMultiplier = 0.88f;
            break;
        case ENarisWeatherState::Blizzard:
            MoveSpeedMultiplier = 0.76f;
            VisibilityMultiplier = 0.38f;
            HealthDrainPerSecond = 1.5f;
            break;
        case ENarisWeatherState::Sandstorm:
            MoveSpeedMultiplier = 0.82f;
            VisibilityMultiplier = 0.32f;
            HealthDrainPerSecond = 0.75f;
            break;
        case ENarisWeatherState::AshStorm:
            MoveSpeedMultiplier = 0.85f;
            VisibilityMultiplier = 0.42f;
            HealthDrainPerSecond = 0.5f;
            break;
        case ENarisWeatherState::VoidStorm:
            MoveSpeedMultiplier = 0.80f;
            VisibilityMultiplier = 0.28f;
            HealthDrainPerSecond = 2.0f;
            break;
        default:
            break;
    }

    if (UNarisCombatComponent* CombatComponent = Combat.Get())
    {
        if (HealthDrainPerSecond > 0.f)
        {
            CombatComponent->Health = FMath::Max(
                0.f,
                CombatComponent->Health -
                    HealthDrainPerSecond * UpdateIntervalSeconds
            );
        }
    }

    if (ANarisHeroCharacter* Hero = HeroOwner.Get())
    {
        Hero->RefreshMovementSpeed();
    }
}
